"""
AI客户端基础类
提供与AI模型交互的统一接口，支持扩展功能如记忆、流式响应等
"""
from typing import Optional, List, Dict, Any, AsyncIterator
from openai import AsyncOpenAI
from loguru import logger
from app.core.config import settings


class Message:
    """消息类，用于封装对话消息"""
    def __init__(self, role: str, content: str):
        self.role = role  # system, user, assistant
        self.content = content
    
    def to_dict(self) -> Dict[str, str]:
        """转换为OpenAI API需要的字典格式"""
        return {"role": self.role, "content": self.content}


class ConversationHistory:
    """对话历史管理类，为记忆功能提供基础"""
    def __init__(self, max_history: int = 10):
        self.messages: List[Message] = []
        self.max_history = max_history
    
    def add_message(self, role: str, content: str):
        """添加消息到历史记录"""
        self.messages.append(Message(role, content))
        # 保持历史记录在限制范围内（保留system消息）
        if len(self.messages) > self.max_history:
            # 保留第一条system消息（如果有）
            system_msgs = [m for m in self.messages if m.role == "system"]
            other_msgs = [m for m in self.messages if m.role != "system"]
            self.messages = system_msgs + other_msgs[-(self.max_history - len(system_msgs)):]
    
    def get_messages(self) -> List[Dict[str, str]]:
        """获取消息列表（OpenAI API格式）"""
        return [msg.to_dict() for msg in self.messages]
    
    def clear(self):
        """清空历史记录"""
        self.messages = []
    
    def get_last_n_messages(self, n: int) -> List[Dict[str, str]]:
        """获取最后N条消息"""
        return [msg.to_dict() for msg in self.messages[-n:]]


