"""
- server_constants.py

- Centralizes constants used repeatedly throughout the application

"""

# Timeout, in seconds, for sending command / receiving response
COMMAND_TIMEOUT = 10

# List of commands server will refuse to run
BANNED_COMMANDS = [
  # System destruction
  r"rm\s+-rf\s+/(\*|$)",  # rm -rf / or rm -rf /*
  r"rm\s+-rf\s+(~|\$HOME)",  # delete home directory
  r"find\s+/.*-delete",  # mass deletion from root
  r"mkfs\.",  # format filesystem
  r"fdisk|parted",  # disk partitioning
  
  # Fork bombs and resource exhaustion
  r":\(\)\{\s*:\|\:\&\s*\}\s*\;:",  # fork bomb
  r"dd\s+if=/dev/zero\s+of=/dev/mem",  # memory bomb
  r"dd\s+if=/dev/zero\s+of=.*bs=.*count=\d{3,}",  # large file creation
  r"while\s+true.*malloc",  # memory exhaustion loop
  
  # Privilege escalation and system control
  r"sudo\s+(su|bash|sh|-i)",  # sudo privilege escalation
  r"(shutdown|reboot|halt|poweroff)",  # system shutdown
  r"killall\s+-9\s+(init|systemd)",  # kill critical processes
  r"killall\s+-9",  # force kill all processes
  r"kill\s+-9\s+-1",  # kill all processes
  r"chmod\s+(\+s|4755)",  # set SUID bit
  r"systemctl\s+(stop|disable)",  # disable system services
  r"service\s+\w+\s+stop",  # stop system services
  
  # Remote code execution
  r"curl.*\|\s*(sh|bash)",  # download and execute
  r"wget.*\|\s*(sh|bash)",  # download and execute
  r"bash\s*<\s*\(",  # bash process substitution execution
  
  # Security compromise
  r"cat\s+/etc/(passwd|shadow)",  # read password files
  r"ssh-keygen.*-f",  # SSH key generation
  r"cp.*\.ssh/authorized_keys",  # SSH key installation
  r"history\s+-c",  # clear command history
  r"unset\s+HISTFILE",  # disable history logging
  r"crontab\s+-[er]",  # edit/remove cron jobs
  
  # Network attacks and scanning
  r"nmap\s+",  # network scanning
  r"nc\s+-l",  # netcat listening
  r"socat.*LISTEN",  # socket listening
  r"masscan|hping3",  # network attack tools
  r"john|hashcat|hydra",  # password cracking tools
  
  # Package management (potentially destructive)
  r"apt-get\s+(remove|purge)",  # package removal
  r"yum\s+remove",  # package removal
  r"pip\s+uninstall",  # Python package removal
  r"npm\s+uninstall\s+-g",  # global npm package removal
  
  # Information gathering
  r"dmidecode|lshw",  # hardware information gathering
]