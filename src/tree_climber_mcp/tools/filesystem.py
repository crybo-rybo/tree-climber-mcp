import os
from mcp.types import Tool, TextContent

from ..shell import ShellManager

class BaseFilesystemTool:
    def __init__(
        self,
        shell_manager: ShellManager,
        allow_all_paths: bool = False,
        filesystem_root: str | None = None,
    ):
        self._shell_manager = shell_manager
        self._allow_all_paths = allow_all_paths
        self._filesystem_root = filesystem_root

    async def _get_working_directory(self) -> str:
        cwd = await self._shell_manager.get_pwd()
        if not cwd:
            return os.getcwd()
        return cwd

    async def _get_trusted_root(self) -> str:
        if self._filesystem_root:
            return os.path.realpath(self._filesystem_root)
        return os.path.realpath(await self._get_working_directory())

    async def _resolve_path(self, path: str) -> str:
        """
        Resolves the given path against the shell's current working directory and
        rejects paths outside that working tree.
        """
        working_directory = os.path.realpath(await self._get_working_directory())
        candidate_path = path if os.path.isabs(path) else os.path.join(working_directory, path)
        target_path = os.path.realpath(candidate_path)

        if self._allow_all_paths:
            return target_path

        trusted_root = await self._get_trusted_root()
        try:
            if os.path.commonpath([trusted_root, target_path]) != trusted_root:
                raise PermissionError(path)
        except ValueError as exc:
            raise PermissionError(path) from exc

        return target_path

    def _access_error(self, path: str) -> list[TextContent]:
        scope = "allowed filesystem root" if self._filesystem_root else "current working directory"
        return [
            TextContent(
                type="text",
                text=f"Error: Access to '{path}' is outside the {scope}."
            )
        ]

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
        except PermissionError:
            return self._access_error(path)

        try:
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
        except PermissionError:
            return self._access_error(path)

        try:
            if not os.path.exists(target_path):
                 return [TextContent(type="text", text=f"Error: File '{path}' does not exist.")]
            if not os.path.isfile(target_path):
                 return [TextContent(type="text", text=f"Error: '{path}' is not a file.")]

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
        except PermissionError:
            return self._access_error(path)

        try:
            # Ensure parent directory exists
            os.makedirs(os.path.dirname(target_path), exist_ok=True)

            with open(target_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return [TextContent(type="text", text=f"Successfully wrote to '{path}'.")]
        except Exception as e:
             return [TextContent(type="text", text=f"Error writing file: {str(e)}")]
