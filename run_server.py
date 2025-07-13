"""
- run_server.py

- Command-line runner for the MCP Command Line Interface Server.
- Provides a simple interface to start and test the server.

"""

import asyncio
import sys
import logging
from cli_agent_mcp import CommandLineServer

# Helper to configure the logging capability
def setup_logging(level: str = "INFO"):
  numeric_level = getattr(logging, level.upper(), logging.INFO)
  logging.basicConfig(
  level=numeric_level,
  format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
  handlers=[
    logging.StreamHandler(sys.stderr)
  ]
)
  
# Main asynchronous entry point for running the MCP server
async def main():
  # TODO - eventually add some arg parsing for setting up logging level
  setup_logging("INFO")
  logger = logging.getLogger(__name__)
  
  logger.info("Starting MCP Command Line Interface Server...")
  try:
    server = CommandLineServer(logger)
    await server.run()
  except KeyboardInterrupt:
    logger.info("Server stopped by user...")
  except Exception as e:
    logger.error(f"Server error: {e}")
    sys.exit(1)

if __name__ == "__main__":
  asyncio.run(main())