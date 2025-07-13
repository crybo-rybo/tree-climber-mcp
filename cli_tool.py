"""
- cli_tool.py

- This tool takes strings of texts and runs them in a xonsh terminal
  and returns the output

"""

from tool_base import ToolBase
from mcp.types import Tool, TextContent

class CommandLineInterfaceTool(ToolBase):

  def __init__(self):
    super().__init__("cli_tool", [
      Tool(
        name="cli_tool",
        description="Runs the provided bash style command and returns the command output.",
        inputSchema={
          "type": "object",
          "properties": {
            "cmdString": {
              "type": "string",
              "description": "The raw text input including the bash command to run along with any other command arguments."
            }
          },
          "required": ["url"]
        }
      )
    ])

  def _call_tool(self, args: dict) -> list[TextContent]:
    print(f"Tool Call Detected in {self._name}")
    return [TextContent(
      type="text",
      text="This is a stubbed MCP call - to use, finish implementation."
    )]
  