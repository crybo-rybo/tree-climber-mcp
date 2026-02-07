"""
- command_line_interface_tool.py

- This tool takes strings of texts and runs them in a xonsh terminal
  and returns the output

"""

from shell_manager import ShellManager
from mcp.types import Tool, TextContent
import server_constants as Constants
import re

class CommandLineInterfaceTool():

  def __init__(self, shell_manager: ShellManager):
    self._tool_obj = Tool(
      name="command_line_interface_tool",
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
    self._shell_manager = shell_manager

  def get_tool(self) -> Tool:
    """
    Method that returns the CommandLineInterfaceTool object that is used
    for MCP server initialization.

    Returns:
      mcp.types.Tool object defined with CommandLineInterfaceTool attributes
    """
    return self._tool_obj
  

  async def call_tool(self, args: dict) -> list[TextContent]:
    """
    Method that handles a call to the command_line_interface_tool

    Returns:
      List - should only be single entry - containing the output from the
      ran bash command.
    """

    # Evaluate tool call arguements
    cmd = args.get("bash_command")
    timeout = args.get("timeout", Constants.COMMAND_TIMEOUT)
    if not cmd:
      return [TextContent(
        type="text",
        text="Error: bash_command parameter is required"
      )]
    
    # Verify that the command is permitted
    if await self._is_command_permitted(cmd) == False:
      return [TextContent(
        type="text",
        text=f"Error: {cmd} is a banned command."
      )]

    # Run the provided command - returned string is the output of the command
    output = await self._shell_manager.run_command(cmd, timeout)

    return [TextContent(
      type="text",
      text=output
    )]
  
  async def _is_command_permitted(self, command: str) -> bool:
    """
    This will check the received command against the list of banned commands.

    Args:
      command (str): The command to check

    Returns:
      bool: True if the command is permitted
    """

    # Normalize the command for checking
    normalized_cmd = ' '.join(command.strip().split()).lower()

    # Check all banned command patterns
    for banned_cmd in Constants.BANNED_COMMANDS:
      if(re.search(banned_cmd, normalized_cmd, re.IGNORECASE)):
        return False
    
    return True