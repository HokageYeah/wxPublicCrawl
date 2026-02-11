from loguru import logger
import json
from app.ai.utils.register import FunctionRegistry, ActionResponse, Action, ToolType

TAG = __name__
logger = logger.bind(tag=TAG)


class FunctionHandler:
    def __init__(self, llm_conn):
        self.llm_conn = llm_conn # 连接对象,用于调用工具
        self.function_registry = FunctionRegistry() # 函数注册器
        self.functions_desc = self.function_registry.get_all_function_desc() # 函数描述
        func_names = self.current_support_functions() # 当前支持的函数列表
        self.finish_init = True # 初始化完成


    def upload_functions_desc(self):
        """
        上传函数描述
        """
        self.functions_desc = self.function_registry.get_all_function_desc()

    def current_support_functions(self):
        """
        获取当前支持的函数列表
        """
        func_names = []
        for func in self.functions_desc:
            func_names.append(func["function"]["name"])
        # 打印当前支持的函数列表
        logger.bind(tag=TAG).info(f"当前支持的函数列表: {func_names}")
        return func_names

    def get_functions(self):
        """获取功能调用配置"""
        return self.functions_desc

    def get_function(self, name):
        """
        获取函数
        """
        return self.function_registry.get_function(name)

    def handle_llm_function_call(self, conn, function_call_data):
        """
        处理函数调用
        """
        try:
            function_name = function_call_data["name"]
            funcItem = self.get_function(function_name)
            if not funcItem:
                return ActionResponse(
                    action=Action.NOTFOUND, result="没有找到对应的函数", response=""
                )
            func = funcItem.func
            arguments = function_call_data["arguments"]
            arguments = json.loads(arguments) if arguments else {}
            logger.bind(tag=TAG).debug(f"调用函数: {function_name}, 参数: {arguments}")
            if (
                funcItem.type == ToolType.SYSTEM_CTL
                or funcItem.type == ToolType.IOT_CTL
            ):
                return func(conn, **arguments)
            elif funcItem.type == ToolType.WAIT:
                return func(**arguments)
            elif funcItem.type == ToolType.CHANGE_SYS_PROMPT:
                return func(conn, **arguments)
            else:
                return ActionResponse(
                    action=Action.NOTFOUND, result="没有找到对应的函数", response=""
                )
        except Exception as e:
            logger.bind(tag=TAG).error(f"处理function call错误: {e}")

        return None
