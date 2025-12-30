import fastmcp
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

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
            print(f"天气查询: {location}")
            
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
            print('calculator----expression', expression)
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
    
    print("="*60)
    print("启动FastMCP服务器")
    print("="*60)
    print(f"项目根目录: {project_root}")
    print(f"服务器地址: http://localhost:8008/mcp")
    print(f"可用工具: weather, calculator, knowledge_base")
    print("="*60)
    
    try:
        server = FastmcpServer()
        server.run(transport="streamable-http", host="localhost", port=8008)
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except Exception as e:
        print(f"服务器启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)