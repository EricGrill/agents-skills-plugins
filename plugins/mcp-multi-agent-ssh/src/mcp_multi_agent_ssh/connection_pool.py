"""SSH connection pool with automatic timeout and cleanup."""

import asyncio
import logging
from dataclasses import dataclass
from datetime import datetime, timedelta

import asyncssh

from .credentials import CredentialManager
from .types import AuthType, ConnectionInfo, ExecResult, FileInfo, SftpResult, StoredCredential

logger = logging.getLogger(__name__)

IDLE_TIMEOUT_SECONDS = 600  # 10 minutes
CLEANUP_INTERVAL_SECONDS = 60  # Check every minute


@dataclass
class PooledConnection:
    """A connection in the pool with metadata."""

    conn: asyncssh.SSHClientConnection
    host: str
    port: int
    username: str
    connected_at: datetime
    last_activity: datetime


class ConnectionPool:
    """Manages a pool of SSH connections with automatic timeout."""

    def __init__(self, credential_manager: CredentialManager) -> None:
        self._connections: dict[str, PooledConnection] = {}
        self._credential_manager = credential_manager
        self._cleanup_task: asyncio.Task | None = None
        self._lock = asyncio.Lock()

    def _make_key(self, host: str, port: int) -> str:
        """Create a unique key for a host:port combination."""
        return f"{host}:{port}"

    async def start(self) -> None:
        """Start the connection pool and cleanup task."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("Connection pool started")

    async def stop(self) -> None:
        """Stop the connection pool and close all connections."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        async with self._lock:
            for key, pooled in list(self._connections.items()):
                pooled.conn.close()
                await pooled.conn.wait_closed()
                logger.info(f"Closed connection to {pooled.host}:{pooled.port}")
            self._connections.clear()

        logger.info("Connection pool stopped")

    async def _cleanup_loop(self) -> None:
        """Background task to clean up idle connections."""
        while True:
            try:
                await asyncio.sleep(CLEANUP_INTERVAL_SECONDS)
                await self._cleanup_idle_connections()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")

    async def _cleanup_idle_connections(self) -> None:
        """Close connections that have been idle too long."""
        now = datetime.utcnow()
        timeout_threshold = now - timedelta(seconds=IDLE_TIMEOUT_SECONDS)

        async with self._lock:
            expired = [
                (key, pooled)
                for key, pooled in self._connections.items()
                if pooled.last_activity < timeout_threshold
            ]

            for key, pooled in expired:
                pooled.conn.close()
                await pooled.conn.wait_closed()
                del self._connections[key]
                logger.warning(
                    f"Connection to {pooled.host}:{pooled.port} expired after "
                    f"{IDLE_TIMEOUT_SECONDS // 60} minutes of inactivity"
                )

    async def connect(
        self,
        host: str,
        port: int = 22,
        username: str | None = None,
        password: str | None = None,
        private_key: str | None = None,
        save_credentials: bool = True,
    ) -> ConnectionInfo:
        """Connect to an SSH server.

        If credentials are stored for the host, they will be used automatically.
        New credentials can optionally be saved for future use.

        Args:
            host: The hostname to connect to.
            port: The SSH port (default 22).
            username: The username. Required if no stored credentials.
            password: The password (if using password auth).
            private_key: The private key as a string (if using key auth).
            save_credentials: Whether to save new credentials.

        Returns:
            Information about the connection.

        Raises:
            ValueError: If no credentials available.
            asyncssh.Error: If connection fails.
        """
        key = self._make_key(host, port)

        async with self._lock:
            # Check for existing connection
            if key in self._connections:
                pooled = self._connections[key]
                pooled.last_activity = datetime.utcnow()
                return self._get_connection_info(pooled)

        # Get or create credentials
        stored = self._credential_manager.get(host)

        if stored:
            username = stored.username
            port = stored.port
            if stored.auth_type == AuthType.PASSWORD:
                password = stored.password
            else:
                private_key = stored.private_key
        elif not username:
            raise ValueError(
                f"No stored credentials for {host} and no username provided"
            )

        # Prepare connection options
        connect_kwargs: dict = {
            "host": host,
            "port": port,
            "username": username,
            "known_hosts": None,  # Skip host key verification for simplicity
        }

        if private_key:
            connect_kwargs["client_keys"] = [asyncssh.import_private_key(private_key)]
        elif password:
            connect_kwargs["password"] = password
        else:
            raise ValueError("Either password or private_key is required")

        # Connect
        conn = await asyncssh.connect(**connect_kwargs)
        now = datetime.utcnow()

        pooled = PooledConnection(
            conn=conn,
            host=host,
            port=port,
            username=username,
            connected_at=now,
            last_activity=now,
        )

        async with self._lock:
            self._connections[key] = pooled

        logger.info(f"Connected to {host}:{port} as {username}")

        # Save credentials if requested and not already stored
        if save_credentials and not stored:
            if private_key:
                cred = StoredCredential(
                    username=username,
                    auth_type=AuthType.KEY,
                    private_key=private_key,
                    port=port,
                )
            else:
                cred = StoredCredential(
                    username=username,
                    auth_type=AuthType.PASSWORD,
                    password=password,
                    port=port,
                )
            self._credential_manager.set(host, cred)

        return self._get_connection_info(pooled)

    async def disconnect(self, host: str, port: int = 22) -> bool:
        """Disconnect from an SSH server.

        Args:
            host: The hostname.
            port: The SSH port.

        Returns:
            True if disconnected, False if not connected.
        """
        key = self._make_key(host, port)

        async with self._lock:
            if key not in self._connections:
                return False

            pooled = self._connections.pop(key)
            pooled.conn.close()
            await pooled.conn.wait_closed()
            logger.info(f"Disconnected from {host}:{port}")
            return True

    async def get_connection(
        self, host: str, port: int = 22
    ) -> asyncssh.SSHClientConnection:
        """Get an existing connection or auto-connect using stored credentials.

        Args:
            host: The hostname.
            port: The SSH port.

        Returns:
            The SSH connection.

        Raises:
            ValueError: If not connected and no stored credentials.
        """
        key = self._make_key(host, port)

        async with self._lock:
            if key in self._connections:
                pooled = self._connections[key]
                pooled.last_activity = datetime.utcnow()
                return pooled.conn

        # Auto-connect using stored credentials
        stored = self._credential_manager.get(host)
        if not stored:
            raise ValueError(
                f"Not connected to {host}:{port} and no stored credentials available"
            )

        await self.connect(host, port)
        return self._connections[key].conn

    def list_connections(self) -> list[ConnectionInfo]:
        """List all active connections.

        Returns:
            List of connection information.
        """
        return [self._get_connection_info(p) for p in self._connections.values()]

    def _get_connection_info(self, pooled: PooledConnection) -> ConnectionInfo:
        """Create ConnectionInfo from a PooledConnection."""
        now = datetime.utcnow()
        idle = (now - pooled.last_activity).total_seconds()
        return ConnectionInfo(
            host=pooled.host,
            port=pooled.port,
            username=pooled.username,
            connected_at=pooled.connected_at,
            last_activity=pooled.last_activity,
            idle_seconds=idle,
        )

    async def exec_command(
        self, host: str, command: str, port: int = 22, timeout: int = 30
    ) -> ExecResult:
        """Execute a command on a remote host.

        Args:
            host: The hostname.
            command: The command to execute.
            port: The SSH port.
            timeout: Command timeout in seconds.

        Returns:
            The command result.
        """
        conn = await self.get_connection(host, port)
        result = await asyncio.wait_for(
            conn.run(command, check=False),
            timeout=timeout,
        )
        return ExecResult(
            stdout=result.stdout or "",
            stderr=result.stderr or "",
            exit_code=result.exit_status or 0,
        )

    async def sftp_upload(
        self, host: str, local_path: str, remote_path: str, port: int = 22
    ) -> SftpResult:
        """Upload a file to a remote host.

        Args:
            host: The hostname.
            local_path: Local file path.
            remote_path: Remote destination path.
            port: The SSH port.

        Returns:
            The upload result.
        """
        conn = await self.get_connection(host, port)
        async with conn.start_sftp_client() as sftp:
            await sftp.put(local_path, remote_path)
            attrs = await sftp.stat(remote_path)
            return SftpResult(
                status="success",
                message=f"Uploaded {local_path} to {remote_path}",
                bytes_transferred=attrs.size,
            )

    async def sftp_download(
        self, host: str, remote_path: str, local_path: str, port: int = 22
    ) -> SftpResult:
        """Download a file from a remote host.

        Args:
            host: The hostname.
            remote_path: Remote file path.
            local_path: Local destination path.
            port: The SSH port.

        Returns:
            The download result.
        """
        conn = await self.get_connection(host, port)
        async with conn.start_sftp_client() as sftp:
            attrs = await sftp.stat(remote_path)
            await sftp.get(remote_path, local_path)
            return SftpResult(
                status="success",
                message=f"Downloaded {remote_path} to {local_path}",
                bytes_transferred=attrs.size,
            )

    async def sftp_list(
        self, host: str, path: str, port: int = 22
    ) -> list[FileInfo]:
        """List files in a remote directory.

        Args:
            host: The hostname.
            path: Remote directory path.
            port: The SSH port.

        Returns:
            List of file information.
        """
        conn = await self.get_connection(host, port)
        async with conn.start_sftp_client() as sftp:
            entries = await sftp.readdir(path)
            result = []
            for entry in entries:
                if entry.filename in (".", ".."):
                    continue
                result.append(
                    FileInfo(
                        name=entry.filename,
                        path=f"{path.rstrip('/')}/{entry.filename}",
                        is_dir=entry.attrs.type == asyncssh.FILEXFER_TYPE_DIRECTORY,
                        size=entry.attrs.size or 0,
                        modified=datetime.fromtimestamp(entry.attrs.mtime)
                        if entry.attrs.mtime
                        else None,
                        permissions=oct(entry.attrs.permissions)[-3:]
                        if entry.attrs.permissions
                        else None,
                    )
                )
            return result