class AIClient:
    """
    AI客户端基础类
    封装OpenAI API调用，提供统一的接口
    
    特性：
    - 单次对话和多轮对话支持
    - 对话历史管理（为记忆功能预留）
    - 流式响应支持
    - 可配置的模型参数
    - 错误处理和日志记录
    
    扩展方向：
    - 接入向量数据库（如Pinecone、Weaviate）进行知识检索
    - RAG（检索增强生成）功能
    - 函数调用（Function Calling，MCP）支持
    - 多模态支持（图片、音频等）
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        enable_history: bool = False,
        max_history: int = 10
    ):
        """
        初始化AI客户端
        
        参数:
            api_key: OpenAI API密钥，默认从settings获取
            base_url: API基础URL，用于使用代理或其他兼容服务
            model: 模型名称，默认从settings获取
            temperature: 温度参数，控制输出随机性 (0-2)
            max_tokens: 最大生成token数
            enable_history: 是否启用对话历史
            max_history: 最大历史记录数
        """
        self.api_key = api_key or settings.AI_API_KEY
        self.base_url = base_url or settings.AI_BASE_URL
        self.model = model or settings.AI_MODEL
        self.temperature = temperature
        self.max_tokens = max_tokens
        
        # 对话历史管理
        self.enable_history = enable_history
        self.history = ConversationHistory(max_history) if enable_history else None
        
        # 验证配置
        if not self.api_key:
            logger.error("AI_API_KEY未配置")
            raise ValueError("AI_API_KEY必须配置")
        
        # 初始化OpenAI客户端
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url if self.base_url else None
        )
        
        logger.info(f"AI客户端已初始化 - 模型: {self.model}, BaseURL: {self.base_url or '默认'}")
    
    async def chat(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None,
        use_history: bool = False
    ) -> str:
        """
        发送聊天消息并获取响应
        
        参数:
            user_message: 用户消息内容
            system_message: 系统消息（设定AI角色和行为）
            temperature: 温度参数，覆盖默认值
            use_history: 是否使用对话历史（需要enable_history=True）
            
        返回:
            str: AI的响应内容
        """
        try:
            messages = []
            
            # 如果启用历史且请求使用历史
            if use_history and self.history:
                messages = self.history.get_messages()
                # 如果提供了新的system_message，替换历史中的system消息
                if system_message:
                    messages = [m for m in messages if m["role"] != "system"]
                    messages.insert(0, {"role": "system", "content": system_message})
            else:
                # 不使用历史，构建新的消息列表
                if system_message:
                    messages.append({"role": "system", "content": system_message})
            
            # 添加用户消息
            messages.append({"role": "user", "content": user_message})
            
            # 调用API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature if temperature is not None else self.temperature,
                max_tokens=self.max_tokens
            )
            
            # 提取响应内容
            content = response.choices[0].message.content.strip()
            
            # 如果启用历史，保存对话
            if self.enable_history and use_history and self.history:
                self.history.add_message("user", user_message)
                self.history.add_message("assistant", content)
            
            logger.info(f"AI响应成功 - 消息数: {len(messages)}, 响应长度: {len(content)}")
            return content
            
        except Exception as e:
            logger.error(f"AI聊天失败: {e}")
            raise
    
    async def chat_with_json_response(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> Any:
        """
        发送消息并期望JSON格式的响应
        自动处理Markdown代码块包裹的情况
        
        参数:
            user_message: 用户消息内容
            system_message: 系统消息
            temperature: 温度参数
            
        返回:
            Any: 解析后的JSON对象（通常是dict或list）
        """
        import json
        
        content = await self.chat(user_message, system_message, temperature)
        
        # 清理可能的Markdown代码块
        if content.startswith("```"):
            lines = content.split('\n')
            clean_lines = [l for l in lines if not l.strip().startswith("```")]
            content = "\n".join(clean_lines)
        
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            logger.error(f"JSON解析失败: {e}, 原始内容: {content}")
            raise ValueError(f"AI返回的内容不是有效的JSON格式: {content[:100]}...")
    
    async def stream_chat(
        self,
        user_message: str,
        system_message: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> AsyncIterator[str]:
        """
        流式聊天，逐步返回响应内容
        适用于需要实时显示生成内容的场景
        
        参数:
            user_message: 用户消息内容
            system_message: 系统消息
            temperature: 温度参数
            
        生成:
            str: 逐步生成的内容片段
        """
        try:
            messages = []
            if system_message:
                messages.append({"role": "system", "content": system_message})
            messages.append({"role": "user", "content": user_message})
            
            stream = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature if temperature is not None else self.temperature,
                max_tokens=self.max_tokens,
                stream=True
            )
            
            full_content = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content_piece = chunk.choices[0].delta.content
                    full_content += content_piece
                    yield content_piece
            
            # 如果启用历史，保存完整对话
            if self.enable_history and self.history:
                self.history.add_message("user", user_message)
                self.history.add_message("assistant", full_content)
                
        except Exception as e:
            logger.error(f"流式聊天失败: {e}")
            raise
    
    def clear_history(self):
        """清空对话历史"""
        if self.history:
            self.history.clear()
            logger.info("对话历史已清空")
    
    def get_history(self) -> List[Dict[str, str]]:
        """获取对话历史"""
        if self.history:
            return self.history.get_messages()
        return []
    
    # 以下方法为未来扩展预留接口
    
    async def chat_with_retrieval(
        self,
        user_message: str,
        retrieval_query: Optional[str] = None,
        top_k: int = 3
    ) -> str:
        """
        带检索增强的聊天（RAG）
        预留接口，待接入向量数据库后实现
        
        参数:
            user_message: 用户消息
            retrieval_query: 检索查询（默认使用user_message）
            top_k: 检索返回的文档数量
            
        返回:
            str: AI响应
        """
        # TODO: 实现向量检索逻辑
        # 1. 使用retrieval_query在向量数据库中检索相关文档
        # 2. 将检索结果作为上下文添加到提示词中
        # 3. 调用chat方法生成响应
        raise NotImplementedError("RAG功能待实现，需要先接入向量数据库")
    
    async def chat_with_function_calling(
        self,
        user_message: str,
        functions: List[Dict[str, Any]],
        system_message: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        支持函数调用的聊天
        预留接口，用于让AI调用特定工具或函数
        
        参数:
            user_message: 用户消息
            functions: 可用函数列表（OpenAI函数调用格式）
            system_message: 系统消息
            
        返回:
            Dict: 包含响应和函数调用信息
        """
        # TODO: 实现函数调用逻辑
        raise NotImplementedError("函数调用功能待实现")


# 便捷函数：创建默认AI客户端
def create_default_client(enable_history: bool = False) -> AIClient:
    """
    创建使用默认配置的AI客户端
    
    参数:
        enable_history: 是否启用对话历史
        
    返回:
        AIClient: 配置好的AI客户端实例
    """
    return AIClient(enable_history=enable_history)

