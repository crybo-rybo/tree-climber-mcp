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
    r'.*[$#>]\s',  # Fallback for more bash-like prompts if xonsh is configured differently
    r'.*\r?\n',   # Matches any line ending with \n or \r\n
    pexpect.EOF,
    pexpect.TIMEOUT
]

xonshWelcomePatterns = [
    r'.*@\s',
    r'.*\r?\n',
    pexpect.EOF,
    pexpect.TIMEOUT
]

xonshPrompt = "##P##"

class ShellManager:
  """
  Class used to create and interface with a xonsh shell instance
  """

  def __init__(self):
    self._xonsh_proc = pexpect.spawn('xonsh', encoding='utf-8')
    self._xonsh_proc.delaybeforesend = 2

  async def flush_buffer(self):
    """
    Set the xonsh prompt to a predictible token and flush everything from tasks output buffer
    """
    setPrompt = f'$PROMPT = "{xonshPrompt}"'
    self._xonsh_proc.sendline(setPrompt)
    self._xonsh_proc.expect_exact(xonshPrompt)
    while self._xonsh_proc.buffer != "":
      self._xonsh_proc.expect_exact(xonshPrompt)

  async def run_command(self, command: str, cmd_timeout: float = 10) -> str:
    """
    Method that sends a command to the xonsh shell instance and returns the output of the command

    Args:
      command (str)      : Bash command to run in the xonsh shell
      cmd_timeout (float): Time - in seconds - before the xonsh call times out

    Returns:
      str: Output of running the provided command in the xonsh shell
    """
    self._xonsh_proc.sendline(command)

    try:
      # read until the next prompt - which should be AFTER the command output
      self._xonsh_proc.expect_exact(xonshPrompt, timeout=cmd_timeout)
    except pexpect.exceptions.TIMEOUT:
      return "Timed out waiting for command to run..."
    except pexpect.exceptions.EOF:
      return "Unknown exception caused shell instance to close..."
    
    output = self._xonsh_proc.before
    match = re.search(command, output)
    if match:
      return output[match.end():]
    return output

  
  async def cleanup(self):
    """
    Closes the xonsh shell
    """
    self._xonsh_proc.close() 

  def _log_buffer(self):
    """
    Helper method that will log the xonsh buffer
    """
    print(f"Before - {self._xonsh_proc.before}")
    print(f"After - {self._xonsh_proc.after}")