'''
Manages instances of the bash shells, as well as executing user commands
'''

import pexpect
import sys

def interactive_shell_session():
  # Start the bash child process
  child = pexpect.spawn('/bin/bash', encoding='utf-8')

  print("Starting interactive shell session - type 'exit' to quit.")

  # Handle exceptions from pexpect
  try:
    while True:
      command = input("$ ")
      if command.lower() == 'exit':
        break

      # Send the command to the bash process
      child.sendline(command)

      # Catch EOF and Timeout exceptions
      child.expect(['\n$', pexpect.EOF, pexpect.TIMEOUT], timeout=10)

      # Print the output received from the shell
      print(child.before, end='')
  # Handle exceptions
  except pexpect.exceptions.EOF:
    print("\nShell exited unexpectedly (EOF).")
  except pexpect.exceptions.TIMEOUT:
    print("\nTimeout waiting for shell response.")
  except Exception as e:
    print(f"\nAn error occured: {e}")
  finally:
    child.close()
    print(f"Shell process exited with status: {child.exitstatus}, signal status: {child.signalstatus}")