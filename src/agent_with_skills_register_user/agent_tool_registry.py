from typing import Dict, Callable, Any, List, Optional
from google.adk.tools import FunctionTool, BaseTool

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, Callable] = {}

    def register_tool(self, func: Callable):
        """Register a tool function."""
        name = getattr(func, "__name__", str(func))
        self._tools[name] = func
        return func

    def get_tool(self, name: str) -> Optional[BaseTool]:
        """Get a FunctionTool instance by name."""
        func = self._tools.get(name)
        if func:
            return FunctionTool(func)
        return None

    def get_tools(self, names: List[str]) -> List[BaseTool]:
        """Get multiple FunctionTool instances by name."""
        tools = []
        for name in names:
            tool = self.get_tool(name)
            if tool:
                tools.append(tool)
        return tools

# Global instance for registration
tool_registry = ToolRegistry()
