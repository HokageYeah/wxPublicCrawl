# 创建一个请求装饰器，用于从请求头中提取并解析cookies和token
from fastapi import Request
import functools
from typing import Dict, Callable


def extract_wx_credentials(
    global_cookies: Dict[str, str], 
    global_token: str,
    cookie_header_name: str = 'X-WX-Cookies',
    token_header_name: str = 'X-WX-Token',
    state_cookie_key: str = 'wx_cookies',
    state_token_key: str = 'wx_token'
):
    """
    装饰器工厂：从请求头中提取平台的cookies和token，并合并到全局配置中
    
    Args:
        global_cookies: 全局cookies字典
        global_token: 全局token字符串
        cookie_header_name: Cookie请求头名称（默认：X-WX-Cookies）
        token_header_name: Token请求头名称（默认：X-WX-Token）
        state_cookie_key: 存储到 request.state 的 cookie 键名（默认：wx_cookies）
        state_token_key: 存储到 request.state 的 token 键名（默认：wx_token）
    
    Returns:
        装饰器函数
    
    使用示例:
        ```python
        from app.decorators.request_decorator import extract_wx_credentials
        from fastapi import Request
        
        # 微信接口示例（使用默认参数，向后兼容）
        cookies = {"mm_lang": "zh_CN"}
        token = "159333899"
        
        @extract_wx_credentials(cookies, token)
        async def fetch_wx_public(request: Request, query: str):
            merged_cookies = request.state.wx_cookies
            final_token = request.state.wx_token
            # ...业务逻辑
        
        # 喜马拉雅接口示例（自定义请求头）
        @extract_wx_credentials(
            {}, '', 
            cookie_header_name='X-XMLY-Cookies',
            token_header_name='X-XMLY-Token',
            state_cookie_key='xmly_cookies',
            state_token_key='xmly_token'
        )
        async def subscribe_album(request: Request, album_id: str):
            merged_cookies = request.state.xmly_cookies
            final_token = request.state.xmly_token
            # ...业务逻辑
        ```
    
    注意事项:
        1. 被装饰的函数必须包含 Request 参数
        2. 装饰器会自动从请求头中提取指定名称的 Cookies 和 Token
        3. 提取的 cookies 会与全局 cookies 合并（请求中的优先级更高）
        4. 处理后的结果存储在 request.state 中
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # 从参数中获取 Request 对象
            request = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            
            if not request:
                # 如果没有找到 Request 对象，尝试从 kwargs 中查找
                request = kwargs.get('request')
            
            if request:
                # ⚠️ 重要：浏览器不允许 JavaScript 手动设置 Cookie 请求头
                # 因此前端会通过自定义请求头传递 Cookie 信息
                # 优先从自定义请求头获取，如果没有则从标准 Cookie 请求头获取
                request_cookies = request.headers.get(cookie_header_name, '') or request.headers.get('Cookie', '')
                
                # 从自定义请求头获取 token
                request_token = request.headers.get(token_header_name, '')
                
                print('=' * 80)
                # 给出请求地址
                print(f'🔍 [DEBUG] extract_credentials - 请求地址: {request.url}')
                print(f'🔍 [DEBUG] extract_credentials - 自定义请求头 {cookie_header_name}:', request.headers.get(cookie_header_name, ''))
                print(f'🔍 [DEBUG] extract_credentials - 标准请求头 Cookie:', request.headers.get('Cookie', ''))
                print(f'🔍 [DEBUG] extract_credentials - 最终使用的 Cookie:', request_cookies)
                print(f'🔍 [DEBUG] extract_credentials - 自定义请求头 {token_header_name}:', request_token)
                
                # 解析 Cookie 字符串为字典
                parsed_cookies = {}
                if request_cookies:
                    for cookie in request_cookies.split(';'):
                        cookie = cookie.strip()
                        if '=' in cookie:
                            key, value = cookie.split('=', 1)
                            parsed_cookies[key] = value
                    print('🔍 [DEBUG] 解析后的 cookies 字典:', parsed_cookies)
                
                # 合并全局 cookies 和请求中的 cookies（请求中的优先级更高）
                merged_cookies = {**global_cookies, **parsed_cookies}
                
                # 优先使用请求头中的 token，如果没有则使用全局 token
                final_token = request_token if request_token else global_token
                
                print('🔍 [DEBUG] 全局 cookies:', global_cookies)
                print('🔍 [DEBUG] 合并后的 cookies:', merged_cookies)
                print('🔍 [DEBUG] 全局 token:', global_token)
                print('🔍 [DEBUG] 请求中的 token:', request_token)
                print('🔍 [DEBUG] 最终使用的 token:', final_token)
                print('=' * 80)
                
                # 将处理后的 cookies 和 token 存储到 request.state 中
                setattr(request.state, state_cookie_key, merged_cookies)
                setattr(request.state, state_token_key, final_token)
            
            # 调用原始函数
            return await func(*args, **kwargs)
        
        return wrapper
    return decorator