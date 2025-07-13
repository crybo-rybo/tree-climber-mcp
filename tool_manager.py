"""
- tool_manager.py

- All tools will be "plugged" into the tool manager and the main surver
  will use the tool manager to setup all of the tools

"""

from mcp.types import Tool, TextContent
from cli_tool import CommandLineInterfaceTool

#CommandLineTool = CommandLineInterfaceTool()

class ToolManager:

  # Initialize all of the tools here...
  def __init__(self):
    self._tool_list = [
      CommandLineInterfaceTool()
    ]

  def export_tools(self) -> list[Tool]:
    expList = []
    for tool in self._tool_list:
      expList.append(tool.get_tool())

    return expList
  
  def call_tool(self, name: str, args: dict) -> list[TextContent]:
    gCall = False
    for tool in self._tool_list:
      if tool.get_tool_name() == name:
        return tool.call_tool(args)
    
    return TextContent(
      type="text",
      text=f"Error: Unknown Tool Name - {name}"
    )
      

