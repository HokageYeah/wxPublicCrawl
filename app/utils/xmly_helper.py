"""
喜马拉雅工具函数 - 处理响应和风险验证逻辑
"""
from typing import Dict, Any
from fastapi import HTTPException
from httpx import AsyncClient
from loguru import logger


async def handle_xmly_risk_verification(
    client: AsyncClient,
    url: str,
    headers: Dict[str, str],
    merged_cookies: Dict[str, str],
    params: Dict[str, str],
    keyword: str,
    slider_solver,
    sign_generator,
    json_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    处理喜马拉雅响应和风险验证逻辑

    Args:
        client: httpx 异步客户端
        url: 请求URL
        headers: 请求头字典（会被修改）
        merged_cookies: 合并后的cookies
        params: 请求参数
        keyword: 搜索关键词
        slider_solver: 滑块验证器实例
        sign_generator: 签名生成器实例
        json_data: 请求返回的JSON数据

    Returns:
        Dict[str, Any]: 处理后的JSON响应数据

    Raises:
        HTTPException: 请求失败或验证失败时抛出

    使用示例:
        ```python
        from app.utils.xmly_helper import handle_xmly_risk_verification

        # 发送请求
        response = await client.get(url, headers=headers, cookies=merged_cookies, params=params)
        json_data = response.json()

        # 处理响应（包括风险验证）
        json_data = await handle_xmly_risk_verification(
            client, url, headers, merged_cookies, params,
            keyword, slider_solver, sign_generator, json_data
        )

        # 继续处理返回的数据
        data = json_data.get('data', {})
        ```
    """
    # 检查返回码
    if json_data.get('ret') != 200:
        error_msg = json_data.get('msg', '未知错误')
        logger.error(f"请求失败: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)

    # 检查是否需要风险验证
    reason = json_data.get("data", {}).get("reason")
    if reason == "risk invalid":
        return await _perform_slider_verification(
            client, url, headers, merged_cookies, params,
            keyword, slider_solver, sign_generator
        )

    # 正常返回，无需验证
    return json_data


async def _perform_slider_verification(
    client: AsyncClient,
    url: str,
    headers: Dict[str, str],
    merged_cookies: Dict[str, str],
    params: Dict[str, str],
    keyword: str,
    slider_solver,
    sign_generator
) -> Dict[str, Any]:
    """
    执行滑块验证和重试逻辑

    Args:
        client: httpx 异步客户端
        url: 请求URL
        headers: 请求头字典（会被修改）
        merged_cookies: 合并后的cookies
        params: 请求参数
        keyword: 搜索关键词
        slider_solver: 滑块验证器实例
        sign_generator: 签名生成器实例

    Returns:
        Dict[str, Any]: 验证后的JSON响应数据

    Raises:
        HTTPException: 验证失败时抛出
    """
    from urllib.parse import quote

    logger.warning("⚠️ 需要滑块验证,尝试重新获取Cookie")

    # 检查滑块验证器是否可用
    if not slider_solver:
        logger.error("❌ 滑块验证器未初始化，无法处理")
        raise HTTPException(status_code=400, detail="滑块验证器未初始化")

    # 检查签名生成器是否可用
    if not sign_generator:
        logger.error("❌ 签名生成器未初始化，无法处理滑块验证")
        raise HTTPException(status_code=400, detail="签名生成器未初始化")

    # 生成xm-sign
    success, xm_sign, error_msg = sign_generator.get_xm_sign()

    if not success:
        logger.error(f"❌ xm-sign 生成失败: {error_msg}")
        raise HTTPException(status_code=400, detail=error_msg)

    # 重新获取cookie并重试一次
    try:
        # 重新生成 encoded_kw
        encoded_kw = quote(keyword)
        verify_url = f"https://www.ximalaya.com/so/{encoded_kw}"
        cookies_dict = await slider_solver.solve_slider(verify_url)
        logger.info(f"滑块验证响应: {cookies_dict}")
        cookie = slider_solver.get_cookies_string(cookies_dict)
        logger.info(f"滑块验证cookie: {cookie}")
        headers["Cookie"] = cookie
        headers["xm-sign"] = xm_sign
        logger.info(f"滑块验证sign: {xm_sign}")

        resp = await client.get(url, headers=headers, cookies=merged_cookies, params=params)
        resp.raise_for_status()
        json_data = resp.json()
        logger.info(f"重试响应: {json_data}")
        logger.info(f"重试响应: ret={json_data.get('ret')}")

        # 再次检查返回码
        if json_data.get('ret') != 200:
            error_msg = json_data.get('msg', '未知错误')
            logger.error(f"重试后仍然失败: {error_msg}")
            raise HTTPException(status_code=400, detail=error_msg)

        return json_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 重新验证失败: {e}")
        raise HTTPException(status_code=500, detail="滑块验证失败")

