#!/usr/bin/env python3
"""
SSH Connect - Connect to remote machines using credentials from .env
"""

import os
import sys
from pathlib import Path

try:
    import paramiko
except ImportError:
    print("Error: paramiko not installed. Run: pip install paramiko")
    sys.exit(1)

try:
    from dotenv import load_dotenv
except ImportError:
    print("Error: python-dotenv not installed. Run: pip install python-dotenv")
    sys.exit(1)


class SSHClient:
    """SSH client that reads credentials from .env file."""

    def __init__(
        self,
        host: str = None,
        user: str = None,
        password: str = None,
        key_path: str = None,
        port: int = None,
        env_file: str = None,
    ):
        # Load .env file
        if env_file:
            load_dotenv(env_file)
        else:
            # Search for .env in current dir and parent dirs
            for parent in [Path.cwd()] + list(Path.cwd().parents):
                env_path = parent / ".env"
                if env_path.exists():
                    load_dotenv(env_path)
                    break

        # Get credentials from params or environment
        self.host = host or os.getenv("SSH_HOST")
        self.user = user or os.getenv("SSH_USER")
        self.password = password or os.getenv("SSH_PASSWORD")
        self.key_path = key_path or os.getenv("SSH_KEY_PATH")
        self.port = port or int(os.getenv("SSH_PORT", "22"))

        # Validate required fields
        if not self.host:
            raise ValueError("SSH_HOST not set in .env or passed as argument")
        if not self.user:
            raise ValueError("SSH_USER not set in .env or passed as argument")
        if not self.password and not self.key_path:
            raise ValueError("SSH_PASSWORD or SSH_KEY_PATH required in .env or as argument")

        # Expand key path
        if self.key_path:
            self.key_path = os.path.expanduser(self.key_path)

        self._client = None

    def connect(self):
        """Establish SSH connection."""
        self._client = paramiko.SSHClient()
        self._client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        connect_kwargs = {
            "hostname": self.host,
            "port": self.port,
            "username": self.user,
        }

        if self.key_path:
            connect_kwargs["key_filename"] = self.key_path
        else:
            connect_kwargs["password"] = self.password

        self._client.connect(**connect_kwargs)
        return self

    def run(self, command: str, timeout: int = 30) -> str:
        """Execute command and return output."""
        if not self._client:
            self.connect()

        stdin, stdout, stderr = self._client.exec_command(command, timeout=timeout)
        output = stdout.read().decode("utf-8")
        errors = stderr.read().decode("utf-8")

        if errors:
            return f"{output}\n{errors}".strip()
        return output.strip()

    def interactive_shell(self):
        """Start an interactive shell session."""
        if not self._client:
            self.connect()

        channel = self._client.invoke_shell()
        print(f"Connected to {self.user}@{self.host}")
        print("Type 'exit' to disconnect\n")

        import select
        import socket

        try:
            while True:
                # Check if there's data to read from remote
                if channel.recv_ready():
                    data = channel.recv(1024).decode("utf-8", errors="replace")
                    print(data, end="", flush=True)

                # Get user input
                try:
                    if sys.stdin in select.select([sys.stdin], [], [], 0.1)[0]:
                        cmd = sys.stdin.readline()
                        if cmd.strip().lower() == "exit":
                            break
                        channel.send(cmd)
                except (select.error, OSError):
                    # Windows doesn't support select on stdin, use simple input
                    cmd = input()
                    if cmd.strip().lower() == "exit":
                        break
                    channel.send(cmd + "\n")
                    # Read response
                    import time
                    time.sleep(0.5)
                    while channel.recv_ready():
                        data = channel.recv(4096).decode("utf-8", errors="replace")
                        print(data, end="", flush=True)

        except KeyboardInterrupt:
            print("\nDisconnected")

    def close(self):
        """Close SSH connection."""
        if self._client:
            self._client.close()
            self._client = None

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def main():
    """CLI entry point."""
    try:
        ssh = SSHClient()

        if len(sys.argv) > 1:
            # Run command passed as argument
            command = " ".join(sys.argv[1:])
            with ssh:
                output = ssh.run(command)
                print(output)
        else:
            # Interactive mode
            with ssh:
                ssh.interactive_shell()

    except ValueError as e:
        print(f"Configuration error: {e}")
        print("\nCreate a .env file with:")
        print("  SSH_HOST=your-server.com")
        print("  SSH_USER=username")
        print("  SSH_KEY_PATH=~/.ssh/id_rsa  # or SSH_PASSWORD=yourpass")
        sys.exit(1)
    except paramiko.AuthenticationException:
        print("Authentication failed. Check your credentials in .env")
        sys.exit(1)
    except paramiko.SSHException as e:
        print(f"SSH error: {e}")
        sys.exit(1)
    except socket.error as e:
        print(f"Connection error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import socket
    main()
