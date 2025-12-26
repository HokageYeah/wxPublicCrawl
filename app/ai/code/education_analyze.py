"""
教育类文章分析模块
使用AI分析文章标题，识别与教育相关的内容
"""
import json
from loguru import logger
from app.schemas.wx_data import ArticleSimple
from app.ai.code.ai_client import AIClient
from app.ai.code.prompt_manager import get_prompt_manager


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
            temperature=0.1  # 低温度以获得一致的结果
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
