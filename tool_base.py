"""
- tool_base.py

- MCP Tool base class that defines generic fields for tool definition / registration

"""

from abc import ABC, abstractmethod
from mcp.types import Tool, TextContent

# Base class which MCP server tools will be derived from
class ToolBase(ABC):

  def __init__(self, name: str, tool_def: Tool):
    self._name = name
    self._tool_obj = tool_def

  def get_tool(self) -> Tool:
    return self._tool_obj
  
  def get_tool_name(self) -> str:
    return self._name

  """
  Pure virtual(?) method for calling an child tool objects
  """
  @abstractmethod
  def call_tool(self, args: dict) -> list[TextContent]:
    pass

  """
  Pure virtual(?) method for cleaning up any child tool objects
  """
  @abstractmethod
  def cleanup(self):
    pass

