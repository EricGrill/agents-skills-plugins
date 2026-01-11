"""Type definitions for MCP SSH Grill."""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class AuthType(str, Enum):
    PASSWORD = "password"
    KEY = "key"


class StoredCredential(BaseModel):
    """Credential stored for a specific host."""

    username: str
    auth_type: AuthType
    password: str | None = None
    private_key: str | None = None
    port: int = 22
    added_at: datetime = Field(default_factory=datetime.utcnow)


class ConnectionInfo(BaseModel):
    """Information about an active connection."""

    host: str
    port: int
    username: str
    connected_at: datetime
    last_activity: datetime
    idle_seconds: float


class ExecResult(BaseModel):
    """Result of executing a command over SSH."""

    stdout: str
    stderr: str
    exit_code: int


class SftpResult(BaseModel):
    """Result of an SFTP operation."""

    status: Literal["success", "error"]
    message: str | None = None
    bytes_transferred: int | None = None


class FileInfo(BaseModel):
    """Information about a remote file."""

    name: str
    path: str
    is_dir: bool
    size: int
    modified: datetime | None = None
    permissions: str | None = None
