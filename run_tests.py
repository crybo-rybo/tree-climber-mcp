#
# File Name: run_tests.py
#
# Description: Entry point for CLI MCP server unit testing
#

import asyncio
import pexpect
from shell_manager import ShellManager

async def main1():
  
  child = pexpect.spawn('xonsh')
  child.interact() 

async def main():
  testShell = ShellManager()
  await testShell.flush_buffer()
  output = await testShell.run_command("ls")
  print(f"Ran 'ls' command:\n{output}")
  output = await testShell.run_command("pwd")
  print(f"Ran 'pwd' command:\n{output}")
  output = await testShell.run_command("cd ..")
  print(f"Ran 'cd ..' command:\n{output}")
  output = await testShell.run_command("pwd")
  print(f"Ran 'pwd' command:\n{output}")
  await testShell.cleanup()


if __name__ == "__main__":
  asyncio.run(main())