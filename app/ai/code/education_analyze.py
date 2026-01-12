"""
教育类文章分析模块
使用AI分析文章标题，识别与教育相关的内容
"""
import json
from loguru import logger
from app.schemas.wx_data import ArticleSimple
from app.ai.llm.ai_client import AIClient
from app.ai.utils.prompt_manager import get_prompt_manager


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
        
        # 2. 获取提示词管理器并加载提示词
        prompt_manager = get_prompt_manager('app/ai/prompt')
        try:
            prompt = prompt_manager.render_prompt(
                "education_prompt",
                articles_json=articles_json
            )
        except FileNotFoundError:
            # 如果文件不存在，尝试加载（指定完整文件名）
            prompt_manager.load_prompt("education_prompt", "education_prompt.txt")
            prompt = prompt_manager.render_prompt(
                "education_prompt",
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
    from app.services.ai_assistant import query_ai_assistant
    
    try:
        logger.info(f"开始通过ID分析公众号文章: {wx_public_id}")
        
        # 1. 获取提示词管理器并加载提示词
        prompt_manager = get_prompt_manager('app/ai/prompt')
        try:
            prompt = prompt_manager.render_prompt(
                "education_prompt_by_id",
                wx_public_id=wx_public_id
            )
        except FileNotFoundError:
            prompt_manager.load_prompt("education_prompt_by_id", "education_prompt_by_id.txt")
            prompt = prompt_manager.render_prompt(
                "education_prompt_by_id",
                wx_public_id=wx_public_id
            )
            
        # 2. 调用AI助手 (启用工具)
        result = await query_ai_assistant(
            query=prompt,
            enable_tools=True,
            temperature=0.1,
            system_message="你是一个专业的文章分析助手，擅长使用工具获取数据并进行分类分析。请只返回纯JSON字符串数组格式，不要包含任何其他文本、说明或markdown标记。示例：[\"2247484875_1\", \"2247484870_1\"]"
        )
        
        if not result.get("success"):
            logger.error(f"AI调用失败: {result.get('error')}")
            return []
            
        response_text = result.get("response", "").strip()
        logger.debug(f"AI原始响应: {response_text[:500]}...")
        
        # 3. 清理响应文本 - 移除markdown代码块标记
        if response_text.startswith("```"):
            lines = response_text.split('\n')
            # 移除第一行(```json 或 ```)和最后一行(```)
            if len(lines) > 2:
                response_text = '\n'.join(lines[1:-1])
            else:
                response_text = response_text.replace("```json", "").replace("```", "")
        
        response_text = response_text.strip()
        logger.debug(f"清理后的响应: {response_text[:300]}...")
        
        # 4. 解析 JSON 数组
        try:
            aid_list = json.loads(response_text)
            
            # 验证返回类型
            if not isinstance(aid_list, list):
                logger.warning(f"AI返回格式错误(非列表): {type(aid_list)}")
                return []
            
            # 验证并过滤有效的 aid
            valid_aids = []
            for aid in aid_list:
                if isinstance(aid, str) and aid.strip():
                    valid_aids.append(aid.strip())
                else:
                    logger.warning(f"跳过无效的aid: {aid} (类型: {type(aid)})")
            
            logger.info(f"分析成功，找到 {len(valid_aids)} 篇教育相关文章")
            return valid_aids
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败 - 位置: {e.pos}, 行: {e.lineno}, 列: {e.colno}")
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
                
                # 尝试再次解析
                aid_list = json.loads(response_text_fixed)
                
                if isinstance(aid_list, list):
                    valid_aids = [aid.strip() for aid in aid_list if isinstance(aid, str) and aid.strip()]
                    logger.info(f"修复后解析成功，找到 {len(valid_aids)} 篇文章")
                    return valid_aids
                else:
                    logger.error(f"修复后仍非列表格式: {type(aid_list)}")
                    return []
                    
            except Exception as fix_error:
                logger.error(f"修复尝试失败: {fix_error}")
                
                # 最后的降级方案：尝试正则提取
                import re
                try:
                    # 尝试用正则表达式提取所有符合格式的 aid
                    aid_pattern = r'"(\d+_\d+)"'
                    matches = re.findall(aid_pattern, response_text)
                    if matches:
                        logger.warning(f"使用正则表达式降级方案，提取到 {len(matches)} 个aid")
                        return matches
                except Exception as regex_error:
                    logger.error(f"正则提取也失败: {regex_error}")
                
                return []
            
    except Exception as e:
        logger.error(f"分析过程发生错误: {e}", exc_info=True)
        return []