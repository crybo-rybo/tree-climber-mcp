"""
- tool_manager.py

- All tools will be "plugged" into the tool manager and the main surver
  will use the tool manager to setup all of the tools

"""

from tool_base import ToolBase
from mcp.types import TextContent

class ToolManager:

  def __init__(self):
    self._tool_list = []

  def _register_tool(self, tool_inst: ToolBase):
    self._tool_list.append(tool_inst)

  def _export_tools(self):
    expList = []
    for tool in self._tool_list:
      expList.append(tool._obj)

    return expList
  
  def _call_tool(self, name: str, args: dict) -> TextContent:
    gCall = False
    for tool in self._tool_list:
      if tool._name == name:
        return tool._call_tool(args)
    
    return TextContent(
      type="text",
      text=f"Error: Unknown Tool Name - {name}"
    )
      

