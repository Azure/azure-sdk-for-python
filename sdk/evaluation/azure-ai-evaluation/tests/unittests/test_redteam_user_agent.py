"""Tests for red team user agent functionality."""

import pytest
from azure.ai.evaluation._user_agent import UserAgentSingleton


class TestRedTeamUserAgent:
    """Test suite for red team user agent functionality."""

    def test_default_redteam_context(self):
        """Test that the default red team context works as expected."""
        base_user_agent = UserAgentSingleton().value

        with UserAgentSingleton.redteam_context():
            redteam_user_agent = UserAgentSingleton().value
            expected = f"{base_user_agent} (type=redteam; subtype=RedTeam)"
            assert redteam_user_agent == expected

        # Should restore to original after context
        assert UserAgentSingleton().value == base_user_agent

    def test_custom_subtype_redteam_context(self):
        """Test red team context with custom subtype."""
        base_user_agent = UserAgentSingleton().value
        custom_subtype = "CustomTest"

        with UserAgentSingleton.redteam_context(subtype=custom_subtype):
            redteam_user_agent = UserAgentSingleton().value
            expected = f"{base_user_agent} (type=redteam; subtype={custom_subtype})"
            assert redteam_user_agent == expected

        # Should restore to original after context
        assert UserAgentSingleton().value == base_user_agent

    def test_nested_contexts(self):
        """Test nested user agent contexts."""
        base_user_agent = UserAgentSingleton().value

        with UserAgentSingleton.add_useragent_product("outer/1.0"):
            outer_user_agent = UserAgentSingleton().value
            expected_outer = f"{base_user_agent} outer/1.0"
            assert outer_user_agent == expected_outer

            with UserAgentSingleton.redteam_context(subtype="NestedTest"):
                nested_user_agent = UserAgentSingleton().value
                expected_nested = f"{expected_outer} (type=redteam; subtype=NestedTest)"
                assert nested_user_agent == expected_nested

            # Should restore to outer context
            assert UserAgentSingleton().value == expected_outer

        # Should restore to original after all contexts
        assert UserAgentSingleton().value == base_user_agent

    def test_multiple_redteam_contexts(self):
        """Test multiple red team contexts in sequence."""
        base_user_agent = UserAgentSingleton().value

        # First context
        with UserAgentSingleton.redteam_context(subtype="First"):
            first_user_agent = UserAgentSingleton().value
            expected_first = f"{base_user_agent} (type=redteam; subtype=First)"
            assert first_user_agent == expected_first

        # Should restore to original
        assert UserAgentSingleton().value == base_user_agent

        # Second context
        with UserAgentSingleton.redteam_context(subtype="Second"):
            second_user_agent = UserAgentSingleton().value
            expected_second = f"{base_user_agent} (type=redteam; subtype=Second)"
            assert second_user_agent == expected_second

        # Should restore to original
        assert UserAgentSingleton().value == base_user_agent

    def test_redteam_context_kwargs_ignored(self):
        """Test that additional kwargs are ignored gracefully."""
        base_user_agent = UserAgentSingleton().value

        with UserAgentSingleton.redteam_context(subtype="Test", ignored_param="should_be_ignored"):
            redteam_user_agent = UserAgentSingleton().value
            expected = f"{base_user_agent} (type=redteam; subtype=Test)"
            assert redteam_user_agent == expected

        # Should restore to original after context
        assert UserAgentSingleton().value == base_user_agent
