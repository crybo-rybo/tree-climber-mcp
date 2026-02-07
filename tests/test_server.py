import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from command_line_server import CommandLineServer
from mcp.types import Tool, TextContent

@pytest.fixture
def mock_dependencies():
    with (patch("command_line_server.Server") as mock_server_cls, 
          patch("command_line_server.CommandLineInterfaceTool") as mock_cli_tool_cls, 
          patch("command_line_server.ReadFileTool") as mock_read_tool_cls,
          patch("command_line_server.WriteFileTool") as mock_write_tool_cls,
          patch("command_line_server.ListDirectoryTool") as mock_list_tool_cls,
          patch("command_line_server.ShellManager") as mock_shell_cls,
          patch("command_line_server.stdio_server") as mock_stdio):
         
        mock_server_instance = MagicMock()
        mock_server_cls.return_value = mock_server_instance
        
        # Mock decorators
        def fake_decorator():
            def wrapper(func):
                return func
            return wrapper
        
        mock_server_instance.list_tools.side_effect = fake_decorator
        mock_server_instance.call_tool.side_effect = fake_decorator
        
        mock_shell_instance = AsyncMock()
        mock_shell_cls.return_value = mock_shell_instance

        # Setup mock tools
        mocks = {
            "cli": mock_cli_tool_cls,
            "read": mock_read_tool_cls,
            "write": mock_write_tool_cls,
            "list": mock_list_tool_cls,
            "server": mock_server_instance,
            "shell": mock_shell_instance,
            "stdio": mock_stdio
        }

        # Ensure tools return valid tool definitions
        for key in ["cli", "read", "write", "list"]:
             tool_instance = MagicMock()
             tool_instance.get_tool.return_value = Tool(name=f"{key}_tool", description="desc", inputSchema={})
             # Make call_tool async
             tool_instance.call_tool = AsyncMock()
             mocks[key].return_value = tool_instance

        yield mocks

@pytest.fixture
def server(mock_dependencies):
    logger = MagicMock()
    return CommandLineServer(logger)

def test_init(server, mock_dependencies):
    mocks = mock_dependencies
    
    # Check ShellManager created
    assert server._shell_manager == mocks["shell"]
    
    # Check tools registered
    assert len(server._tools) == 4
    assert "cli_tool" in server._tools
    assert "read_tool" in server._tools
    assert "write_tool" in server._tools
    assert "list_tool" in server._tools

@pytest.mark.asyncio
async def test_cleanup(server, mock_dependencies):
    mocks = mock_dependencies
    
    await server._cleanup()
    
    mocks["shell"].cleanup.assert_called_once()
    
@pytest.mark.asyncio
async def test_run_success(server, mock_dependencies):
    mocks = mock_dependencies
    mock_server = mocks["server"]
    mock_stdio = mocks["stdio"]
    
    # Mock stdio context manager
    mock_read = AsyncMock()
    mock_write = AsyncMock()
    mock_stdio.return_value.__aenter__.return_value = (mock_read, mock_write)
    
    mock_server.run = AsyncMock()
    mock_server.get_capabilities.return_value = {"tools": {}}
    
    await server.run()
    
    # Verify flush_buffer called
    mocks["shell"].flush_buffer.assert_called_once()
    
    mock_server.run.assert_called()
    
    # Cleanup verification
    mocks["shell"].cleanup.assert_called()