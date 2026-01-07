import fastmcp
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, Optional, List
import httpx
import json
from loguru import logger

# 创建路由
router = APIRouter()

# 定义请求模型
class QueryRequest(BaseModel):
    """查询请求模型"""
    query: str

# 知识库数据
KNOWLEDGE_BASE = {
    "python": "Python是一种高级编程语言，以简洁、易读的语法著称。",
    "fastapi": "FastAPI是一个现代、快速的Web框架，用于构建API。",
    "mcp": "MCP(Model-Control-Protocol)是一个用于AI模型交互的协议。",
    "天气": "天气是指某个地区在某一时间段内的大气状况，包括温度、湿度、风向等。"
}

# 天气数据
WEATHER_DATA = {
    "北京": "晴朗，气温25°C",
    "上海": "多云，气温28°C",
    "广州": "小雨，气温30°C",
    "深圳": "阵雨，气温29°C"
}

# 创建MCP服务端
class FastmcpServer:
    def __init__(self):
        """初始化FastMCP服务端"""
        self.server = fastmcp.FastMCP(name="fastmcp_demo_server")
        # 注册工具和资源
        self._register_functions()
    
    def _register_functions(self):
        """注册工具和资源"""
        # 注册天气查询工具
        @self.server.tool("weather")
        def weather(location: str) -> str:
            """全国各地天气查询工具，输入城市名称，返回该城市天气信息。
            
            可以查询的城市包括：北京、上海、广州、深圳等主要城市。
            查询结果包含天气状况和气温信息。
            
            参数:
                location (str): 需要查询天气的城市名称，例如"北京"、"上海"
            
            返回:
                str: 包含城市名和天气信息的字符串
            """
            logger.info(f"[MCP工具] 天气查询: {location}")
            
            # 简化处理
            if "北京" in location:
                return f"北京天气: 晴朗，气温25°C"
            elif "上海" in location:
                return f"上海天气: 多云，气温28°C"
            elif "广州" in location:
                return f"广州天气: 小雨，气温30°C"
            elif "深圳" in location:
                return f"深圳天气: 阵雨，气温29°C"
            elif "罗山" in location:
                return f"罗山天气: 多云，气温-20°C，空气质量优"
            else:
                return f"抱歉，没有找到{location}的天气信息"
        
        # 注册计算器工具
        @self.server.tool("calculator")
        def calculator(expression: str) -> str:
            """简单计算器工具，可以执行基本的数学运算。
            
            支持加法(+)、减法(-)、乘法(*)、除法(/)等基本运算。
            也支持小数点和括号运算。
            
            参数:
                expression (str): 数学表达式，例如"1+2"、"3*4"、"10/2"
                
            返回:
                str: 计算结果的字符串表示
                
            示例:
                - "1+2" 返回 "计算结果: 3"
                - "10-5" 返回 "计算结果: 5"
                - "3*4" 返回 "计算结果: 12"
            """
            logger.info(f"[MCP工具] 计算器: {expression}")
            try:
                # 安全地计算表达式
                result = eval(expression, {"__builtins__": {}}, {"abs": abs, "round": round})
                return f"计算结果: {result}"
            except Exception as e:
                return f"计算错误: {str(e)}"
        
        # 注册知识库资源
        @self.server.resource("knowledge_base/{topic}")
        def knowledge_base(topic: str) -> str:
            """知识库资源"""
            # 首先检查topic参数
            if topic in KNOWLEDGE_BASE:
                return KNOWLEDGE_BASE[topic]
                
            # 如果topic不匹配，则返回默认信息
            return f"抱歉，我没有关于'{topic}'的信息。"
        
        # 注册公众号文章获取工具
        @self.server.tool("get_wx_articles")
        def get_wx_articles(wx_public_id: str) -> str:
            """获取微信公众号所有文章列表工具。
            
            根据公众号ID自动翻页获取该公众号的所有文章，并返回完整的文章列表。
            此工具会自动从系统加载用户认证信息，无需手动设置。
            
            参数:
                wx_public_id (str): 微信公众号ID（fakeid）
            
            返回:
                str: JSON格式的文章列表字符串，包含所有文章信息
            
            示例:
                - 输入公众号ID，返回该公众号所有已发布的文章列表
            
            注意:
                - 工具会自动加载已保存的用户会话信息
                - 返回的数据包含文章标题、发布时间、链接等详细信息
            """
            logger.info(f"[MCP工具] 开始获取公众号文章: wx_public_id={wx_public_id}")
            
            # 配置参数
            session_url = "http://localhost:8002/api/v1/wx/public/system/session/load"
            article_list_url = "http://localhost:8002/api/v1/wx/public/get-wx-article-list"
            begin = 0
            count = 20  # 每页获取20篇文章
            all_articles = []
            
            try:
                # 第一步：加载用户会话信息
                logger.info("[MCP工具] 正在加载用户会话信息...")
                # 1. 发起 HTTP GET 请求
                session_response = httpx.get(session_url, timeout=10.0)
                # 2. 检查 HTTP 状态码，如果是 4xx 或 5xx 则抛出异常
                session_response.raise_for_status()
                # 3. 将响应体解析为 JSON
                session_result = session_response.json().get("data", {})
                
                # 检查是否成功获取会话
                if not session_result.get("logged_in", False):
                    error_msg = "用户未登录，请先登录微信公众号平台"
                    logger.warning(f"[MCP工具] ✗ {error_msg}")
                    return json.dumps({
                        "success": False,
                        "error": error_msg,
                        "articles": []
                    }, ensure_ascii=False)
                
                # 提取 cookies 和 token
                cookies = session_result.get("cookies", {})
                token = session_result.get("token", "")
                logger.info(f"🔧mcp工具调用cookies: {cookies}， 类型: {type(cookies)}")
                logger.info(f"🔧mcp工具调用token: {token}， 类型: {type(token)}")
                if not cookies or not token:
                    error_msg = "会话信息不完整，缺少认证数据"
                    logger.warning(f"[MCP工具] ✗ {error_msg}")
                    return json.dumps({
                        "success": False,
                        "error": error_msg,
                        "articles": []
                    }, ensure_ascii=False)
                
                logger.info(f"[MCP工具] ✓ 会话加载成功，准备获取文章列表")
                # 将 cookies 对象转换为 Cookie 字符串使用;分割
                cookie_str = ";".join([f"{key}={value}" for key, value in cookies.items()])
                logger.info(f"[MCP工具] 转换后的cookie_str: {cookie_str}")
                # 准备请求头
                headers = {
                    "X-WX-Cookies": cookie_str,
                    "X-WX-Token": token
                }
                # return headers
                
                # 第二步：循环获取所有文章
                while True:
                    logger.info(f"[MCP工具] 正在获取第 {begin // count + 1} 页，当前已获取 {len(all_articles)} 篇文章...")
                    
                    # 构造请求参数
                    payload = {
                        "wx_public_id": wx_public_id,
                        "begin": begin,
                        "count": count,
                        "query": ""
                    }
                    logger.info(f"[MCP工具] 调用公众号文章接口请求payload: {payload}")
                    # 发送请求，添加认证请求头
                    response = httpx.post(article_list_url, json=payload, headers=headers, timeout=30.0)
                    response.raise_for_status()
                    # 解析响应
                    result = response.json()
                    # ret = ["SUCCESS::请求成功"], 成功
                    # ret = ["ERROR::请求失败"], 失败
                    ret = result.get("ret", [])
                    ret_code = ret[0].split("::")[0] if ret else ""
                    ret_msg = ret[0].split("::")[1] if ret else ""

                    logger.info(f"[MCP工具] 调用公众号文章接口返回result: {result}")
                    logger.info(f"[MCP工具] 调用公众号文章接口返回ret_code: {ret_code}")
                    logger.info(f"[MCP工具] 调用公众号文章接口返回ret_msg: {ret_msg}")
                    # 检查返回状态
                    if ret_code != "SUCCESS":
                        error_msg = ret_msg
                        logger.error(f"[MCP工具] 接口返回错误: {error_msg}")
                        return json.dumps({
                            "success": False,  
                            "error": f"获取文章失败: {error_msg}",
                            "articles": all_articles
                        }, ensure_ascii=False)
                    # 获取文章列表
                    data = result.get("data", {})
                    publish_list = data.get("publish_list", [])
                    
                    # 如果没有更多文章，结束循环
                    if not publish_list or len(publish_list) == 0:
                        logger.info(f"[MCP工具] 没有更多文章，共获取 {len(all_articles)} 篇")
                        break
                    
                    # 将文章添加到列表
                    all_articles.extend(publish_list)
                    
                    # 如果返回的文章数少于请求数，说明已经是最后一页
                    if len(publish_list) < count:
                        logger.info(f"[MCP工具] 已获取所有文章，总计 {len(all_articles)} 篇")
                        break
                    
                    # 更新起始位置，继续下一页
                    begin += count
                
                # 返回结果
                logger.info(f"[MCP工具] ✓ 成功获取公众号 {wx_public_id} 的所有文章，共 {len(all_articles)} 篇")
                return json.dumps({
                    "success": True,
                    "wx_public_id": wx_public_id,
                    "total_count": len(all_articles),
                    "articles": all_articles
                }, ensure_ascii=False)
                
            except httpx.HTTPError as e:
                error_msg = f"网络请求失败: {str(e)}"
                logger.error(f"[MCP工具] ✗ {error_msg}")
                return json.dumps({
                    "success": False,
                    "error": error_msg,
                    "articles": all_articles
                }, ensure_ascii=False)
            except Exception as e:
                error_msg = f"获取文章时发生错误: {str(e)}"
                logger.error(f"[MCP工具] ✗ {error_msg}")
                return json.dumps({
                    "success": False,
                    "error": error_msg,
                    "articles": all_articles
                }, ensure_ascii=False)
    
    # def process_query(self, query: str) -> str:
    #     """处理用户查询"""
    #     # 检查是否是天气查询
    #     if "天气" in query:
    #         location = query.replace("天气", "").replace("如何", "").replace("怎么样", "").strip()
    #         if location:
    #             # 直接使用天气数据
    #             for city, weather_info in WEATHER_DATA.items():
    #                 if city in location:
    #                     return f"{location}天气: {weather_info}"
    #             return f"抱歉，没有找到{location}的天气信息"
    #         else:
    #             return "请指定您想查询哪个地区的天气。"
        
    #     # 检查是否是计算问题
    #     if any(op in query for op in ["+", "-", "*", "/"]):
    #         # 提取表达式
    #         expression = query
    #         for op in ["计算", "等于", "是多少", "结果"]:
    #             expression = expression.replace(op, "")
    #         expression = expression.strip()
            
    #         try:
    #             # 安全地计算表达式
    #             result = eval(expression, {"__builtins__": {}}, {"abs": abs, "round": round})
    #             return f"计算结果: {result}"
    #         except Exception as e:
    #             return f"计算错误: {str(e)}"
        
    #     # 检查是否是知识库查询
    #     if "什么是" in query or "告诉我关于" in query or "介绍" in query:
    #         topic = query.lower()
    #         for key in ["什么是", "告诉我关于", "介绍"]:
    #             if key in topic:
    #                 topic = topic.replace(key, "").strip()
            
    #         # 直接查询知识库
    #         for key, value in KNOWLEDGE_BASE.items():
    #             if key in topic:
    #                 return value
            
    #         return f"抱歉，我没有关于'{topic}'的信息。"
        
    #     # 默认回复
    #     return f"您的问题是: {query}。这是一个基于AI助手的回答。"
    
    def get_server(self):
        """获取服务端实例"""
        return self.server
    
    def run(self, transport="streamable-http", host="localhost", port=8008):
        """运行服务器"""
        self.server.run(transport=transport, host=host, port=port)

# 创建服务端实例
fastmcp_server = FastmcpServer()


if __name__ == "__main__":
    import sys
    from pathlib import Path
    
    # 添加项目根目录到Python路径
    project_root = Path(__file__).resolve().parent.parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    logger.info("="*60)
    logger.info("启动FastMCP服务器")
    logger.info("="*60)
    logger.info(f"项目根目录: {project_root}")
    logger.info(f"服务器地址: http://localhost:8008/mcp")
    logger.info(f"可用工具: weather, calculator, knowledge_base, get_wx_articles")
    logger.info("="*60)
    
    try:
        server = FastmcpServer()
        server.run(transport="streamable-http", host="localhost", port=8008)
    except KeyboardInterrupt:
        logger.info("\n服务器已停止")
    except Exception as e:
        logger.error(f"服务器启动失败: {e}", exc_info=True)
        sys.exit(1)