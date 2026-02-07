import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from command_line_interface_tool import CommandLineInterfaceTool
from mcp.types import TextContent

@pytest.fixture(autouse=True)
def mock_shell_manager_cls():
    with patch("command_line_interface_tool.ShellManager") as mock_cls:
        # return a mock instance when instantiated
        mock_instance = AsyncMock()
        mock_cls.return_value = mock_instance
        yield mock_cls, mock_instance

@pytest.fixture
def cli_tool():
    return CommandLineInterfaceTool()

def test_get_tool(cli_tool):
    tool = cli_tool.get_tool()
    assert tool.name == "command_line_interface_tool"
    assert "bash_command" in tool.inputSchema["properties"]

@pytest.mark.asyncio
async def test_call_tool_missing_arg(cli_tool):
    result = await cli_tool.call_tool({})
    assert len(result) == 1
    assert result[0].type == "text"
    assert "Error: bash_command parameter is required" in result[0].text

@pytest.mark.asyncio
async def test_call_tool_banned_command(cli_tool):
    result = await cli_tool.call_tool({"bash_command": "rm -rf /"})
    assert len(result) == 1
    assert "banned command" in result[0].text

@pytest.mark.asyncio
async def test_call_tool_valid_command(cli_tool, mock_shell_manager_cls):
    mock_cls, mock_instance = mock_shell_manager_cls
    
    # Setup mock return for run_command
    mock_instance.run_command.return_value = "file.txt"
    
    cmd = "ls"
    result = await cli_tool.call_tool({"bash_command": cmd})
    
    # Verify ShellManager was instantiated and used
    mock_cls.assert_called()
    mock_instance.flush_buffer.assert_called() # _get_shell_manager calls flush_buffer
    mock_instance.run_command.assert_called_with(cmd, 10) # default timeout
    
    assert len(result) == 1
    assert result[0].text == "file.txt"

@pytest.mark.asyncio
async def test_call_tool_custom_timeout(cli_tool, mock_shell_manager_cls):
    _, mock_instance = mock_shell_manager_cls
    
    mock_instance.run_command.return_value = "ok"
    
    await cli_tool.call_tool({"bash_command": "echo hi", "timeout": 30})
    
    mock_instance.run_command.assert_called_with("echo hi", 30)

@pytest.mark.asyncio
async def test_cleanup(cli_tool, mock_shell_manager_cls):
    _, mock_instance = mock_shell_manager_cls
    
    # Ensure manager is created
    await cli_tool._get_shell_manager()
    
    await cli_tool.cleanup()
    
    mock_instance.cleanup.assert_called_once()
