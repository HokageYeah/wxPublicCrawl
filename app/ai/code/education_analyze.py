"""
教育类文章分析模块
使用AI分析文章标题，识别与教育相关的内容
"""
import json
import re
from typing import Any, Callable, Optional
from loguru import logger
from app.schemas.wx_data import ArticleSimple
from app.ai.llm.ai_client import AIClient
from app.ai.utils.prompt_manager import get_prompt_manager


# ==================== 公共辅助函数 ====================

def _load_prompt(prompt_name: str, file_name: str, **kwargs) -> str:
    """
    加载并渲染提示词
    
    参数:
        prompt_name: 提示词名称
        file_name: 提示词文件名
        **kwargs: 渲染提示词所需的参数
        
    返回:
        str: 渲染后的提示词
    """
    prompt_manager = get_prompt_manager('app/ai/prompt')
    try:
        prompt = prompt_manager.render_prompt(prompt_name, **kwargs)
    except FileNotFoundError:
        # 如果文件不存在，尝试加载（指定完整文件名）
        prompt_manager.load_prompt(prompt_name, file_name)
        prompt = prompt_manager.render_prompt(prompt_name, **kwargs)
    return prompt


async def _call_ai_assistant_with_tools(
    prompt: str,
    enable_tools: bool = True,
    temperature: float = 0.1,
    system_message: str = "你是一个专业的AI助手。"
) -> str:
    """
    调用AI助手并清理响应文本
    
    参数:
        prompt: 提示词
        enable_tools: 是否启用工具
        temperature: 温度参数
        system_message: 系统消息
        
    返回:
        str: 清理后的响应文本
    """
    from app.services.ai_assistant import query_ai_assistant
    
    # 调用AI助手
    result = await query_ai_assistant(
        query=prompt,
        enable_tools=enable_tools,
        temperature=temperature,
        system_message=system_message
    )
    
    # 检查调用是否成功
    if not result.get("success"):
        error_msg = result.get("error", "未知错误")
        logger.error(f"AI调用失败: {error_msg}")
        raise Exception(f"AI调用失败: {error_msg}")
    
    # 提取并清理响应文本
    response_text = result.get("response", "").strip()
    logger.debug(f"AI原始响应: {response_text[:500]}...")
    
    # 清理响应文本 - 移除markdown代码块标记
    response_text = _clean_markdown_from_response(response_text)
    response_text = response_text.strip()
    
    logger.debug(f"清理后的响应: {response_text[:300]}...")
    return response_text


def _clean_markdown_from_response(response_text: str) -> str:
    """
    从响应文本中清理Markdown代码块标记
    
    参数:
        response_text: 原始响应文本
        
    返回:
        str: 清理后的文本
    """
    if not response_text.startswith("```"):
        return response_text
    
    lines = response_text.split('\n')
    # 移除第一行(```json 或 ```)和最后一行(```)
    if len(lines) > 2:
        return '\n'.join(lines[1:-1])
    else:
        return response_text.replace("```json", "").replace("```", "")


def _parse_json_response(
    response_text: str,
    log_prefix: str = "JSON",
    fallback_pattern: Optional[str] = None
) -> Any:
    """
    解析JSON响应，包含错误处理和降级方案
    
    参数:
        response_text: 响应文本
        log_prefix: 日志前缀
        fallback_pattern: 降级方案的正则表达式模式（可选）
        
    返回:
        Any: 解析后的数据，失败时返回None
    """
    try:
        # 第一次尝试直接解析
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        logger.error(f"{log_prefix}解析失败 - 位置: {e.pos}, 行: {e.lineno}, 列: {e.colno}")
        logger.error(f"错误信息: {e.msg}")
        
        # 显示出错位置附近的文本
        start = max(0, e.pos - 80)
        end = min(len(response_text), e.pos + 80)
        error_context = response_text[start:end]
        logger.error(f"错误位置附近: ...{error_context}...")
        
        # 尝试修复常见问题
        try:
            # 移除 BOM 标记
            response_text_fixed = response_text.encode().decode('utf-8-sig')
            return json.loads(response_text_fixed)
        except Exception as fix_error:
            logger.error(f"修复尝试失败: {fix_error}")
            
            # 最后的降级方案：尝试正则提取
            if fallback_pattern:
                try:
                    matches = re.findall(fallback_pattern, response_text)
                    if matches:
                        logger.warning(f"使用正则表达式降级方案，提取到 {len(matches)} 个结果")
                        return matches
                except Exception as regex_error:
                    logger.error(f"正则提取也失败: {regex_error}")
            
            return None


