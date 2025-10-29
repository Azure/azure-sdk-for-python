# pylint: disable=line-too-long,useless-suppression
"""Tests for API version defaults in Confidential Ledger clients."""
import os
import re


class TestDefaultApiVersion:
    """Test that the default API version is correctly set in source code."""

    def test_data_plane_patch_has_correct_default(self):
        """Verify data-plane _patch.py has 2024-12-09-preview as default."""
        patch_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "azure", "confidentialledger", "_patch.py"
        )
        
        with open(patch_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check docstring mentions the correct version
        assert '"2024-12-09-preview"' in content, \
            "Docstring should mention 2024-12-09-preview"
        
        # Check code sets the correct default
        assert 'api_version = kwargs.pop("api_version", "2024-12-09-preview")' in content, \
            "Code should default to 2024-12-09-preview"

    def test_data_plane_async_patch_has_correct_default(self):
        """Verify async data-plane aio/_patch.py has 2024-12-09-preview as default."""
        patch_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "azure", "confidentialledger", "aio", "_patch.py"
        )
        
        with open(patch_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check docstring mentions the correct version
        assert '"2024-12-09-preview"' in content, \
            "Docstring should mention 2024-12-09-preview"
        
        # Check code sets the correct default
        assert 'api_version = kwargs.pop("api_version", "2024-12-09-preview")' in content, \
            "Code should default to 2024-12-09-preview"

    def test_mgmt_client_docstring_mentions_version(self):
        """Verify management client docstring mentions current default version."""
        mgmt_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "azure-mgmt-confidentialledger", "azure", "mgmt", "confidentialledger",
            "_confidential_ledger.py"
        )
        
        with open(mgmt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check docstring mentions the correct version
        assert "2024-09-19-preview" in content, \
            "Docstring should mention 2024-09-19-preview as default"
        
        # Check it mentions the newer version
        assert "2025-06-10-preview" in content, \
            "Docstring should mention 2025-06-10-preview as available"

    def test_mgmt_client_async_docstring_mentions_version(self):
        """Verify async management client docstring mentions current default version."""
        mgmt_file = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "azure-mgmt-confidentialledger", "azure", "mgmt", "confidentialledger",
            "aio", "_confidential_ledger.py"
        )
        
        with open(mgmt_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check docstring mentions the correct version
        assert "2024-09-19-preview" in content, \
            "Docstring should mention 2024-09-19-preview as default"
        
        # Check it mentions the newer version
        assert "2025-06-10-preview" in content, \
            "Docstring should mention 2025-06-10-preview as available"

    def test_generated_config_uses_latest_preview(self):
        """Verify generated configuration file uses the latest preview version."""
        config_file = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "azure", "confidentialledger", "_configuration.py"
        )
        
        with open(config_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that generated config uses 2024-12-09-preview
        assert '"2024-12-09-preview"' in content, \
            "Generated configuration should use 2024-12-09-preview"
