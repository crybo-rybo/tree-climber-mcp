import pytest
import os
from unittest.mock import AsyncMock, MagicMock, patch, mock_open
from filesystem_tools import ReadFileTool, WriteFileTool, ListDirectoryTool
from shell_manager import ShellManager
from mcp.types import TextContent

@pytest.fixture
def mock_shell_manager():
    mock = AsyncMock(spec=ShellManager)
    mock.get_pwd.return_value = "/mock/cwd"
    return mock

@pytest.fixture
def list_tool(mock_shell_manager):
    return ListDirectoryTool(mock_shell_manager)

@pytest.fixture
def read_tool(mock_shell_manager):
    return ReadFileTool(mock_shell_manager)

@pytest.fixture
def write_tool(mock_shell_manager):
    return WriteFileTool(mock_shell_manager)

# --- ListDirectoryTool Tests ---

@pytest.mark.asyncio
async def test_list_directory_success(list_tool, mock_shell_manager):
    with (patch("os.path.exists") as mock_exists, 
          patch("os.path.isdir") as mock_isdir, 
          patch("os.listdir") as mock_listdir):
        
        mock_exists.return_value = True
        mock_isdir.return_value = True
        mock_listdir.return_value = ["file1.txt", "dir1"]
        
        # Mock checks for individual items to append '/'
        def isdir_side_effect(path):
            if path.endswith("dir1"): return True
            if path.startswith("/mock/cwd"): return True # target path
            return False
        mock_isdir.side_effect = isdir_side_effect

        result = await list_tool.call_tool({})
        
        assert len(result) == 1
        assert "dir1/" in result[0].text
        assert "file1.txt" in result[0].text
        
        # Verify default path used CWD
        mock_shell_manager.get_pwd.assert_called()

@pytest.mark.asyncio
async def test_list_directory_not_found(list_tool):
    with patch("os.path.exists", return_value=False):
        result = await list_tool.call_tool({"path": "bad_dir"})
        assert "Error: Directory 'bad_dir' does not exist" in result[0].text

# --- ReadFileTool Tests ---

@pytest.mark.asyncio
async def test_read_file_success(read_tool, mock_shell_manager):
    with (patch("os.path.exists", return_value=True), 
          patch("os.path.isfile", return_value=True), 
          patch("builtins.open", mock_open(read_data="content"))):
        
        result = await read_tool.call_tool({"path": "test.txt"})
        
        assert len(result) == 1
        assert result[0].text == "content"
        
        # Check path resolution
        mock_shell_manager.get_pwd.assert_called()

@pytest.mark.asyncio
async def test_read_file_missing_arg(read_tool):
    result = await read_tool.call_tool({})
    assert "Error: 'path' argument is required" in result[0].text

# --- WriteFileTool Tests ---

@pytest.mark.asyncio
async def test_write_file_success(write_tool, mock_shell_manager):
    m_open = mock_open()
    with (patch("os.makedirs"), 
          patch("builtins.open", m_open)):
        
        result = await write_tool.call_tool({"path": "new.txt", "content": "hello"})
        
        assert "Successfully wrote" in result[0].text
        m_open.assert_called()
        handle = m_open()
        handle.write.assert_called_with("hello")

@pytest.mark.asyncio
async def test_write_file_missing_args(write_tool):
    result = await write_tool.call_tool({"path": "foo"})
    assert "Error: 'content' argument is required" in result[0].text