def _validate_and_extract_string_list(
    data: Any,
    log_prefix: str = "数据"
) -> list[str]:
    """
    验证并提取字符串列表
    
    参数:
        data: 待验证的数据
        log_prefix: 日志前缀
        
    返回:
        list[str]: 有效的字符串列表
    """
    if not isinstance(data, list):
        logger.warning(f"{log_prefix}格式错误(非列表): {type(data)}")
        return []
    
    # 验证并过滤有效的字符串
    valid_items = []
    for item in data:
        if isinstance(item, str) and item.strip():
            valid_items.append(item.strip())
        else:
            logger.warning(f"跳过无效的项: {item} (类型: {type(item)})")
    
    return valid_items


def _validate_and_extract_dict_list(
    data: Any,
    log_prefix: str = "数据",
    required_fields: Optional[list[str]] = None,
    validator: Optional[Callable[[dict], bool]] = None
) -> list[dict]:
    """
    验证并提取字典列表
    
    参数:
        data: 待验证的数据
        log_prefix: 日志前缀
        required_fields: 必需字段列表（可选）
        validator: 自定义验证函数（可选）
        
    返回:
        list[dict]: 有效的字典列表
    """
    if not isinstance(data, list):
        logger.warning(f"{log_prefix}格式错误(非列表): {type(data)}")
        return []
    
    # 验证并过滤有效的字典
    valid_items = []
    for item in data:
        if not isinstance(item, dict):
            logger.warning(f"跳过非字典类型的项目: {item} (类型: {type(item)})")
            continue
        
        # 检查必需字段
        if required_fields:
            if all(item.get(field) for field in required_fields):
                valid_items.append(item)
            else:
                logger.warning(f"跳过缺少必需字段的项目: {item}")
        # 使用自定义验证函数
        elif validator and validator(item):
            valid_items.append(item)
        # 如果没有验证要求，直接添加
        else:
            valid_items.append(item)
    
    return valid_items


# ==================== 主要业务函数 ====================

async def analyze_education_articles(articles: list[ArticleSimple]) -> list[str]:
    """
    使用AI分析文章以识别与教育相关的内容
    
    参数:
        articles: 包含文章ID(aid)和标题(title)的文章列表
        
    返回:
        list[str]: 与教育相关的文章ID(aid)列表
    """
    if not articles:
        logger.info("文章列表为空，无需分析")
        return []

    try:
        # 1. 准备文章数据
        articles_data = [{"id": a.aid, "title": a.title} for a in articles]
        articles_json = json.dumps(articles_data, ensure_ascii=False, indent=2)
        logger.info(f"开始分析 {len(articles)} 篇文章")
        
        # 2. 加载提示词
        prompt = _load_prompt(
            "education_prompt",
            "education_prompt.txt",
            articles_json=articles_json
        )
        
        # 3. 创建AI客户端并调用
        ai_client = AIClient(
            temperature=0.1,  # 低温度以获得一致的结果
            use_db_config=True
        )
        
        # 使用chat_with_json_response方法，自动处理JSON解析和清理
        result_aids = await ai_client.chat_with_json_response(
            user_message=prompt,
            system_message="You are a helpful assistant for classifying articles."
        )
        
        # 4. 验证返回结果
        if isinstance(result_aids, list):
            logger.info(f"AI分析成功，找到 {len(result_aids)} 篇教育相关文章")
            return result_aids
        else:
            logger.warning(f"AI返回的结果不是列表格式: {type(result_aids)}")
            return []
            
    except FileNotFoundError as e:
        logger.error(f"提示词文件未找到: {e}")
        return []
    except ValueError as e:
        logger.error(f"JSON解析失败: {e}")
        return []
    except Exception as e:
        logger.error(f"AI分析失败: {e}")
        # 如果失败，返回空列表而不是崩溃
        return []


