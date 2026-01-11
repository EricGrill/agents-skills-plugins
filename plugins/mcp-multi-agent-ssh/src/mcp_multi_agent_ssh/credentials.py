"""Encrypted credential storage for SSH connections."""

import base64
import json
import logging
import os
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

from .types import StoredCredential

logger = logging.getLogger(__name__)

CONFIG_DIR = Path.home() / ".mcp-multi-agent-ssh"
CREDENTIALS_FILE = CONFIG_DIR / "credentials.enc"
SALT_FILE = CONFIG_DIR / "salt"

PBKDF2_ITERATIONS = 100_000
SALT_LENGTH = 16
NONCE_LENGTH = 12


class CredentialManager:
    """Manages encrypted storage of SSH credentials."""

    def __init__(self) -> None:
        self._credentials: dict[str, StoredCredential] = {}
        self._encryption_key: bytes | None = None
        self._master_password: str | None = None
        self._initialized = False

    def initialize(self, master_password: str | None = None) -> None:
        """Initialize the credential manager with a master password.

        Args:
            master_password: The master password. If None, reads from
                MCP_SSH_MASTER_PASSWORD environment variable.

        Raises:
            ValueError: If no master password is provided or found.
        """
        password = master_password or os.environ.get("MCP_SSH_MASTER_PASSWORD")
        if not password:
            raise ValueError(
                "Master password required. Provide it directly or set "
                "MCP_SSH_MASTER_PASSWORD environment variable."
            )

        self._master_password = password
        self._ensure_config_dir()
        self._derive_key()
        self._load()
        self._initialized = True

    def _ensure_config_dir(self) -> None:
        """Create config directory with secure permissions."""
        CONFIG_DIR.mkdir(mode=0o700, parents=True, exist_ok=True)

    def _get_or_create_salt(self) -> bytes:
        """Get existing salt or create a new one."""
        if SALT_FILE.exists():
            return SALT_FILE.read_bytes()

        salt = os.urandom(SALT_LENGTH)
        SALT_FILE.write_bytes(salt)
        SALT_FILE.chmod(0o600)
        return salt

    def _derive_key(self) -> None:
        """Derive encryption key from master password using PBKDF2."""
        if not self._master_password:
            raise ValueError("Master password not set")

        salt = self._get_or_create_salt()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=PBKDF2_ITERATIONS,
        )
        self._encryption_key = kdf.derive(self._master_password.encode())

    def _encrypt(self, data: bytes) -> bytes:
        """Encrypt data using AES-256-GCM."""
        if not self._encryption_key:
            raise ValueError("Encryption key not set")

        nonce = os.urandom(NONCE_LENGTH)
        aesgcm = AESGCM(self._encryption_key)
        ciphertext = aesgcm.encrypt(nonce, data, None)
        return nonce + ciphertext

    def _decrypt(self, data: bytes) -> bytes:
        """Decrypt data using AES-256-GCM."""
        if not self._encryption_key:
            raise ValueError("Encryption key not set")

        nonce = data[:NONCE_LENGTH]
        ciphertext = data[NONCE_LENGTH:]
        aesgcm = AESGCM(self._encryption_key)
        return aesgcm.decrypt(nonce, ciphertext, None)

    def _load(self) -> None:
        """Load credentials from encrypted file."""
        if not CREDENTIALS_FILE.exists():
            self._credentials = {}
            return

        try:
            encrypted_data = CREDENTIALS_FILE.read_bytes()
            decrypted_data = self._decrypt(encrypted_data)
            raw_creds = json.loads(decrypted_data.decode())

            self._credentials = {
                host: StoredCredential.model_validate(cred)
                for host, cred in raw_creds.items()
            }
            logger.info(f"Loaded credentials for {len(self._credentials)} hosts")
        except Exception as e:
            logger.error(f"Failed to load credentials: {e}")
            raise ValueError("Failed to decrypt credentials. Wrong master password?") from e

    def _save(self) -> None:
        """Save credentials to encrypted file."""
        raw_creds = {
            host: cred.model_dump(mode="json") for host, cred in self._credentials.items()
        }
        data = json.dumps(raw_creds).encode()
        encrypted_data = self._encrypt(data)

        CREDENTIALS_FILE.write_bytes(encrypted_data)
        CREDENTIALS_FILE.chmod(0o600)
        logger.info(f"Saved credentials for {len(self._credentials)} hosts")

    def _check_initialized(self) -> None:
        """Ensure the manager is initialized."""
        if not self._initialized:
            raise ValueError("CredentialManager not initialized. Call initialize() first.")

    def get(self, host: str) -> StoredCredential | None:
        """Get stored credentials for a host.

        Args:
            host: The hostname to look up.

        Returns:
            The stored credentials, or None if not found.
        """
        self._check_initialized()
        return self._credentials.get(host)

    def set(self, host: str, credential: StoredCredential) -> None:
        """Store credentials for a host.

        Args:
            host: The hostname.
            credential: The credentials to store.
        """
        self._check_initialized()
        self._credentials[host] = credential
        self._save()
        logger.info(f"Stored credentials for {host}")

    def delete(self, host: str) -> bool:
        """Delete stored credentials for a host.

        Args:
            host: The hostname.

        Returns:
            True if credentials were deleted, False if host not found.
        """
        self._check_initialized()
        if host in self._credentials:
            del self._credentials[host]
            self._save()
            logger.info(f"Deleted credentials for {host}")
            return True
        return False

    def list_hosts(self) -> list[str]:
        """List all hosts with stored credentials.

        Returns:
            List of hostnames.
        """
        self._check_initialized()
        return list(self._credentials.keys())

    def has_credentials(self, host: str) -> bool:
        """Check if credentials exist for a host.

        Args:
            host: The hostname.

        Returns:
            True if credentials exist.
        """
        self._check_initialized()
        return host in self._credentials
