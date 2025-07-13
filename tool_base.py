"""
- tool_base.py

- MCP Tool base class that defines generic fields for tool definition / registration

"""
from tool_manager import ToolManager
from abc import ABC, abstractmethod
from mcp.types import Tool, TextContent

# Base class which MCP server tools will be derived from
class ToolBase(ABC):

  def __init__(self, name: str, tool_def: Tool):
    self._name = name
    self._tool_obj = tool_def
    ToolManager()._register_tool(self)

  @abstractmethod
  def _call_tool(self, args: dict) -> list[TextContent]:
    pass # essentially = 0 in C++ ??

