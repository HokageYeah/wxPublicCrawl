"""
AI模块使用示例
展示如何使用AIClient和PromptManager进行各种AI任务
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
import json
from loguru import logger
from app.ai.llm.ai_client import AIClient, create_default_client
from app.ai.utils.prompt_manager import (
    get_prompt_manager, 
    PromptBuilder,
    load_and_render_prompt
)


# ============================================
# 示例1: 基础AI对话
# ============================================
async def example_basic_chat():
    """基础对话示例"""
    print("\n" + "="*50)
    print("示例1: 基础AI对话")
    print("="*50)
    
    client = AIClient(temperature=0.7)
    
    response = await client.chat(
        user_message="用一句话介绍Python的特点",
        system_message="你是一个编程专家"
    )
    
    print(f"AI回答: {response}")


# ============================================
# 示例2: JSON格式响应
# ============================================
async def example_json_response():
    """JSON响应示例"""
    print("\n" + "="*50)
    print("示例2: JSON格式响应")
    print("="*50)
    
    client = AIClient(temperature=0.1)
    
    result = await client.chat_with_json_response(
        user_message="""
        请分析以下文章的主题，返回JSON格式：
        {"topic": "主题", "category": "分类", "keywords": ["关键词1", "关键词2"]}
        
        文章标题：人工智能在医疗领域的应用与挑战
        """,
        system_message="你是一个文章分析专家，只返回JSON格式"
    )
    
    print(f"解析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")


# ============================================
# 示例3: 流式响应
# ============================================
async def example_stream_chat():
    """流式响应示例"""
    print("\n" + "="*50)
    print("示例3: 流式响应（实时显示）")
    print("="*50)
    
    client = AIClient()
    
    print("AI正在回答: ", end='', flush=True)
    async for chunk in client.stream_chat(
        user_message="写一首关于代码的五言绝句",
        system_message="你是一个诗人"
    ):
        print(chunk, end='', flush=True)
    print("\n")


# ============================================
# 示例4: 带对话历史的多轮对话
# ============================================
async def example_conversation_with_history():
    """多轮对话示例"""
    print("\n" + "="*50)
    print("示例4: 多轮对话（带历史）")
    print("="*50)
    
    # 启用对话历史
    client = AIClient(enable_history=True, max_history=10)
    
    # 第一轮
    response1 = await client.chat(
        user_message="我的项目名叫wxPublicCrawl",
        system_message="你是一个助手",
        use_history=True
    )
    print(f"第1轮 - AI: {response1}")
    
    # 第二轮（AI会记住项目名）
    response2 = await client.chat(
        user_message="我的项目叫什么名字？",
        use_history=True
    )
    print(f"第2轮 - AI: {response2}")
    
    # 查看历史
    print("\n对话历史:")
    for i, msg in enumerate(client.get_history(), 1):
        print(f"  {i}. [{msg['role']}] {msg['content'][:50]}...")


# ============================================
# 示例5: 使用提示词管理器
# ============================================
async def example_prompt_manager():
    """提示词管理示例"""
    print("\n" + "="*50)
    print("示例5: 提示词管理")
    print("="*50)
    
    manager = get_prompt_manager()
    
    # 动态添加提示词
    manager.add_prompt(
        "sentiment_analysis",
        """
你是一个情感分析专家。
请分析以下文本的情感倾向：
{{ text }}

