# Tree Climber MCP

Tree Climber MCP is a Model Context Protocol (MCP) server that empowers AI models to safely interact with a local `xonsh` shell environment. It provides a controlled interface for executing bash commands, enabling LLMs to navigate directories, read files, and perform system operations within defined safety boundaries.

## Features

- **MCP Compliant:** Implements the Model Context Protocol to seamlessly integrate with MCP clients (like Claude Desktop or other AI agents).
- **Safe Shell Execution:** Uses `xonsh` (a Python-powered shell) for command execution.
- **Security First:** Includes a robust list of banned commands (e.g., `rm -rf /`, `sudo`, `ssh-keygen`) to prevent accidental or malicious system damage.
- **Asynchronous Architecture:** Built with `asyncio` for non-blocking performance.
- **Extensive Testing:** Includes a comprehensive unit test suite ensuring reliability and safety.

## Prerequisites

- **Python 3.12+**
- **xonsh**: Must be installed on your system (`pip install xonsh`).
- **uv**: Recommended for dependency management.

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd tree-climber-mcp
    ```

2.  **Install dependencies:**
    This project uses `uv` for package management.
    ```bash
    uv sync
    ```

## Usage

### Running the Server

The server typically runs as a subprocess communicating via `stdio`. To start it manually (e.g., for debugging):

```bash
uv run python run_server.py
```

### Integrating with MCP Clients

To use this with an MCP client (like Claude Desktop), configure your client to run the server script.

**Example `claude_desktop_config.json`:**

```json
{
  "mcpServers": {
    "tree-climber": {
      "command": "/path/to/uv",
      "args": [
        "run",
        "python",
        "/absolute/path/to/tree-climber-mcp/run_server.py"
      ]
    }
  }
}
```

## Security

Tree Climber MCP is designed to be safe. It enforces a blocklist of dangerous commands in `server_constants.py`. blocked categories include:

- **System Destruction:** `rm -rf /`, formatting disks.
- **Privilege Escalation:** `sudo`, `su`.
- **Remote Access:** `ssh`, `curl | bash`.
- **Resource Exhaustion:** Fork bombs.

**Note:** While significant safeguards are in place, always proceed with caution when granting an AI agent access to your terminal.

## Development

### Running Tests

This project uses `pytest` for unit testing. The test suite covers command validation, shell interaction, and server logic.

```bash
uv run pytest
```

### Project Structure

- `command_line_server.py`: Main MCP server entry point.
- `command_line_interface_tool.py`: Defines the "tool" exposed to the LLM.
- `shell_manager.py`: Handles low-level interaction with the `xonsh` subprocess.
- `server_constants.py`: Configuration and banned command definitions.