async def analyze_education_articles_by_id(wx_public_id: str) -> list[str]:
    """
    使用AI通过公众号ID获取并分析教育相关文章
    
    参数:
        wx_public_id: 公众号ID
        
    返回:
        list[str]: 与教育相关的文章ID(aid)列表
    """
    try:
        logger.info(f"开始通过ID分析公众号文章: {wx_public_id}")
        
        # 1. 加载提示词
        prompt = _load_prompt(
            "education_prompt_by_id",
            "education_prompt_by_id.txt",
            wx_public_id=wx_public_id
        )
            
        # 2. 调用AI助手 (启用工具)
        response_text = await _call_ai_assistant_with_tools(
            prompt=prompt,
            enable_tools=True,
            temperature=0.1,
            system_message="你是一个专业的文章分析助手，擅长使用工具获取数据并进行分类分析。请只返回纯JSON字符串数组格式，不要包含任何其他文本、说明或markdown标记。示例：[\"2247484875_1\", \"2247484870_1\"]"
        )
        
        # 3. 解析 JSON 数组（使用aid格式作为降级方案）
        aid_list = _parse_json_response(
            response_text,
            log_prefix="文章ID数组",
            fallback_pattern=r'"(\d+_\d+)"'
        )
        
        if aid_list is None:
            logger.error("JSON解析失败")
            return []
        
        # 4. 验证并提取有效的 aid
        valid_aids = _validate_and_extract_string_list(aid_list, log_prefix="文章ID")
        
        logger.info(f"分析成功，找到 {len(valid_aids)} 篇教育相关文章")
        return valid_aids
            
    except Exception as e:
        logger.error(f"分析过程发生错误: {e}", exc_info=True)
        return []


async def get_all_articles_info_by_id(wx_public_id: str) -> list[dict]:
    """
    使用AI通过公众号ID获取所有文章的标题、发布时间、链接
    
    参数:
        wx_public_id: 公众号ID
        
    返回:
        list[dict]: 文章信息列表，每个元素包含 title、publish_time、link
    """
    try:
        logger.info(f"开始通过ID获取公众号文章信息: {wx_public_id}")
        
        # 1. 加载提示词
        prompt = _load_prompt(
            "get_all_articles_prompt_by_id",
            "get_all_articles_prompt_by_id.txt",
            wx_public_id=wx_public_id
        )
            
        # 2. 调用AI助手 (启用工具)
        response_text = await _call_ai_assistant_with_tools(
            prompt=prompt,
            enable_tools=True,
            temperature=0.1,
            system_message="你是一个专业的文章信息获取助手，擅长使用工具获取数据并整理信息。请只返回纯JSON字符串数组格式，不要包含任何其他文本、说明或markdown标记。"
        )
        
        # 3. 解析 JSON 数组
        articles_info = _parse_json_response(response_text, log_prefix="文章信息数组")
        
        if articles_info is None:
            logger.error("JSON解析失败")
            return []
        
        # 4. 定义验证函数
        def validate_article_info(article: dict) -> bool:
            """验证文章信息是否有效"""
            title = article.get("title", "")
            link = article.get("link", "")
            return bool(title and link)
        
        # 5. 验证并提取有效的文章信息
        valid_articles = _validate_and_extract_dict_list(
            articles_info,
            log_prefix="文章信息",
            validator=validate_article_info
        )
        
        # 6. 格式化输出
        result = [
            {
                "title": article.get("title", ""),
                "publish_time": article.get("publish_time", ""),
                "link": article.get("link", "")
            }
            for article in valid_articles
        ]
        
        logger.info(f"获取成功，共 {len(result)} 篇文章")
        return result
            
    except Exception as e:
        logger.error(f"获取文章信息过程发生错误: {e}", exc_info=True)
        return []
