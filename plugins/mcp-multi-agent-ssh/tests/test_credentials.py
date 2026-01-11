"""Tests for credential manager."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from mcp_multi_agent_ssh.credentials import CredentialManager
from mcp_multi_agent_ssh.types import AuthType, StoredCredential


@pytest.fixture
def temp_config_dir(tmp_path):
    """Create a temporary config directory for tests."""
    config_dir = tmp_path / ".mcp-multi-agent-ssh"
    config_dir.mkdir(mode=0o700)
    return config_dir


@pytest.fixture
def credential_manager(temp_config_dir):
    """Create a credential manager with test config directory."""
    with patch("mcp_multi_agent_ssh.credentials.CONFIG_DIR", temp_config_dir):
        with patch(
            "mcp_multi_agent_ssh.credentials.CREDENTIALS_FILE",
            temp_config_dir / "credentials.enc",
        ):
            with patch("mcp_multi_agent_ssh.credentials.SALT_FILE", temp_config_dir / "salt"):
                manager = CredentialManager()
                manager.initialize("test-master-password")
                yield manager


class TestCredentialManager:
    """Tests for CredentialManager class."""

    def test_initialize_creates_salt(self, temp_config_dir):
        """Test that initialization creates a salt file."""
        with patch("mcp_multi_agent_ssh.credentials.CONFIG_DIR", temp_config_dir):
            with patch("mcp_multi_agent_ssh.credentials.SALT_FILE", temp_config_dir / "salt"):
                with patch(
                    "mcp_multi_agent_ssh.credentials.CREDENTIALS_FILE",
                    temp_config_dir / "credentials.enc",
                ):
                    manager = CredentialManager()
                    manager.initialize("test-password")
                    assert (temp_config_dir / "salt").exists()

    def test_store_and_retrieve_password_credential(self, credential_manager):
        """Test storing and retrieving a password-based credential."""
        cred = StoredCredential(
            username="testuser",
            auth_type=AuthType.PASSWORD,
            password="testpass",
            port=22,
        )
        credential_manager.set("example.com", cred)

        retrieved = credential_manager.get("example.com")
        assert retrieved is not None
        assert retrieved.username == "testuser"
        assert retrieved.password == "testpass"
        assert retrieved.auth_type == AuthType.PASSWORD

    def test_store_and_retrieve_key_credential(self, credential_manager):
        """Test storing and retrieving a key-based credential."""
        cred = StoredCredential(
            username="keyuser",
            auth_type=AuthType.KEY,
            private_key="-----BEGIN OPENSSH PRIVATE KEY-----\ntest\n-----END OPENSSH PRIVATE KEY-----",
            port=2222,
        )
        credential_manager.set("server.example.com", cred)

        retrieved = credential_manager.get("server.example.com")
        assert retrieved is not None
        assert retrieved.username == "keyuser"
        assert retrieved.auth_type == AuthType.KEY
        assert "OPENSSH PRIVATE KEY" in retrieved.private_key
        assert retrieved.port == 2222

    def test_list_hosts(self, credential_manager):
        """Test listing stored hosts."""
        cred1 = StoredCredential(
            username="user1", auth_type=AuthType.PASSWORD, password="pass1"
        )
        cred2 = StoredCredential(
            username="user2", auth_type=AuthType.PASSWORD, password="pass2"
        )

        credential_manager.set("host1.com", cred1)
        credential_manager.set("host2.com", cred2)

        hosts = credential_manager.list_hosts()
        assert "host1.com" in hosts
        assert "host2.com" in hosts
        assert len(hosts) == 2

    def test_delete_credential(self, credential_manager):
        """Test deleting a credential."""
        cred = StoredCredential(
            username="testuser", auth_type=AuthType.PASSWORD, password="testpass"
        )
        credential_manager.set("delete-me.com", cred)

        assert credential_manager.has_credentials("delete-me.com")
        result = credential_manager.delete("delete-me.com")
        assert result is True
        assert not credential_manager.has_credentials("delete-me.com")

    def test_delete_nonexistent_credential(self, credential_manager):
        """Test deleting a credential that doesn't exist."""
        result = credential_manager.delete("nonexistent.com")
        assert result is False

    def test_get_nonexistent_credential(self, credential_manager):
        """Test getting a credential that doesn't exist."""
        result = credential_manager.get("nonexistent.com")
        assert result is None

    def test_wrong_master_password_fails(self, temp_config_dir):
        """Test that wrong master password fails to decrypt."""
        with patch("mcp_multi_agent_ssh.credentials.CONFIG_DIR", temp_config_dir):
            with patch(
                "mcp_multi_agent_ssh.credentials.CREDENTIALS_FILE",
                temp_config_dir / "credentials.enc",
            ):
                with patch("mcp_multi_agent_ssh.credentials.SALT_FILE", temp_config_dir / "salt"):
                    # Create and save credentials with one password
                    manager1 = CredentialManager()
                    manager1.initialize("correct-password")
                    cred = StoredCredential(
                        username="user", auth_type=AuthType.PASSWORD, password="pass"
                    )
                    manager1.set("test.com", cred)

                    # Try to load with wrong password
                    manager2 = CredentialManager()
                    with pytest.raises(ValueError, match="Failed to decrypt"):
                        manager2.initialize("wrong-password")
