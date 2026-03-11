import re

from mcp.types import TextContent, Tool

from ..config import COMMAND_TIMEOUT
from ..security import BANNED_COMMAND_PATTERNS
from ..shell import ShellManager

class CommandTool:
    """Validate and run shell commands through the managed xonsh session."""

    def __init__(self, shell_manager: ShellManager):
        self._tool_obj = Tool(
            name="command_line_interface_tool",
            description="Runs a provided bash command in an xonsh shell instance.",
            inputSchema={
                "type": "object",
                "properties": {
                    "bash_command": {
                        "type": "string",
                        "description": "The complete bash command to run in the xonsh shell.",
                    },
                    "timeout": {
                        "type": "number",
                        "description": "Optional timeout in seconds (default: 10)",
                        "default": 10,
                        "minimum": 1,
                        "maximum": 60,
                    },
                },
                "required": ["bash_command"],
            },
        )
        self._shell_manager = shell_manager

    def get_tool(self) -> Tool:
        return self._tool_obj

    async def call_tool(self, args: dict) -> list[TextContent]:
        cmd = args.get("bash_command")
        timeout = args.get("timeout", COMMAND_TIMEOUT)
        if not cmd:
            return [TextContent(type="text", text="Error: bash_command parameter is required")]

        if await self._is_command_permitted(cmd) is False:
            return [TextContent(type="text", text=f"Error: {cmd} is a banned command.")]

        output = await self._shell_manager.run_command(cmd, timeout)
        return [TextContent(type="text", text=output)]

    async def _is_command_permitted(self, command: str) -> bool:
        normalized_cmd = " ".join(command.strip().split()).lower()
        for banned_cmd in BANNED_COMMAND_PATTERNS:
            if re.search(banned_cmd, normalized_cmd, re.IGNORECASE):
                return False
        return True
