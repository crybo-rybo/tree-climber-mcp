# Tree Climber MCP

Tree Climber MCP is a Model Context Protocol (MCP) server that provides an AI model with the capability to execute bash commands within a `xonsh` shell environment.

## Project Overview

- **Purpose:** Enables LLMs to interact with the local file system and execute shell commands safely.
- **Main Technologies:** 
  - **Python (>=3.12):** Core language.
  - **MCP (Model Context Protocol):** Standardized protocol for AI-server communication.
  - **xonsh:** A Python-powered shell used for command execution.
  - **pexpect:** Used to automate and interact with the `xonsh` shell process.
- **Architecture:**
  - `CommandLineServer`: The main MCP server implementation.
  - `CommandLineInterfaceTool`: The tool exposed to the AI model.
  - `ShellManager`: Manages the lifecycle and interaction with the `xonsh` shell.
  - `server_constants.py`: Contains configuration like timeouts and banned commands.

## Building and Running

### Prerequisites
- Python 3.12 or higher.
- `xonsh` must be installed on the system.

### Setup
This project uses `uv` for dependency management.
```bash
uv sync
```

### Running the Server
The server communicates via `stdio`.
```bash
python run_server.py
```

### Testing
A basic test script is provided to verify shell interaction.
```bash
python run_tests.py
```

## Development Conventions

- **Asynchronous Code:** The project relies heavily on `asyncio` for non-blocking I/O and shell interactions.
- **Safety & Security:** A comprehensive list of `BANNED_COMMANDS` in `server_constants.py` prevents the execution of potentially destructive commands (e.g., `rm -rf /`, privilege escalation, etc.).
- **Shell Environment:** The server specifically uses `xonsh`, which combines Python and shell syntax.
- **Logging:** Configurable logging is implemented in `run_server.py` and used throughout the server components.
