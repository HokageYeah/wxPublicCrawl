"""
MCP-LLM连接器使用示例
展示如何使用MCPLLMConnect实现AI自动调用工具
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).resolve().parent.parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from loguru import logger
from app.ai.llm.mcp_llm_connect import MCPLLMConnect
from app.ai.mcp.mcp_client.client_manager import MCPClientManager


# 配置日志
logger.add(
    "mcp_llm_example.log",
    level="DEBUG",
    filter=lambda r: "MCP" in r["extra"].get("tag", "")
)


async def example_basic_query():
    """示例1: 基础查询"""
    print("\n" + "="*60)
    print("示例1: 基础查询（AI自动调用工具）")
    print("="*60)
    
    # 注意：这里需要实际的llm_conn对象
    # 这只是演示代码结构
    print("⚠️  此示例需要实际的llm_conn对象，请根据项目实际情况调整")
    
    # # 1. 初始化MCP管理器
    # mcp_manager = MCPClientManager(llm_conn)
    # await mcp_manager.init_mcp_clients()
    
    # # 2. 创建连接器
    # connector = MCPLLMConnect(mcp_manager)
    
    # # 3. 发送查询
    # response = await connector.query("查询北京的天气")
    # print(f"\nAI回复: {response}")


async def example_multi_step_task():
    """示例2: 多步骤任务"""
    print("\n" + "="*60)
    print("示例2: 多步骤任务（AI组合多个工具）")
    print("="*60)
    
    # connector = MCPLLMConnect(mcp_manager)
    
    # # AI会自动规划步骤并调用多个工具
    # response = await connector.query(
    #     "帮我翻到公众号列表的第5页，然后告诉我第一篇文章的标题"
    # )
    # print(f"\nAI回复: {response}")
    
    print("示例代码请参考 README_MCP_LLM.md")


async def example_with_context():
    """示例3: 带上下文的对话"""
    print("\n" + "="*60)
    print("示例3: 带上下文的对话")
    print("="*60)
    
    # connector = MCPLLMConnect(mcp_manager)
    
    # # 第一轮对话
    # response1 = await connector.query("查询北京的天气")
    # print(f"\n轮1 - AI: {response1}")
    
    # # 第二轮对话（AI会记住之前的内容）
    # response2 = await connector.query("那上海呢？")
    # print(f"\n轮2 - AI: {response2}")
    
    # # 查看对话历史
    # history = connector.get_conversation_history()
    # print(f"\n对话轮数: {len(history)}")
    
    print("示例代码请参考 README_MCP_LLM.md")


async def example_statistics():
    """示例4: 统计信息"""
    print("\n" + "="*60)
    print("示例4: 查看工具使用统计")
    print("="*60)
    
    # connector = MCPLLMConnect(mcp_manager)
    
    # # 执行一些查询
    # await connector.query("查询天气")
    # await connector.query("翻页")
    # await connector.query("获取文章")
    
    # # 查看统计
    # stats = connector.get_stats()
    # print(f"\n工具调用统计:")
    # print(f"  总调用次数: {stats['tool_calls']['total_calls']}")
    # print(f"  成功: {stats['tool_calls']['successful_calls']}")
    # print(f"  失败: {stats['tool_calls']['failed_calls']}")
    # print(f"\n工具使用详情:")
    # for tool, count in stats['tool_calls']['tools_used'].items():
    #     print(f"  {tool}: {count}次")
    
    print("示例代码请参考 README_MCP_LLM.md")


async def example_custom_config():
    """示例5: 自定义配置"""
    print("\n" + "="*60)
    print("示例5: 自定义配置")
    print("="*60)
    
    # from app.ai.llm.ai_client import AIClient
    
    # # 创建自定义AI客户端
    # custom_ai = AIClient(
    #     model="gpt-4",
    #     temperature=0.3,
    #     max_tokens=2000
    # )
    
    # # 使用自定义配置创建连接器
    # connector = MCPLLMConnect(
    #     mcp_manager=mcp_manager,
    #     ai_client=custom_ai,
    #     max_tool_calls=5  # 最多5次工具调用
    # )
    
    # response = await connector.query("执行复杂任务...")
    # print(f"\nAI回复: {response}")
    
    print("示例代码请参考 README_MCP_LLM.md")


async def example_error_handling():
    """示例6: 错误处理"""
    print("\n" + "="*60)
    print("示例6: 错误处理")
    print("="*60)
    
    # connector = MCPLLMConnect(mcp_manager)
    
    # try:
    #     # 可能导致工具调用失败的查询
    #     response = await connector.query("使用不存在的工具")
    #     print(f"\nAI回复: {response}")
    # except Exception as e:
    #     print(f"\n捕获到错误: {e}")
    #     
    #     # 查看统计了解失败原因
    #     stats = connector.get_stats()
    #     print(f"失败的工具调用: {stats['tool_calls']['failed_calls']}")
    
    print("示例代码请参考 README_MCP_LLM.md")


async def example_streaming():
    """示例7: 流式响应（不支持工具）"""
    print("\n" + "="*60)
    print("示例7: 流式响应")
    print("="*60)
    
    # connector = MCPLLMConnect(mcp_manager)
    
    # # 流式输出（不支持工具调用）
    # print("\nAI正在回答: ", end='')
    # async for chunk in connector.stream_query("讲个故事"):
    #     print(chunk, end='', flush=True)
    # print("\n")
    
    print("⚠️  流式模式暂不支持工具调用")
    print("示例代码请参考 README_MCP_LLM.md")


async def example_pagination_automation():
    """示例8: 实际场景 - 公众号自动翻页"""
    print("\n" + "="*60)
    print("示例8: 实际场景 - 公众号自动翻页")
    print("="*60)
    
    # connector = MCPLLMConnect(mcp_manager)
    
    # # 自然语言指令，AI自动完成复杂任务
    # response = await connector.query("""
    #     帮我执行以下任务：
    #     1. 从当前页开始，连续翻5页
    #     2. 记录每一页有多少篇文章
    #     3. 统计总共有多少篇文章
    #     4. 给我一个汇总报告
    # """)
    
    # print(f"\nAI报告:\n{response}")
    
    print("这是MCP-LLM连接器的核心应用场景！")
    print("AI会自动：")
    print("  1. 规划任务步骤")
    print("  2. 循环调用 next_page 工具")
    print("  3. 调用 get_article_count 工具")
    print("  4. 汇总数据生成报告")
    print("\n示例代码请参考 README_MCP_LLM.md")


async def main():
    """运行所有示例"""
    print("\n" + "🚀 "*20)
    print("MCP-LLM连接器使用示例集合")
    print("🚀 "*20)
    
    try:
        await example_basic_query()
        await example_multi_step_task()
        await example_with_context()
        await example_statistics()
        await example_custom_config()
        await example_error_handling()
        await example_streaming()
        await example_pagination_automation()
        
        print("\n" + "="*60)
        print("✅ 所有示例演示完成！")
        print("="*60)
        print("\n💡 提示:")
        print("  1. 这些示例需要实际的MCP服务和配置才能运行")
        print("  2. 请参考 README_MCP_LLM.md 了解详细使用方法")
        print("  3. 确保已配置 AI_API_KEY 和 MCP 服务")
        print("  4. 查看日志文件 mcp_llm_example.log 了解详细执行过程")
        
    except Exception as e:
        logger.error(f"示例运行失败: {e}")
        print(f"\n❌ 错误: {e}")


if __name__ == "__main__":
    # 运行所有示例
    asyncio.run(main())

