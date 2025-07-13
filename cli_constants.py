"""
- cli_constants.py

- Centralizes constants used repeatedly throughout the application

"""

# Timeout, in seconds, for sending command / receiving response
COMMAND_TIMEOUT = 10

# List of black listed commands that will be prevented from
# being ran
BANNED_LIST = (
  r"rm -rf *",
  r":(){ :|:&};:"
)