返回JSON格式：{"sentiment": "positive|negative|neutral", "confidence": 0.0-1.0}
        """
    )
    
    # 渲染提示词
    prompt = manager.render_prompt(
        "sentiment_analysis",
        text="这个产品真的太棒了！质量很好，服务也很周到。"
    )
    
    print("渲染后的提示词:")
    print(prompt)
    
    # 使用AI分析
    client = AIClient(temperature=0.1)
    result = await client.chat_with_json_response(
        user_message=prompt,
        system_message="你是一个情感分析专家"
    )
    
    print(f"\n分析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")


# ============================================
# 示例6: 使用PromptBuilder构建复杂提示词
# ============================================
async def example_prompt_builder():
    """提示词构建器示例"""
    print("\n" + "="*50)
    print("示例6: 使用PromptBuilder构建提示词")
    print("="*50)
    
    # 构建提示词
    prompt = (PromptBuilder()
        .add_system_context("你是一个专业的数据分析师")
        .add_instruction("请分析以下用户评论，提取关键信息")
        .add_data(
            "1. 商品质量很好，但是物流太慢\n2. 客服态度不错，解决问题很快\n3. 价格有点贵",
            label="用户评论"
        )
        .add_constraints([
            "返回JSON格式",
            "包含优点和缺点",
            "给出改进建议"
        ])
        .build())
    
    print("构建的提示词:")
    print(prompt)
    
    # 使用AI分析
    client = AIClient(temperature=0.3)
    result = await client.chat_with_json_response(
        user_message=prompt,
        system_message="你是一个数据分析师"
    )
    
    print(f"\n分析结果: {json.dumps(result, ensure_ascii=False, indent=2)}")


# ============================================
# 示例7: 实际业务场景 - 内容分类
# ============================================
async def example_content_classification():
    """内容分类示例"""
    print("\n" + "="*50)
    print("示例7: 内容分类（实际业务场景）")
    print("="*50)
    
    # 待分类的文章列表
    articles = [
        {"id": "1", "title": "小学数学教学方法探讨"},
        {"id": "2", "title": "今日天气预报：明天有雨"},
        {"id": "3", "title": "高考志愿填报指南"},
        {"id": "4", "title": "美食推荐：北京烤鸭"},
        {"id": "5", "title": "在线教育平台如何选择"}
    ]
    
    # 使用PromptBuilder构建分类提示词
    articles_json = json.dumps(articles, ensure_ascii=False, indent=2)
    
    prompt = (PromptBuilder()
        .add_system_context("你是一个专业的文章分类助手")
        .add_instruction("请找出所有与'教育'相关的文章")
        .add_data(articles_json, label="文章列表")
        .add_constraints([
            "只返回JSON数组，包含教育相关文章的ID",
            "例如: [\"1\", \"3\"]",
            "如果没有相关文章，返回空数组 []"
        ])
        .build())
    
    # 调用AI
    client = AIClient(temperature=0.1)
    education_ids = await client.chat_with_json_response(
        user_message=prompt,
        system_message="你是一个文章分类助手"
    )
    
    print(f"教育相关文章ID: {education_ids}")
    print("\n分类结果:")
    for article in articles:
        is_education = article["id"] in education_ids
        status = "✓ 教育相关" if is_education else "✗ 非教育"
        print(f"  {status} - {article['title']}")


# ============================================
# 示例8: 错误处理
# ============================================
async def example_error_handling():
    """错误处理示例"""
    print("\n" + "="*50)
    print("示例8: 错误处理")
    print("="*50)
    
    client = AIClient(temperature=0.1)
    
    try:
        # 请求返回JSON但AI可能返回非JSON格式
        result = await client.chat_with_json_response(
            user_message="随便说点什么"  # 模糊的指令可能导致非JSON响应
        )
        print(f"结果: {result}")
    except ValueError as e:
        print(f"✓ 捕获到JSON解析错误: {e}")
    except Exception as e:
        print(f"✓ 捕获到其他错误: {e}")


# ============================================
# 主函数：运行所有示例
# ============================================
async def main():
    """运行所有示例"""
    print("\n" + "🚀 " * 20)
    print("AI模块使用示例集合")
    print("🚀 " * 20)
    
    try:
        await example_basic_chat()
        await example_json_response()
        await example_stream_chat()
        await example_conversation_with_history()
        await example_prompt_manager()
        await example_prompt_builder()
        await example_content_classification()
        await example_error_handling()
        
        print("\n" + "✅ " * 20)
        print("所有示例运行完成！")
        print("✅ " * 20 + "\n")
        
    except Exception as e:
        logger.error(f"示例运行失败: {e}")
        print(f"\n❌ 错误: {e}")
        print("请确保已正确配置 AI_API_KEY、AI_BASE_URL 和 AI_MODEL")


# ============================================
# 快速测试单个功能
# ============================================
async def quick_test():
    """快速测试AI功能是否可用"""
    print("🔍 快速测试AI功能...")
    
    try:
        client = AIClient()
        response = await client.chat(
            user_message="说'你好'",
            system_message="你是助手"
        )
        print(f"✅ AI功能正常！响应: {response}")
        return True
    except Exception as e:
        print(f"❌ AI功能异常: {e}")
        return False


if __name__ == "__main__":
    # 运行所有示例
    asyncio.run(main())
    
    # 或者只运行快速测试
    # asyncio.run(quick_test())
    
    # 或者运行单个示例
    # asyncio.run(example_basic_chat())

