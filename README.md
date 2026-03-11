<p align="center">
  <img src="docs/images/tree_climber_logo.png" alt="Tree Climber MCP logo" width="220">
</p>

<h1 align="center">Tree Climber MCP</h1>

<p align="center">
  <b>Safely connect AI models to a local shell environment.</b><br/>
  <sub>xonsh-powered &bull; Secure command execution &bull; MCP compliant</sub>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.12%2B-blue" alt="Python 3.12+" />
  <img src="https://img.shields.io/badge/tests-pytest-success" alt="Tests" />
  <img src="https://img.shields.io/badge/build-uv-purple" alt="uv build" />
</p>

## About

Tree Climber MCP is a Model Context Protocol (MCP) server that lets AI models interact with a local `xonsh` shell and a small set of filesystem helpers. Shell commands are filtered through a blocklist, and filesystem operations are limited to the shell's current working directory tree.

## Features

- **MCP Compliant:** Implements the Model Context Protocol to seamlessly integrate with MCP clients (like Claude Desktop or other AI agents).
- **Safe Shell Execution:** Uses `xonsh` (a Python-powered shell) for command execution.
- **Filesystem Helpers:** Exposes `read_file`, `write_file`, and `list_directory` alongside the shell tool.
- **Security First:** Blocks dangerous shell commands (for example `rm -rf /`, `sudo bash`, and `curl ... | bash`) and restricts filesystem access to the active working directory.
- **Async Server Interface:** Uses `asyncio` for MCP request handling and lifecycle management.
- **Extensive Testing:** Includes a comprehensive unit test suite ensuring reliability and safety.

## Prerequisites

- **Python 3.12+**
- **uv**: Recommended for dependency management.
- `uv sync` installs the Python dependencies, including `xonsh`, into the project environment.

## Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/crybo-rybo/tree-climber-mcp.git
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

Tree Climber MCP applies two safety layers:

- Shell commands are checked against the `BANNED_COMMANDS` regex list in `src/server_constants.py`.
- Filesystem tools only operate inside the shell's current working directory tree.

Blocked shell categories include:

- **System Destruction:** `rm -rf /`, formatting disks.
- **Privilege Escalation:** `sudo bash`, system shutdown commands.
- **Remote Code Execution:** `curl | bash`, `wget | sh`.
- **Resource Exhaustion / Scanning:** Fork bombs, `masscan`, `nmap`.

**Note:** While significant safeguards are in place, always proceed with caution when granting an AI agent access to your terminal.

## Development

### Running Tests

This project uses `pytest` for unit testing. The test suite covers command validation, shell interaction, and server logic.

```bash
uv run pytest
```

### Project Structure

- `run_server.py`: local runner that bootstraps `src/` and starts the MCP server.
- `src/command_line_server.py`: registers the shell and filesystem tools with the MCP server.
- `src/command_line_interface_tool.py`: validates and runs shell commands.
- `src/filesystem_tools.py`: implements `list_directory`, `read_file`, and `write_file`.
- `src/shell_manager.py`: manages the persistent `xonsh` subprocess.
- `src/server_constants.py`: shell prompt, timeout, and blocked-command definitions.
- `tests/`: pytest coverage for server, shell manager, constants, and filesystem tools.
