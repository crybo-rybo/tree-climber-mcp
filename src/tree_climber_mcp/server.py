from logging import Logger
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

from .config import SERVER_NAME, SERVER_VERSION
from .shell import ShellManager
from .tools.command import CommandTool
from .tools.filesystem import ListDirectoryTool, ReadFileTool, WriteFileTool

class TreeClimberServer:
    """Create and run the MCP server with the registered tool set."""

    def __init__(self, logger: Logger):
        self._server = Server(SERVER_NAME)
        self._logger = logger
        self._shell_manager = ShellManager()
        self._tools = {}

        self._register_tool(CommandTool(self._shell_manager))
        self._register_tool(ReadFileTool(self._shell_manager))
        self._register_tool(WriteFileTool(self._shell_manager))
        self._register_tool(ListDirectoryTool(self._shell_manager))
        self._register_handlers()

    def _register_tool(self, tool_instance) -> None:
        self._tools[tool_instance.get_tool().name] = tool_instance

    async def _cleanup(self) -> None:
        self._logger.info("Cleaning up server resources...")
        if self._shell_manager:
            await self._shell_manager.cleanup()

    def _register_handlers(self) -> None:
        @self._server.list_tools()
        async def handle_list_tools() -> list[Tool]:
            return [tool.get_tool() for tool in self._tools.values()]

        @self._server.call_tool()
        async def handle_call_tool(name: str, args: dict) -> list[TextContent]:
            tool = self._tools.get(name)
            if not tool:
                raise ValueError(f"Unknown tool: {name}")
            return await tool.call_tool(args)

    async def run(self) -> None:
        self._logger.info("Starting Tree Climber MCP server...")
        try:
            await self._shell_manager.flush_buffer()

            self._logger.info("Setting up stdio server...")
            async with stdio_server() as (read_stream, write_stream):
                init_options = InitializationOptions(
                    server_name=SERVER_NAME,
                    server_version=SERVER_VERSION,
                    capabilities=self._server.get_capabilities(
                        notification_options=self._server.notification_options,
                        experimental_capabilities=None,
                    ),
                )

                self._logger.info("Running server now...")
                await self._server.run(read_stream, write_stream, init_options)
        except Exception as exc:
            self._logger.error("Failed to start MCP server: %s", exc)
            self._logger.exception("Full stack trace:")
            raise
        finally:
            self._logger.info("Cleaning up resources...")
            await self._cleanup()
            self._logger.info("Cleanup complete!")
