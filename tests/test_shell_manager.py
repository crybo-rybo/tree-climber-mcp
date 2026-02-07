import pytest
import asyncio
from unittest.mock import MagicMock, patch
from shell_manager import ShellManager
import server_constants as Constants
import pexpect

@pytest.fixture
def mock_pexpect_spawn():
    with patch("pexpect.spawn") as mock_spawn:
        yield mock_spawn

@pytest.fixture
def shell_manager(mock_pexpect_spawn):
    # Setup the mock process instance returned by spawn
    mock_proc = MagicMock()
    mock_pexpect_spawn.return_value = mock_proc
    
    # Initialize manager
    manager = ShellManager()
    return manager, mock_proc

@pytest.mark.asyncio
async def test_init(shell_manager):
    manager, mock_proc = shell_manager
    assert manager._xonsh_proc == mock_proc
    assert mock_proc.delaybeforesend == 2

@pytest.mark.asyncio
async def test_flush_buffer(shell_manager):
    manager, mock_proc = shell_manager
    
    # Configure mock to simulate buffer behavior
    # First call to buffer returns "some output", second returns "" (empty)
    type(mock_proc).buffer = PropertyMock(side_effect=["some output", ""])
    
    await manager.flush_buffer()
    
    # Verify prompt was set
    expected_set_prompt = f'$PROMPT = "{Constants.SHELL_PROMPT}"'
    mock_proc.sendline.assert_called_with(expected_set_prompt)
    
    # Verify we waited for prompt
    assert mock_proc.expect_exact.call_count >= 1
    mock_proc.expect_exact.assert_called_with(Constants.SHELL_PROMPT)

from unittest.mock import PropertyMock

@pytest.mark.asyncio
async def test_run_command_success(shell_manager):
    manager, mock_proc = shell_manager
    
    cmd = "echo hello"
    expected_output = "hello\\n"
    
    # Mock the 'before' attribute to simulate output capture
    # typically run_command searches for cmd in output. 
    # Logic: 
    # output = self._xonsh_proc.before
    # match = re.search(command, output)
    # if match: return output[match.end():]
    
    # We need to simulate the echo back of the command + the output
    full_output = f"{cmd}\\n{expected_output}"
    type(mock_proc).before = PropertyMock(return_value=full_output)
    
    result = await manager.run_command(cmd)
    
    mock_proc.sendline.assert_called_with(cmd)
    mock_proc.expect_exact.assert_called_with(Constants.SHELL_PROMPT, timeout=Constants.COMMAND_TIMEOUT)
    
    # The current implementation strips the command from the output using regex
    # So we expect just the output part. 
    # If full_output is "echo hello\nhello\n", regex matches "echo hello", remaining is "\nhello\n"
    assert result == "\\n" + expected_output

@pytest.mark.asyncio
async def test_run_command_timeout(shell_manager):
    manager, mock_proc = shell_manager
    
    cmd = "sleep 100"
    
    # Simulate TIMEOUT exception
    mock_proc.expect_exact.side_effect = pexpect.exceptions.TIMEOUT("Timeout")
    
    result = await manager.run_command(cmd)
    
    assert result == "Timed out waiting for command to run..."

@pytest.mark.asyncio
async def test_cleanup(shell_manager):
    manager, mock_proc = shell_manager
    await manager.cleanup()
    mock_proc.close.assert_called_once()

@pytest.mark.asyncio
async def test_get_pwd(shell_manager):
    manager, mock_proc = shell_manager
    
    # Mock output: command echo + newline + path + newline
    # The parsing logic splits lines and ignores the command line.
    mock_output = "print($PWD)\r\n/users/test/dir\r\n"
    type(mock_proc).before = PropertyMock(return_value=mock_output)
    
    pwd = await manager.get_pwd()
    
    mock_proc.sendline.assert_called_with("print($PWD)")
    mock_proc.expect_exact.assert_called_with(Constants.SHELL_PROMPT, timeout=Constants.COMMAND_TIMEOUT)
    
    assert pwd == "/users/test/dir"

@pytest.mark.asyncio
async def test_get_pwd_error(shell_manager):
    manager, mock_proc = shell_manager
    
    # Simulate exception during expect
    mock_proc.expect_exact.side_effect = Exception("Boom")
    
    pwd = await manager.get_pwd()
    assert pwd == ""

