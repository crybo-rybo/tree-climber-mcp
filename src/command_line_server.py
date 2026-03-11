"""
- command_line_server.py

1. Manages the main MCP server
2. Registers the tools
3. Sets up MCP server handlers

"""

import asyncio
from logging import Logger
from command_line_interface_tool import CommandLineInterfaceTool
from filesystem_tools import ReadFileTool, WriteFileTool, ListDirectoryTool
from shell_manager import ShellManager
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
  Tool,
  TextContent
)

class CommandLineServer:
  """
  This class manages creating the MCP Server for the Command Line Interface tool.
  """
  
  def __init__(self, logger: Logger):
    self._server = Server("cli-server")
    self._logger = logger
    self._shell_manager = ShellManager()
    
    # Initialize tools with the shell manager
    self._tools = {}
    self._register_tool(CommandLineInterfaceTool(self._shell_manager))
    self._register_tool(ReadFileTool(self._shell_manager))
    self._register_tool(WriteFileTool(self._shell_manager))
    self._register_tool(ListDirectoryTool(self._shell_manager))

    # Register the MCP request handlers
    self._register_handlers()

  def _register_tool(self, tool_instance):
      self._tools[tool_instance.get_tool().name] = tool_instance

  async def _cleanup(self):
    """
    Cleanup resources.
    """
    self._logger.info("Cleaning up cli-server resources...")
    if self._shell_manager:
        await self._shell_manager.cleanup()

  def _register_handlers(self):
    """
    Register the MCP server handlers.
    """

    @self._server.list_tools()
    async def handle_list_tools() -> list[Tool]:
      """
      List available tools.
      """
      return [t.get_tool() for t in self._tools.values()]
    
    @self._server.call_tool()
    async def handle_call_tool(name: str, args: dict) -> list[TextContent]:
      """
      Handle tool call made by model.
      """
      tool = self._tools.get(name)
      if not tool:
        raise ValueError(f"Unknown tool: {name}")
      return await tool.call_tool(args)
    
  async def run(self):
    """
    Starts the MCP Server.
    """
    self._logger.info("Starting CLI MCP Server...")
    try:
      # Initialize shell manager
      await self._shell_manager.flush_buffer()

      self._logger.info("Setting up stdio server...")
      async with stdio_server() as (read_stream, write_stream):
        # Configure the server options
        init_options = InitializationOptions(
          server_name="cli-server",
          server_version="0.0.1",
          capabilities=self._server.get_capabilities(
            notification_options=self._server.notification_options,
            experimental_capabilities=None
          )
        )

        # Start the server now
        self._logger.info("Running server now...")
        await self._server.run(
          read_stream,
          write_stream,
          init_options
        )
    except Exception as e:
      self._logger.error(f"Failed to start MCP server: {e}")
      self._logger.exception("Full stack trace:")
      raise
    finally:
      # Cleanup server
      self._logger.info("Cleaning up resources...")
      await self._cleanup()
      self._logger.info("Cleanup complete!")