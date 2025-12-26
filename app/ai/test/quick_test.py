"""
AI模块快速测试脚本
用于验证AI功能是否正常工作
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import asyncio
from loguru import logger


async def test_ai_config():
    """测试AI配置是否正确"""
    print("\n" + "="*60)
    print("🔍 测试1: 检查AI配置")
    print("="*60)
    
    try:
        from app.core.config import settings
        
        print(f"✓ AI_API_KEY: {'已配置' if settings.AI_API_KEY else '❌ 未配置'}")
        print(f"✓ AI_BASE_URL: {settings.AI_BASE_URL or '使用默认'}")
        print(f"✓ AI_MODEL: {settings.AI_MODEL or '❌ 未配置'}")
        
        if not settings.AI_API_KEY:
            print("\n⚠️  请在环境变量或 .env 文件中配置 AI_API_KEY")
            return False
        
        if not settings.AI_MODEL:
            print("\n⚠️  请在环境变量或 .env 文件中配置 AI_MODEL")
            return False
            
        return True
    except Exception as e:
        print(f"❌ 配置检查失败: {e}")
        return False


async def test_ai_client():
    """测试AI客户端基础功能"""
    print("\n" + "="*60)
    print("🔍 测试2: AI客户端基础功能")
    print("="*60)
    
    try:
        from app.ai.code.ai_client import AIClient
        
        print("正在创建AI客户端...")
        client = AIClient(temperature=0.7)
        print("✓ AI客户端创建成功")
        
        print("\n正在发送测试消息...")
        response = await client.chat(
            user_message="请只说'你好'两个字",
            system_message="你是一个助手，严格按照用户要求回复"
        )
        
        print(f"✓ AI响应成功")
        print(f"  响应内容: {response[:100]}{'...' if len(response) > 100 else ''}")
        return True
        
    except Exception as e:
        print(f"❌ AI客户端测试失败: {e}")
        logger.exception("详细错误:")
        return False


async def test_json_response():
    """测试JSON响应功能"""
    print("\n" + "="*60)
    print("🔍 测试3: JSON响应功能")
    print("="*60)
    
    try:
        from app.ai.code.ai_client import AIClient
        import json
        
        client = AIClient(temperature=0.1)
        
        print("正在请求JSON格式响应...")
        result = await client.chat_with_json_response(
            user_message='请返回这个JSON: {"status": "ok", "message": "测试成功"}',
            system_message="你是一个助手，只返回有效的JSON格式"
        )
        
        print(f"✓ JSON解析成功")
        print(f"  结果: {json.dumps(result, ensure_ascii=False, indent=2)}")
        return True
        
    except Exception as e:
        print(f"❌ JSON响应测试失败: {e}")
        return False


async def test_prompt_manager():
    """测试提示词管理器"""
    print("\n" + "="*60)
    print("🔍 测试4: 提示词管理器")
    print("="*60)
    
    try:
        from app.ai.code.prompt_manager import get_prompt_manager, PromptBuilder
        
        print("正在初始化提示词管理器...")
        manager = get_prompt_manager('app/ai/prompt')
        print("✓ 提示词管理器初始化成功")
        
        # 测试加载现有提示词
        print("\n正在加载 education_prompt...")
        try:
            manager.load_prompt("education_prompt", "education_prompt.txt")
            print("✓ 提示词加载成功")
        except FileNotFoundError:
            print("⚠️  education_prompt.txt 文件未找到（如果不使用教育分析功能，可以忽略）")
        
        # 测试动态添加提示词
        print("\n正在测试动态提示词...")
        manager.add_prompt("test_prompt", "这是测试: {{ test_data }}")
        rendered = manager.render_prompt("test_prompt", test_data="成功")
        print(f"✓ 提示词渲染成功: {rendered}")
        
        # 测试 PromptBuilder
        print("\n正在测试 PromptBuilder...")
        prompt = (PromptBuilder()
            .add_system_context("你是助手")
            .add_instruction("执行测试")
            .build())
        print(f"✓ PromptBuilder 构建成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 提示词管理器测试失败: {e}")
        logger.exception("详细错误:")
        return False


async def main():
    """运行所有测试"""
    print("\n" + "🚀 " * 20)
    print("AI模块快速测试")
    print("🚀 " * 20)
    
    results = []
    
    # 测试1: 配置检查
    result1 = await test_ai_config()
    results.append(("配置检查", result1))
    
    if not result1:
        print("\n❌ 配置检查失败，请先配置 AI_API_KEY 和 AI_MODEL")
        print("\n配置方法:")
        print("1. 在项目根目录创建 .env.desktop 文件")
        print("2. 添加以下内容:")
        print("   AI_API_KEY=your-api-key")
        print("   AI_BASE_URL=https://api.openai.com/v1  # 可选")
        print("   AI_MODEL=gpt-3.5-turbo")
        return
    
    # 测试2: AI客户端
    result2 = await test_ai_client()
    results.append(("AI客户端", result2))
    
    if not result2:
        print("\n⚠️  AI客户端测试失败，跳过后续测试")
        print_summary(results)
        return
    
    # 测试3: JSON响应
    result3 = await test_json_response()
    results.append(("JSON响应", result3))
    
    # 测试4: 提示词管理器
    result4 = await test_prompt_manager()
    results.append(("提示词管理器", result4))
    
    # 打印总结
    print_summary(results)


def print_summary(results):
    """打印测试总结"""
    print("\n" + "="*60)
    print("📊 测试总结")
    print("="*60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    total = len(results)
    passed = sum(1 for _, r in results if r)
    
    print(f"\n总计: {passed}/{total} 项测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！AI模块可以正常使用。")
        print("\n下一步:")
        print("- 查看 app/ai/README.md 了解详细使用方法")
        print("- 运行 python app/ai/test/usage_examples.py 查看更多示例")
    else:
        print("\n⚠️  部分测试失败，请检查配置和环境。")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  测试被用户中断")
    except Exception as e:
        print(f"\n\n❌ 测试过程中出现错误: {e}")
        logger.exception("详细错误:")

