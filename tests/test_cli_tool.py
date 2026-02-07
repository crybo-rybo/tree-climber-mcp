import pytest
from unittest.mock import AsyncMock, MagicMock
from command_line_interface_tool import CommandLineInterfaceTool
from shell_manager import ShellManager
from mcp.types import TextContent

@pytest.fixture
def mock_shell_manager():
    mock = AsyncMock(spec=ShellManager)
    return mock

@pytest.fixture
def cli_tool(mock_shell_manager):
    return CommandLineInterfaceTool(mock_shell_manager)

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
async def test_call_tool_valid_command(cli_tool, mock_shell_manager):
    # Setup mock return for run_command
    mock_shell_manager.run_command.return_value = "file.txt"
    
    cmd = "ls"
    result = await cli_tool.call_tool({"bash_command": cmd})
    
    # Verify ShellManager was used
    mock_shell_manager.run_command.assert_called_with(cmd, 10) # default timeout
    
    assert len(result) == 1
    assert result[0].text == "file.txt"

@pytest.mark.asyncio
async def test_call_tool_custom_timeout(cli_tool, mock_shell_manager):
    mock_shell_manager.run_command.return_value = "ok"
    
    await cli_tool.call_tool({"bash_command": "echo hi", "timeout": 30})
    
    mock_shell_manager.run_command.assert_called_with("echo hi", 30)