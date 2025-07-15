#
# File Name: run_tests.py
#
# Description: Entry point for CLI MCP server unit testing
#

import asyncio
from shell_manager import ShellManager

async def main():
  testShell = ShellManager()
  await testShell.initialize_shell()
  output = await testShell.run_command("ls")
  output = await testShell.run_command("pwd")
  output = await testShell.run_command("cd ..")
  output = await testShell.run_command("pwd")
  await testShell.cleanup()

if __name__ == "__main__":
  asyncio.run(main())