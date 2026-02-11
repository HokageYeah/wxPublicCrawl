#!/usr/bin/env python3
"""
AI助手初始化测试脚本
用于测试完整的初始化流程
"""

import sys
import os
from pathlib import Path
import asyncio

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from app.ai.llm.mcp_llm_connect import MCPLLMConnect


async def test_ai_init():
    """测试AI助手初始化流程"""
    print("\n" + "=" * 80)
    print("🧪 AI助手初始化测试")
    print("=" * 80 + "\n")
    
    try:
        # 1. 创建连接器实例
        print("📝 步骤1: 创建MCPLLMConnect实例...")
        connector = MCPLLMConnect()
        print("✅ 实例创建成功\n")
        
        # 2. 异步初始化
        print("🔌 步骤2: 执行异步初始化...")
        success = await connector.async_init()
        
        if success:
            print("✅ 异步初始化成功\n")
        else:
            print("⚠️  异步初始化部分失败（可能MCP服务器未启动）\n")
        
        # 3. 测试基本对话
        print("💬 步骤3: 测试基本对话功能...")
        response = await connector.query(
            user_message="你好，请简单介绍一下你自己。",
            system_message="你是一个有用的AI助手。"
        )
        print(f"AI回复: {response}\n")
        
        # 4. 测试工具调用（如果MCP初始化成功）
        if success:
            print("🔧 步骤4: 测试MCP工具调用...")
            response = await connector.query(
                user_message="查询北京的天气",
                system_message="你是一个有用的AI助手。当用户需要查询天气、进行计算或查找知识时，请使用相应的工具。"
            )
            print(f"AI回复: {response}\n")
            
            # 5. 查看统计信息
            stats = connector.get_stats()
            print("📊 步骤5: 查看统计信息")
            print(f"对话轮次: {stats['conversation_turns']}")
            print(f"工具调用总次数: {stats['tool_calls']['total_calls']}")
            print(f"成功次数: {stats['tool_calls']['successful_calls']}")
            print(f"失败次数: {stats['tool_calls']['failed_calls']}")
        else:
            print("⏭️  跳过工具调用测试（MCP服务器未就绪）\n")
        
        print("=" * 80)
        print("✅ 所有测试完成！")
        print("=" * 80 + "\n")
        
        return True
        
    except Exception as e:
        print("=" * 80)
        print(f"❌ 测试失败: {e}")
        print("=" * 80 + "\n")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    success = await test_ai_init()
    return 0 if success else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

