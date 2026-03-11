"""
- run_server.py

- Command-line runner for the MCP Command Line Interface Server.
- Provides a simple interface to start and test the server.

"""

import asyncio
import logging
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"

if str(SRC_DIR) not in sys.path:
  sys.path.insert(0, str(SRC_DIR))

from command_line_server import CommandLineServer

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

async def main():
  """
  Main entry point for running the Command Line Interface MCP Server
  """
  
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
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    pass
