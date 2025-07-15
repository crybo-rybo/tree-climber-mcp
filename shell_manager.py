'''
Manages instances of the bash shells, as well as executing user commands
'''

import pexpect
import asyncio
import re

# Define common xonsh prompts. Xonsh's default prompt is quite distinctive.
# It often looks like: user@host:/path>
# or just '@ '
# We'll try to capture common patterns, including newlines.
# pexpect often translates \n to \r\n, so we'll look for both.
xonshPromptPatterns = [
    r'.*@\s',     # Matches typical xonsh prompt ending with '> '
    r'.*[$#]\s',  # Fallback for more bash-like prompts if xonsh is configured differently
    r'.*\r?\n',   # Matches any line ending with \n or \r\n
    pexpect.EOF,
    pexpect.TIMEOUT
]

class ShellManager:
   
  def __init__(self):
    self._xonsh_proc = None

  async def initialize_shell(self):
    self._xonsh_proc = pexpect.spawn('xonsh --no-rc', encoding='utf-8')

    # Flush the initial xonsh welcome message from child process
    try:
      self._xonsh_proc.expect(r'.*@', timeout=25)
    except pexpect.exceptions.TIMEOUT:
      print(f"Timeout waiting for welcome message: {self._xonsh_proc.before}")
    except pexpect.exceptions.EOF:
      print("EOF File Error when initializing...")

  async def run_command(self, command: str, cmd_timeout: float = 10) -> str:
    # TODO - add some sanity checking for "blacklisted" commands

    # Send the command to the xonsh process
    self._xonsh_proc.sendline(command)

    # xonsh will echo the command so just read output until AFTER the command
    try:
      self._xonsh_proc.expect(re.escape(command) + r'\r?\n', timeout=cmd_timeout)
    except pexpect.exceptions.TIMEOUT:
      # do nothing
      pass
    except pexpect.exceptions.EOF:
      # failed for some reason
      return "Unknown exception caused shell instance to close..."
    
    # Next - get the output of the command
    try:
      self._xonsh_proc.expect(xonshPromptPatterns, timeout=cmd_timeout)
    except pexpect.exceptions.TIMEOUT:
      return "Timed out waiting for xonsh response to command..."
    except pexpect.exceptions.EOF:
      return "Unknown exception caused shell instance to close..."
    
    # Get the text "after" any of the matched patterns...
    print(f"Xonsh Process Command Output: {self._xonsh_proc.after}")
    retVal = self._xonsh_proc.after

    # Seek to the end of post-command output
    try:
      self._xonsh_proc.expect(r'.*@', timeout=25)
    except pexpect.exceptions.TIMEOUT:
      return retVal
    except pexpect.exceptions.EOF:
      return retVal
    
    return retVal

  
  async def cleanup(self):
    self._xonsh_proc.close()