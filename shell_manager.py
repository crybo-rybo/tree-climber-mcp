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

  def __init__(self):
    self._xonsh_proc = pexpect.spawn('xonsh', encoding='utf-8')
    self._xonsh_proc.delaybeforesend = 2

  async def flush_buffer(self):
    # Set the xonsh prompt to something that we can easily delim
    setPrompt = f'$PROMPT = "{xonshPrompt}"'
    self._xonsh_proc.sendline(setPrompt)
    self._xonsh_proc.expect_exact(setPrompt)
    #self._log_buffer()
    self._xonsh_proc.expect_exact(setPrompt)
    #self._log_buffer()
    self._xonsh_proc.expect_exact(xonshPrompt)
    #self._log_buffer()

  async def run_command(self, command: str, cmd_timeout: float = 2) -> str:
    # Send the command to the xonsh process
    self._xonsh_proc.sendline(command)

    # xonsh will echo commands - read buffer until command is found
    # anything after should be command output...?
    try:
      self._xonsh_proc.expect(re.escape(command) + r'\r?\n', timeout=cmd_timeout)
      self._xonsh_proc.expect(re.escape(command) + r'\r?\n', timeout=cmd_timeout)
      self._xonsh_proc.expect_exact(xonshPrompt, timeout=cmd_timeout)
    except pexpect.exceptions.TIMEOUT:
      pass
    except pexpect.exceptions.EOF:
      return "Unknown exception caused shell instance to close..."
    
    outString = self._xonsh_proc.before
    findStr = outString.find(xonshPrompt)
    if findStr:
      return outString.split(xonshPrompt)[0]
    else:
      return outString

  
  async def cleanup(self):
    self._xonsh_proc.close() 

  def _log_buffer(self):
    print(f"Before - {self._xonsh_proc.before}")
    print(f"After - {self._xonsh_proc.after}")