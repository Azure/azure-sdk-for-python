# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""
Test to verify that security warnings are present in the SecretClient docstrings.
This is a documentation-only test to ensure users are warned about the security
implications of disabling verify_challenge_resource.
"""
import os
import pytest


class TestDocstringSecurity:
    """Test class for verifying security warnings in docstrings and README."""

    def test_sync_client_file_contains_security_note(self):
        """Verify that the sync SecretClient file contains security warnings."""
        client_file = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "azure", 
            "keyvault", 
            "secrets", 
            "_client.py"
        )
        with open(client_file, "r") as f:
            content = f.read()
        
        assert "SECURITY NOTE" in content, "Client file should contain 'SECURITY NOTE'"
        assert "verify_challenge_resource" in content, "Client file should mention verify_challenge_resource"
        assert "CWE-346" in content, "Client file should reference CWE-346"
        assert "OWASP A07" in content, "Client file should reference OWASP A07"
        assert "Leave this set to True" in content, "Client file should recommend keeping it True"
        assert "unintended resource" in content, "Client file should warn about unintended resource access"

    def test_async_client_file_contains_security_note(self):
        """Verify that the async SecretClient file contains security warnings."""
        client_file = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "azure", 
            "keyvault", 
            "secrets", 
            "aio",
            "_client.py"
        )
        with open(client_file, "r") as f:
            content = f.read()
        
        assert "SECURITY NOTE" in content, "Async client file should contain 'SECURITY NOTE'"
        assert "verify_challenge_resource" in content, "Async client file should mention verify_challenge_resource"
        assert "CWE-346" in content, "Async client file should reference CWE-346"
        assert "OWASP A07" in content, "Async client file should reference OWASP A07"
        assert "Leave this set to True" in content, "Async client file should recommend keeping it True"
        assert "unintended resource" in content, "Async client file should warn about unintended resource access"

    def test_readme_contains_security_note(self):
        """Verify that the README contains security warnings about verify_challenge_resource."""
        readme_file = os.path.join(
            os.path.dirname(__file__), 
            "..", 
            "README.md"
        )
        with open(readme_file, "r") as f:
            content = f.read()
        
        assert "Security note" in content, "README should contain 'Security note'"
        assert "verify_challenge_resource" in content, "README should mention verify_challenge_resource"
        assert "CWE-346" in content, "README should reference CWE-346"
        assert "OWASP A07" in content, "README should reference OWASP A07"
        # Check that the security note appears after the client creation example
        assert content.index("SecretClient(vault_url=VAULT_URL, credential=credential)") < content.index("Security note"), \
            "Security note should appear after the client creation example"

