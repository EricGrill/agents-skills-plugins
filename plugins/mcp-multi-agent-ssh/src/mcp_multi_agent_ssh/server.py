"""MCP SSH Grill server - Stateful SSH connections for Claude Code."""

import asyncio
import getpass
import logging
import os
import sys
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from dataclasses import dataclass

from mcp.server.fastmcp import Context, FastMCP

from .connection_pool import ConnectionPool
from .credentials import CredentialManager
from .types import ConnectionInfo, ExecResult, FileInfo, SftpResult

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stderr)],
)
logger = logging.getLogger(__name__)


@dataclass
class AppContext:
    """Application context with shared resources."""

    credential_manager: CredentialManager
    connection_pool: ConnectionPool


def get_master_password() -> str:
    """Get master password from environment or prompt user."""
    password = os.environ.get("MCP_SSH_MASTER_PASSWORD")
    if password:
        return password

    # If stdin is a TTY, prompt for password
    if sys.stdin.isatty():
        return getpass.getpass("Enter master password for SSH credentials: ")

    raise ValueError(
        "Master password required. Set MCP_SSH_MASTER_PASSWORD environment variable "
        "or run interactively."
    )


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle."""
    # Initialize credential manager
    credential_manager = CredentialManager()
    try:
        password = get_master_password()
        credential_manager.initialize(password)
    except ValueError as e:
        logger.error(f"Failed to initialize credentials: {e}")
        raise

    # Initialize connection pool
    connection_pool = ConnectionPool(credential_manager)
    await connection_pool.start()

    logger.info("MCP SSH Grill server started")

    try:
        yield AppContext(
            credential_manager=credential_manager,
            connection_pool=connection_pool,
        )
    finally:
        await connection_pool.stop()
        logger.info("MCP SSH Grill server stopped")


# Create the MCP server
mcp = FastMCP(
    "SSH Grill",
    lifespan=app_lifespan,
)


# =============================================================================
# Connection Management Tools
# =============================================================================


@mcp.tool()
async def ssh_connect(
    host: str,
    ctx: Context,
    port: int = 22,
    username: str | None = None,
    password: str | None = None,
    private_key: str | None = None,
    save_credentials: bool = True,
) -> dict:
    """Connect to an SSH server.

    If credentials are already stored for this host, they will be used automatically.
    New credentials can optionally be saved for future connections.

    Args:
        host: The hostname or IP address to connect to.
        port: The SSH port (default 22).
        username: The username for authentication (required if no stored credentials).
        password: The password for authentication (optional, use either password or private_key).
        private_key: The private key as a PEM string (optional, use either password or private_key).
        save_credentials: Whether to save the credentials for future use (default True).

    Returns:
        Connection information including host, port, and username.
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context
    pool = app_ctx.connection_pool

    try:
        info = await pool.connect(
            host=host,
            port=port,
            username=username,
            password=password,
            private_key=private_key,
            save_credentials=save_credentials,
        )
        return {
            "status": "connected",
            "host": info.host,
            "port": info.port,
            "username": info.username,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def ssh_disconnect(host: str, ctx: Context, port: int = 22) -> dict:
    """Disconnect from an SSH server.

    Args:
        host: The hostname to disconnect from.
        port: The SSH port (default 22).

    Returns:
        Status of the disconnect operation.
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context
    pool = app_ctx.connection_pool

    if await pool.disconnect(host, port):
        return {"status": "disconnected", "host": host, "port": port}
    else:
        return {"status": "not_connected", "host": host, "port": port}


@mcp.tool()
async def ssh_list_connections(ctx: Context) -> list[dict]:
    """List all active SSH connections.

    Returns:
        List of active connections with their details and idle time.
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context
    pool = app_ctx.connection_pool

    connections = pool.list_connections()
    return [
        {
            "host": c.host,
            "port": c.port,
            "username": c.username,
            "connected_at": c.connected_at.isoformat(),
            "last_activity": c.last_activity.isoformat(),
            "idle_seconds": round(c.idle_seconds, 1),
        }
        for c in connections
    ]


# =============================================================================
# Command Execution Tools
# =============================================================================


@mcp.tool()
async def ssh_exec(
    host: str, command: str, ctx: Context, port: int = 22, timeout: int = 30
) -> dict:
    """Run a command on a remote SSH server.

    Automatically connects using stored credentials if not already connected.

    Args:
        host: The hostname to run the command on.
        command: The command to run.
        port: The SSH port (default 22).
        timeout: Command timeout in seconds (default 30).

    Returns:
        Command output including stdout, stderr, and exit code.
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context
    pool = app_ctx.connection_pool

    try:
        result = await pool.exec_command(host, command, port, timeout)
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "exit_code": result.exit_code,
        }
    except asyncio.TimeoutError:
        return {
            "stdout": "",
            "stderr": f"Command timed out after {timeout} seconds",
            "exit_code": -1,
        }
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "exit_code": -1}


# =============================================================================
# SFTP Tools
# =============================================================================


@mcp.tool()
async def sftp_upload(
    host: str, local_path: str, remote_path: str, ctx: Context, port: int = 22
) -> dict:
    """Upload a file to a remote SSH server via SFTP.

    Args:
        host: The hostname to upload to.
        local_path: Path to the local file to upload.
        remote_path: Destination path on the remote server.
        port: The SSH port (default 22).

    Returns:
        Upload result including status and bytes transferred.
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context
    pool = app_ctx.connection_pool

    try:
        result = await pool.sftp_upload(host, local_path, remote_path, port)
        return {
            "status": result.status,
            "message": result.message,
            "bytes_transferred": result.bytes_transferred,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def sftp_download(
    host: str, remote_path: str, local_path: str, ctx: Context, port: int = 22
) -> dict:
    """Download a file from a remote SSH server via SFTP.

    Args:
        host: The hostname to download from.
        remote_path: Path to the file on the remote server.
        local_path: Destination path on the local machine.
        port: The SSH port (default 22).

    Returns:
        Download result including status and bytes transferred.
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context
    pool = app_ctx.connection_pool

    try:
        result = await pool.sftp_download(host, remote_path, local_path, port)
        return {
            "status": result.status,
            "message": result.message,
            "bytes_transferred": result.bytes_transferred,
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


@mcp.tool()
async def sftp_list(host: str, path: str, ctx: Context, port: int = 22) -> list[dict]:
    """List files in a directory on a remote SSH server.

    Args:
        host: The hostname to list files on.
        path: The directory path to list.
        port: The SSH port (default 22).

    Returns:
        List of files with their details (name, size, permissions, etc.).
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context
    pool = app_ctx.connection_pool

    try:
        files = await pool.sftp_list(host, path, port)
        return [
            {
                "name": f.name,
                "path": f.path,
                "is_dir": f.is_dir,
                "size": f.size,
                "modified": f.modified.isoformat() if f.modified else None,
                "permissions": f.permissions,
            }
            for f in files
        ]
    except Exception as e:
        return [{"error": str(e)}]


# =============================================================================
# Credential Management Tools
# =============================================================================


@mcp.tool()
async def ssh_list_credentials(ctx: Context) -> list[str]:
    """List all hosts with stored SSH credentials.

    Returns:
        List of hostnames that have stored credentials.
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context
    cred_manager = app_ctx.credential_manager

    return cred_manager.list_hosts()


@mcp.tool()
async def ssh_delete_credentials(host: str, ctx: Context) -> dict:
    """Delete stored SSH credentials for a host.

    Args:
        host: The hostname to delete credentials for.

    Returns:
        Status of the delete operation.
    """
    app_ctx: AppContext = ctx.request_context.lifespan_context
    cred_manager = app_ctx.credential_manager

    if cred_manager.delete(host):
        return {"status": "deleted", "host": host}
    else:
        return {"status": "not_found", "host": host}


def main():
    """Entry point for the MCP SSH Grill server."""
    mcp.run()


if __name__ == "__main__":
    main()
