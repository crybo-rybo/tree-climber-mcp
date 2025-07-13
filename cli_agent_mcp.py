"""
- cli_agent_mcp.py

1. Manages the main MCP server
2. Registers the Tools
3. Sets up MCP server handlers

"""

import asyncio
from logging import Logger
from tool_manager import ToolManager
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
  Tool,
  TextContent
)

# Class that handles the main MCP server management
class CommandLineServer:
  
  def __init__(self, logger: Logger):
    self._server = Server("cli-server")
    self._tool_manager = ToolManager()
    self._logger = logger

    # Register the MCP request handlers
    self._register_handlers()

  async def _cleanup(self):
    self._logger.info("Cleaning up cli-server resources...")
    # TODO - stuff here if necessary...? Probably something that closes the xonsh session for the CLI tool?

  # Registers the handlers required for MCP server functionality
  def _register_handlers(self):

    @self._server.list_tools()
    async def handle_list_tools() -> list[Tool]:
      return self._tool_manager.export_tools()
    
    @self._server.call_tool()
    async def handle_call_tool(name: str, args: dict) -> list[TextContent]:
      return self._tool_manager.call_tool(name, args)
    
  # Main routine to run the MCP server
  async def run(self):
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

  # Asnyc context manager entry (TODO - get explaination on this API)
  async def __aenter__(self):
    return self
  
  async def __aexit__(self, exc_type, exc_val, exc_tb):
    await self._cleanup()

# Main entry point for the server
async def main():
  server = CommandLineServer()
  try:
    await server.run()
  finally:
    await server._cleanup()

if __name__ == "__main__":
  asyncio.run(main())

