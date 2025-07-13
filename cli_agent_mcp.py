"""
- cli_agent_mcp.py

1. Manages the main MCP server
2. Registers the Tools
3. Sets up MCP server handlers

"""

import asyncio
import typing
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
  Tool,
  TextContent
)

# Class that handles the main MCP server management
class CommandLineServer:
  
  def __init__(self):
    self.server = Server("command-line-server")
    self.input_handler = 0
    self.command_runner = 0
    