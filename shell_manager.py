'''
Manages instances of the bash shells, as well as executing user commands
'''

import pexpect
import re

def interactive_xonsh_session():
  # Start the xonsh child process
  print("Spawning xonsh process...")
  # --no-rc prevents welcome message....
  child = pexpect.spawn('xonsh --no-rc', encoding='utf-8')

  # Define common xonsh prompts. Xonsh's default prompt is quite distinctive.
  # It often looks like: user@host:/path>
  # or just '> '
  # We'll try to capture common patterns, including newlines.
  # pexpect often translates \n to \r\n, so we'll look for both.
  xonshPromptPatterns = [
      r'.*>\s',     # Matches typical xonsh prompt ending with '> '
      r'.*[$#@]\s',  # Fallback for more bash-like prompts if xonsh is configured differently
      r'.*\r?\n',   # Matches any line ending with \n or \r\n
      pexpect.EOF,
      pexpect.TIMEOUT
  ]

  atOnlyPattern = [
     r'@\s',
     pexpect.EOF,
     pexpect.TIMEOUT
  ]



  # 2. Flush initial xonsh output and get to the first prompt
  try:
      print("Waiting for initial xonsh prompt...")
      '''
        Just look until the initial @ on the command line to get rid of all the
        welcome message...
      '''
      child.expect(atOnlyPattern, timeout=10)
      print("Initial xonsh prompt received.")
      # The 'before' buffer will contain startup messages. We'll ignore them for now.
      #print(f"D0 - before value: {child.before}\n")
      #print(f"D0 - after value: {child.after}\n")

  except pexpect.exceptions.EOF:
      print("ERROR: xonsh exited immediately after spawning.")
      child.close()
      return
  except pexpect.exceptions.TIMEOUT:
      print("WARNING: Timed out waiting for initial xonsh prompt. Continuing anyway.")
      # If it times out, the 'before' buffer will contain whatever was received.

  print("\nStarting interactive xonsh session. Type 'exit' to quit.")

  # Handle exceptions from pexpect
  try:
    while True:
      # Get user input and send to xonsh
      command = input("@ ")
      if command.lower() == 'exit':
        break
      child.sendline(command)
      
      # Expect xonsh to echo the command
      try:
         child.expect(re.escape(command) + r'\r?\n', timeout=5)
      except pexpect.exceptions.TIMEOUT:
        # do nothing
        pass
      except pexpect.exceptions.EOF:
         # xonsh exited for some reason
         print("\nXonsh exited unexpectedly...")
         break
      print(f"D1 - before value: {child.before}\n")
      print(f"D1 - after value: {child.after}\n")
      
      # Get the output of the command
      try:
         child.expect(xonshPromptPatterns, timeout=10)
      except pexpect.exceptions.TIMEOUT:
         # not end of world - just signal
         print("\nTimed out waiting for xonsh response...\n")
         continue
      except pexpect.exceptions.EOF:
         print("\nExonsh exited unexpectedly...\n")
         break

      # Clean up output a bit
      rawOutput = child.after
      print(rawOutput)

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