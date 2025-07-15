"""
- test_shell_manager.py

- Unit tests for xonsh shell interaction
"""

import unittest
import asyncio
from unittest.mock import patch
from shell_manager import ShellManager

class TestShellManager(unittest.TestCase):

  def setUp(self):
    self._shell_manager = ShellManager()

  def tearDown(self):
    try:
      asyncio.run(self._shell_manager.cleanup())
    except Exception as e:
      print(f"Error during test cleanup: {e}")

  # Just some debugging tests
  def test_pwd_command(self):
    print("Running 'ls' command...\n")
    print(self._shell_manager.run_command("ls", 25))
    self.assertTrue(True)