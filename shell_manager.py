'''
Manages instances of the bash shells, as well as executing user commands
'''
import server_constants as Constants
import pexpect
import asyncio
import re

class ShellManager:
  """
  Class used to create and interface with a xonsh shell instance
  """

  def __init__(self):
    self._xonsh_proc = pexpect.spawn('xonsh', encoding='utf-8')
    self._xonsh_proc.delaybeforesend = 2

  async def flush_buffer(self):
    """
    Set the xonsh prompt to a predictible token and flush everything from processes output buffer
    """
    setPrompt = f'$PROMPT = "{Constants.SHELL_PROMPT}"'
    self._xonsh_proc.sendline(setPrompt)
    self._xonsh_proc.expect_exact(Constants.SHELL_PROMPT)
    while self._xonsh_proc.buffer != "":
      self._xonsh_proc.expect_exact(Constants.SHELL_PROMPT)

  async def run_command(self, command: str, cmd_timeout: float = Constants.COMMAND_TIMEOUT) -> str:
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
      self._xonsh_proc.expect_exact(Constants.SHELL_PROMPT, timeout=cmd_timeout)
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