"""
- cli_tool.py

- This tool takes strings of texts and runs them in a xonsh terminal
  and returns the output

"""

from tool_base import ToolBase
from shell_manager import ShellManager
from mcp.types import Tool, TextContent

class CommandLineInterfaceTool(ToolBase):

  def __init__(self):
    super().__init__("cli_tool", Tool(
      name="cli_tool",
      description="Runs a provided bash command in an xonsh shell instance.",
      inputSchema={
        "type": "object",
        "properties": {
          "bash_command": {
            "type": "string",
            "description": "The complete bash command to run in the xonsh shell."
          },
          "timeout": {
            "type": "number",
            "description": "Optional timeout in seconds (default: 10)",
            "default": 10,
            "minimum": 1,
            "maximum": 60
          }
        },
        "required": ["bash_command"]
      }
    )
    )

    # ShellManager class manages initializing Xonsh sub-process as well as IO to that process
    self._shell_manager = ShellManager()

  def call_tool(self, args: dict) -> list[TextContent]:
    print(f"Tool Call Detected in {self._name}")
    return [TextContent(
      type="text",
      text="This is a stubbed MCP call - to use, finish implementation."
    )]
  
  def cleanup(self):
    self._name = ""
    self._tool_obj = 0
    self._shell_manager.cleanup()