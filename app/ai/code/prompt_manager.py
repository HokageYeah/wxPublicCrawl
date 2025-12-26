"""
提示词管理类
负责提示词的加载、缓存、渲染和管理
"""
from typing import Dict, Any, Optional
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader, TemplateNotFound
from loguru import logger
from app.utils.src_path import get_resource_path


class PromptTemplate:
    """提示词模板类"""
    def __init__(self, name: str, content: str):
        self.name = name
        self.content = content
        self._template = Template(content)
    
    def render(self, **kwargs) -> str:
        """
        渲染模板
        
        参数:
            **kwargs: 模板变量
            
        返回:
            str: 渲染后的提示词
        """
        try:
            return self._template.render(**kwargs)
        except Exception as e:
            logger.error(f"模板渲染失败 [{self.name}]: {e}")
            raise ValueError(f"模板渲染失败: {e}")
    
    def __str__(self):
        return f"PromptTemplate(name={self.name})"


class PromptManager:
    """
    提示词管理器
    
    特性：
    - 从文件或目录加载提示词
    - 提示词缓存
    - Jinja2模板渲染
    - 动态模板变量
    - 多环境支持（开发/生产）
    
    扩展方向：
    - 支持从数据库加载提示词
    - 提示词版本管理
    - A/B测试不同提示词
    - 提示词性能监控和优化建议
    - 支持多语言提示词
    """
    
    def __init__(self, prompt_dir: Optional[str] = None):
        """
        初始化提示词管理器
        
        参数:
            prompt_dir: 提示词文件夹路径，默认为 app/ai/prompt/
        """
        if prompt_dir is None:
            prompt_dir = get_resource_path('app/ai/prompt')
        
        self.prompt_dir = Path(prompt_dir)
        self._cache: Dict[str, PromptTemplate] = {}
        
        # 验证目录是否存在
        if not self.prompt_dir.exists():
            logger.warning(f"提示词目录不存在: {self.prompt_dir}")
            # 不抛出异常，允许后续手动添加提示词
        else:
            logger.info(f"提示词管理器已初始化 - 目录: {self.prompt_dir}")
    
    def load_prompt(self, name: str, file_name: Optional[str] = None) -> PromptTemplate:
        """
        加载提示词模板
        
        参数:
            name: 提示词名称（用于缓存键）
            file_name: 文件名，如果为None则使用 name.txt
            
        返回:
            PromptTemplate: 提示词模板对象
        """
        # 检查缓存
        if name in self._cache:
            logger.debug(f"从缓存加载提示词: {name}")
            return self._cache[name]
        
        # 确定文件路径
        if file_name is None:
            file_name = f"{name}.txt"
        
        file_path = self.prompt_dir / file_name
        
        # 读取文件
        if not file_path.exists():
            logger.error(f"提示词文件不存在: {file_path}")
            raise FileNotFoundError(f"提示词文件不存在: {file_path}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            # 创建模板并缓存
            template = PromptTemplate(name, content)
            self._cache[name] = template
            
            logger.info(f"成功加载提示词: {name} (文件: {file_name})")
            return template
            
        except Exception as e:
            logger.error(f"加载提示词文件失败 [{file_path}]: {e}")
            raise
    
    def get_prompt(self, name: str) -> PromptTemplate:
        """
        获取提示词模板（优先从缓存）
        
        参数:
            name: 提示词名称
            
        返回:
            PromptTemplate: 提示词模板对象
        """
        if name not in self._cache:
            # 尝试加载
            self.load_prompt(name)
        return self._cache[name]
    
    def render_prompt(self, name: str, **kwargs) -> str:
        """
        渲染提示词（一步到位）
        
        参数:
            name: 提示词名称
            **kwargs: 模板变量
            
        返回:
            str: 渲染后的提示词
        """
        template = self.get_prompt(name)
        return template.render(**kwargs)
    
    def add_prompt(self, name: str, content: str):
        """
        直接添加提示词到缓存（不保存到文件）
        适用于动态生成的提示词
        
        参数:
            name: 提示词名称
            content: 提示词内容
        """
        template = PromptTemplate(name, content)
        self._cache[name] = template
        logger.info(f"添加动态提示词: {name}")
    
    def reload_prompt(self, name: str):
        """
        重新加载提示词（清除缓存后重新加载）
        
        参数:
            name: 提示词名称
        """
        if name in self._cache:
            del self._cache[name]
        self.load_prompt(name)
        logger.info(f"重新加载提示词: {name}")
    
    def clear_cache(self):
        """清空所有缓存的提示词"""
        self._cache.clear()
        logger.info("提示词缓存已清空")
    
    def list_prompts(self) -> list[str]:
        """
        列出所有已加载的提示词
        
        返回:
            list[str]: 提示词名称列表
        """
        return list(self._cache.keys())
    
    def list_prompt_files(self) -> list[str]:
        """
        列出提示词目录中的所有文件
        
        返回:
            list[str]: 文件名列表
        """
        if not self.prompt_dir.exists():
            return []
        return [f.name for f in self.prompt_dir.glob("*.txt")]
    
    # 以下方法为未来扩展预留接口
    
    def load_prompt_from_db(self, prompt_id: str) -> PromptTemplate:
        """
        从数据库加载提示词
        预留接口，用于支持提示词的集中管理和版本控制
        
        参数:
            prompt_id: 数据库中的提示词ID
            
        返回:
            PromptTemplate: 提示词模板对象
        """
        # TODO: 实现数据库加载逻辑
        raise NotImplementedError("数据库加载功能待实现")
    
    def save_prompt_to_db(self, name: str, content: str, metadata: Optional[Dict[str, Any]] = None):
        """
        保存提示词到数据库
        预留接口，用于提示词的持久化管理
        
        参数:
            name: 提示词名称
            content: 提示词内容
            metadata: 元数据（如版本、标签、描述等）
        """
        # TODO: 实现数据库保存逻辑
        raise NotImplementedError("数据库保存功能待实现")
    
    def get_prompt_with_version(self, name: str, version: str) -> PromptTemplate:
        """
        获取特定版本的提示词
        预留接口，用于提示词版本管理和A/B测试
        
        参数:
            name: 提示词名称
            version: 版本号
            
        返回:
            PromptTemplate: 提示词模板对象
        """
        # TODO: 实现版本管理逻辑
        raise NotImplementedError("版本管理功能待实现")


class PromptBuilder:
    """
    提示词构建器
    用于动态构建复杂的提示词，支持链式调用
    
    示例:
        prompt = (PromptBuilder()
            .add_system_context("你是一个专业的文章分类助手")
            .add_instruction("分析以下文章")
            .add_examples([...])
            .add_constraints(["只返回JSON", "不要包含Markdown"])
            .build())
    """
    
    def __init__(self):
        self.parts = []
    
    def add_system_context(self, context: str) -> 'PromptBuilder':
        """添加系统上下文"""
        self.parts.append(context)
        return self
    
    def add_instruction(self, instruction: str) -> 'PromptBuilder':
        """添加指令"""
        self.parts.append(f"\n{instruction}")
        return self
    
    def add_examples(self, examples: list[str]) -> 'PromptBuilder':
        """添加示例"""
        if examples:
            self.parts.append("\n示例：")
            for i, example in enumerate(examples, 1):
                self.parts.append(f"{i}. {example}")
        return self
    
    def add_data(self, data: str, label: str = "数据") -> 'PromptBuilder':
        """添加数据"""
        self.parts.append(f"\n{label}：\n{data}")
        return self
    
    def add_constraints(self, constraints: list[str]) -> 'PromptBuilder':
        """添加约束条件"""
        if constraints:
            self.parts.append("\n请严格遵守以下规则：")
            for i, constraint in enumerate(constraints, 1):
                self.parts.append(f"{i}. {constraint}")
        return self
    
    def add_custom_section(self, content: str) -> 'PromptBuilder':
        """添加自定义部分"""
        self.parts.append(f"\n{content}")
        return self
    
    def build(self) -> str:
        """构建最终的提示词"""
        return "\n".join(self.parts)


# 全局提示词管理器实例（单例模式）
_global_prompt_manager: Optional[PromptManager] = None


def get_prompt_manager(prompt_dir: Optional[str] = None) -> PromptManager:
    """
    获取全局提示词管理器实例（单例）
    
    返回:
        PromptManager: 全局提示词管理器
    """
    global _global_prompt_manager
    if _global_prompt_manager is None:
        _global_prompt_manager = PromptManager(prompt_dir)
    return _global_prompt_manager


# 便捷函数
def load_and_render_prompt(name: str, **kwargs) -> str:
    """
    加载并渲染提示词（便捷函数）
    
    参数:
        name: 提示词名称
        **kwargs: 模板变量
        
    返回:
        str: 渲染后的提示词
    """
    manager = get_prompt_manager()
    return manager.render_prompt(name, **kwargs)

