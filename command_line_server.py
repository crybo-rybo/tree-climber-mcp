"""
- command_line_server.py

1. Manages the main MCP server
2. Registers the tools
3. Sets up MCP server handlers

"""

import asyncio
from logging import Logger
from command_line_interface_tool import CommandLineInterfaceTool
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
    self._cli_tool = CommandLineInterfaceTool()
    self._logger = logger

    # Register the MCP request handlers
    self._register_handlers()

  async def _cleanup(self):
    """
    Cleanup resources.
    """
    self._logger.info("Cleaning up cli-server resources...")
    await self._cli_tool.cleanup()

  def _register_handlers(self):
    """
    Register the MCP server handlers.
    """

    @self._server.list_tools()
    async def handle_list_tools() -> list[Tool]:
      """
      List available tools.
      """
      toolList = []
      toolList.append(self._cli_tool.get_tool())
      return toolList
    
    @self._server.call_tool()
    async def handle_call_tool(name: str, args: dict) -> list[TextContent]:
      """
      Handle tool call made by model.
      """
      if name != "command_line_interface_tool":
        raise ValueError(f"Unknown tool: {name}")
      return await self._cli_tool.call_tool(args)
    
  async def run(self):
    """
    Starts the MCP Server.
    """
    self._logger.info("Starting CLI MCP Server...")
    try:
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
