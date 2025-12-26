import json
import os
from pathlib import Path
from jinja2 import Template
from openai import AsyncOpenAI
from loguru import logger
from app.schemas.wx_data import ArticleSimple
from app.core.config import settings
from app.utils.src_path import get_resource_path

import sys

# Locate the prompt file relative to this script
# 优先使用 sys._MEIPASS (PyInstaller 打包后的临时目录)
PROMPT_FILE=Path(get_resource_path('app/ai/prompt/education_prompt.txt'))

async def analyze_education_articles(articles: list[ArticleSimple]) -> list[str]:
    """
    使用 OpenAI 分析文章以识别与教育相关的内容。
    
    参数:
        articles: 包含文章ID(aid)和标题(title)的文章列表。
        
    返回:
        list[str]: 与教育相关的文章ID(aid)列表。
    """
    if not articles:
        return []

    try:
        # 1. 准备提示词数据
        articles_data = [{"id": a.aid, "title": a.title} for a in articles]
        articles_json = json.dumps(articles_data, ensure_ascii=False, indent=2)
        print('[DEBUG] PROMPT_FILE:', PROMPT_FILE)
        print('[DEBUG] PROMPT_FILE.exists():', PROMPT_FILE.exists())
        print('[DEBUG] PROMPT_FILE Type:', type(PROMPT_FILE))
        # 2. 读取提示词模板
        if not PROMPT_FILE.exists():
            logger.error(f"Prompt file not found: {PROMPT_FILE}")
            return []
        
        with open(PROMPT_FILE, "r", encoding="utf-8") as f:
            prompt_content = f.read()

        # 3. 渲染提示词
        template = Template(prompt_content)
        prompt = template.render(articles_json=articles_json)
        
        # 4. 调用 OpenAI API
        # 使用 settings 中的配置
        api_key = settings.AI_API_KEY
        base_url = settings.AI_BASE_URL
        ai_model = settings.AI_MODEL
        logger.info(f"AI Config - BaseURL: {base_url}, Key length: {len(api_key) if api_key else 0}")
        logger.info(f"AI Config - Model: {ai_model}")
        
        if not api_key:
            logger.error("AI_API_KEY is not set in settings")
            return []

        client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url if base_url else None
        )
        
        response = await client.chat.completions.create(
            model=ai_model,  # 默认使用 ai_model，可以更改
            messages=[
                {"role": "system", "content": "You are a helpful assistant for classifying articles."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.1, # 低温度以获得一致的结果
        )
        print('🔍 [DEBUG] AI解析响应:', response)
        content = response.choices[0].message.content.strip()
        print('🔍 [DEBUG] AI解析响应内容:', content)
        # 5. 解析响应
        # 如果模型忽略了指令，清理可能的 markdown 代码块
        if content.startswith("```"):
            lines = content.split('\n')
            # 过滤掉 ```json 和 ``` 行
            clean_lines = [l for l in lines if not l.strip().startswith("```")]
            content = "\n".join(clean_lines)
            
        result_aids = json.loads(content)
        
        if isinstance(result_aids, list):
            logger.info(f"AI Analysis success. Found {len(result_aids)} education articles.")
            return result_aids
        else:
            logger.warning(f"AI response is not a valid list: {content}")
            return []
            
    except Exception as e:
        logger.error(f"AI Analysis failed: {e}")
        # 如果失败，返回空列表而不是崩溃
        return []
