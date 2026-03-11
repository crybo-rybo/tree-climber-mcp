"""Manage the xonsh subprocess used for tool execution."""

import pexpect

from .config import COMMAND_TIMEOUT, SHELL_PROMPT

class ShellManager:
    """Create and interact with a persistent xonsh shell session."""

    def __init__(self):
        self._xonsh_proc = pexpect.spawn("xonsh", encoding="utf-8")
        self._xonsh_proc.delaybeforesend = 2

    async def flush_buffer(self):
        """Set a predictable prompt and clear the shell buffer."""
        set_prompt = f'$PROMPT = "{SHELL_PROMPT}"'
        self._xonsh_proc.sendline(set_prompt)
        self._xonsh_proc.expect_exact(SHELL_PROMPT)
        while self._xonsh_proc.buffer != "":
            self._xonsh_proc.expect_exact(SHELL_PROMPT)

    async def run_command(self, command: str, cmd_timeout: float = COMMAND_TIMEOUT) -> str:
        """Run a command in xonsh and return its output."""
        self._xonsh_proc.sendline(command)

        try:
            self._xonsh_proc.expect_exact(SHELL_PROMPT, timeout=cmd_timeout)
        except pexpect.exceptions.TIMEOUT:
            return "Timed out waiting for command to run..."
        except pexpect.exceptions.EOF:
            return "Unknown exception caused shell instance to close..."

        output = self._xonsh_proc.before
        lines = output.splitlines(keepends=True)
        if lines and lines[0].strip() == command.strip():
            return "".join(lines[1:])
        return output

    async def get_pwd(self) -> str:
        """Return the current working directory from the xonsh session."""
        self._xonsh_proc.sendline("print($PWD)")
        try:
            self._xonsh_proc.expect_exact(SHELL_PROMPT, timeout=COMMAND_TIMEOUT)
            output = self._xonsh_proc.before
            for line in output.splitlines():
                line = line.strip()
                if line and "print($PWD)" not in line:
                    return line
            return ""
        except Exception:
            return ""

    async def cleanup(self):
        """Close the xonsh shell."""
        self._xonsh_proc.close()
