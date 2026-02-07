import os
import asyncio
from mcp.types import Tool, TextContent
from shell_manager import ShellManager

class BaseFilesystemTool:
    def __init__(self, shell_manager: ShellManager):
        self._shell_manager = shell_manager

    async def _resolve_path(self, path: str) -> str:
        """
        Resolves the given path against the shell's current working directory.
        """
        if os.path.isabs(path):
            return path
        
        cwd = await self._shell_manager.get_pwd()
        if not cwd:
            # Fallback to python's cwd if shell fails (unlikely)
            return os.path.abspath(path)
            
        return os.path.join(cwd, path)

class ListDirectoryTool(BaseFilesystemTool):
    def get_tool(self) -> Tool:
        return Tool(
            name="list_directory",
            description="Lists the files and subdirectories in the specified directory.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The directory path to list. Defaults to current directory if omitted."
                    }
                }
            }
        )

    async def call_tool(self, args: dict) -> list[TextContent]:
        path = args.get("path", ".")
        try:
            target_path = await self._resolve_path(path)
            
            if not os.path.exists(target_path):
                return [TextContent(type="text", text=f"Error: Directory '{path}' does not exist.")]
            if not os.path.isdir(target_path):
                 return [TextContent(type="text", text=f"Error: '{path}' is not a directory.")]

            items = os.listdir(target_path)
            # Add type indicator (directory/)
            formatted_items = []
            for item in items:
                if os.path.isdir(os.path.join(target_path, item)):
                    formatted_items.append(f"{item}/")
                else:
                    formatted_items.append(item)
            
            return [TextContent(type="text", text="\n".join(sorted(formatted_items)))]
        except Exception as e:
            return [TextContent(type="text", text=f"Error listing directory: {str(e)}")]

class ReadFileTool(BaseFilesystemTool):
    def get_tool(self) -> Tool:
        return Tool(
            name="read_file",
            description="Reads the contents of a file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file to read."
                    }
                },
                "required": ["path"]
            }
        )

    async def call_tool(self, args: dict) -> list[TextContent]:
        path = args.get("path")
        if not path:
             return [TextContent(type="text", text="Error: 'path' argument is required.")]

        try:
            target_path = await self._resolve_path(path)
            
            if not os.path.exists(target_path):
                 return [TextContent(type="text", text=f"Error: File '{path}' does not exist.")]
            if not os.path.isfile(target_path):
                 return [TextContent(type="text", text=f"Error: '{path}' is not a file.")]

            # TODO: Add safety check against reading sensitive system files if needed, 
            # though the user permission model applies.

            with open(target_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return [TextContent(type="text", text=content)]
        except Exception as e:
            return [TextContent(type="text", text=f"Error reading file: {str(e)}")]

class WriteFileTool(BaseFilesystemTool):
    def get_tool(self) -> Tool:
        return Tool(
            name="write_file",
            description="Writes content to a file. Overwrites existing files.",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file to write."
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write to the file."
                    }
                },
                "required": ["path", "content"]
            }
        )

    async def call_tool(self, args: dict) -> list[TextContent]:
        path = args.get("path")
        content = args.get("content")
        
        if not path:
             return [TextContent(type="text", text="Error: 'path' argument is required.")]
        if content is None:
             return [TextContent(type="text", text="Error: 'content' argument is required.")]

        try:
            target_path = await self._resolve_path(path)
            
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return [TextContent(type="text", text=f"Successfully wrote to '{path}'.")]
        except Exception as e:
             return [TextContent(type="text", text=f"Error writing file: {str(e)}")]
