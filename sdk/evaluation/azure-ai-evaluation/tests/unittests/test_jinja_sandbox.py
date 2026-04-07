# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Tests for Jinja2 sandboxing in azure-ai-evaluation (MSRC-110257)."""

import os
from unittest.mock import patch

import jinja2
import pytest

from azure.ai.evaluation._legacy.prompty._utils import render_jinja_template
from azure.ai.evaluation.simulator._conversation import (
    _create_jinja_template,
    ConversationBot,
    ConversationRole,
    OpenAIChatCompletionsModel,
)


# Common SSTI payloads that should be blocked by the sandbox
SSTI_PAYLOAD_CLASS = "{{ ().__class__.__base__.__subclasses__() }}"
SSTI_PAYLOAD_IMPORT = (
    "{% for x in ().__class__.__base__.__subclasses__() %}"
    "{% if 'catch_warnings' in x.__name__ %}"
    "{{ x().__enter__.__globals__['__builtins__']['__import__']('os').popen('echo pwned').read() }}"
    "{% endif %}{% endfor %}"
)
SSTI_PAYLOAD_GETATTR = "{{ ''.__class__.__mro__[1].__subclasses__() }}"


class MockModel(OpenAIChatCompletionsModel):
    def __init__(self):
        super().__init__(name="mock", endpoint_url="https://mock", token_manager="mock")


# ============================================================
# Tests for _legacy/prompty/_utils.py :: render_jinja_template
# ============================================================


@pytest.mark.unittest
class TestRenderJinjaTemplateSandbox:
    """Tests for render_jinja_template in _legacy/prompty/_utils.py."""

    def test_normal_template_renders_with_sandbox(self):
        """Normal templates should render correctly with sandbox enabled."""
        result = render_jinja_template("Hello, {{ name }}!", name="World")
        assert result == "Hello, World!"

    def test_template_with_loop_renders(self):
        """Templates with standard Jinja2 features like loops should work."""
        template = "{% for item in items %}{{ item }} {% endfor %}"
        result = render_jinja_template(template, items=["a", "b", "c"])
        assert result == "a b c "

    def test_template_with_conditionals_renders(self):
        """Templates with conditionals should work."""
        template = "{% if show %}visible{% else %}hidden{% endif %}"
        assert render_jinja_template(template, show=True) == "visible"
        assert render_jinja_template(template, show=False) == "hidden"

    def test_ssti_class_access_blocked(self):
        """Accessing __class__ should raise SecurityError via sandbox."""
        with pytest.raises(Exception) as exc_info:
            render_jinja_template(SSTI_PAYLOAD_CLASS)
        # The SecurityError gets wrapped in PromptyException
        assert "SecurityError" in str(exc_info.value) or "unsafe" in str(exc_info.value).lower()

    def test_ssti_import_blocked(self):
        """Attempting to import modules via SSTI should be blocked."""
        with pytest.raises(Exception):
            render_jinja_template(SSTI_PAYLOAD_IMPORT)

    def test_ssti_mro_access_blocked(self):
        """Accessing __mro__ should be blocked by sandbox."""
        with pytest.raises(Exception):
            render_jinja_template(SSTI_PAYLOAD_GETATTR)

    @patch.dict(os.environ, {"PF_USE_SANDBOX_FOR_JINJA": "true"})
    def test_sandbox_enabled_explicitly(self):
        """Sandbox should be active when PF_USE_SANDBOX_FOR_JINJA=true."""
        with pytest.raises(Exception):
            render_jinja_template(SSTI_PAYLOAD_CLASS)

    @patch.dict(os.environ, {"PF_USE_SANDBOX_FOR_JINJA": "false"})
    def test_sandbox_disabled_allows_ssti(self):
        """When sandbox is explicitly disabled, SSTI payloads should NOT raise SecurityError."""
        # This is the unsafe opt-out — template renders without sandbox
        result = render_jinja_template(SSTI_PAYLOAD_CLASS)
        assert result is not None  # It renders (dangerously)

    def test_sandbox_enabled_by_default(self):
        """Sandbox should be enabled by default when env var is not set."""
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("PF_USE_SANDBOX_FOR_JINJA", None)
            with pytest.raises(Exception):
                render_jinja_template(SSTI_PAYLOAD_CLASS)


# ============================================================
# Tests for simulator/_conversation :: _create_jinja_template
# ============================================================


@pytest.mark.unittest
class TestCreateJinjaTemplateSandbox:
    """Tests for _create_jinja_template in simulator/_conversation/__init__.py."""

    def test_normal_template_renders(self):
        """Normal templates should render correctly."""
        tmpl = _create_jinja_template("Hello, {{ name }}!")
        assert tmpl.render(name="World") == "Hello, World!"

    def test_strict_undefined_preserved(self):
        """StrictUndefined should still be enforced — missing vars raise."""
        tmpl = _create_jinja_template("Hello, {{ name }}!")
        with pytest.raises(jinja2.UndefinedError):
            tmpl.render()  # 'name' not provided

    def test_ssti_class_access_blocked(self):
        """Accessing __class__ should raise SecurityError."""
        tmpl = _create_jinja_template(SSTI_PAYLOAD_CLASS)
        with pytest.raises(jinja2.sandbox.SecurityError):
            tmpl.render()

    def test_ssti_import_blocked(self):
        """Attempting to import modules via SSTI should be blocked."""
        tmpl = _create_jinja_template(SSTI_PAYLOAD_IMPORT)
        with pytest.raises(jinja2.sandbox.SecurityError):
            tmpl.render()

    @patch.dict(os.environ, {"PF_USE_SANDBOX_FOR_JINJA": "false"})
    def test_sandbox_disabled_allows_ssti(self):
        """When sandbox is disabled, SSTI should not raise SecurityError."""
        tmpl = _create_jinja_template(SSTI_PAYLOAD_CLASS)
        result = tmpl.render()
        assert result is not None

    @patch.dict(os.environ, {"PF_USE_SANDBOX_FOR_JINJA": "true"})
    def test_sandbox_enabled_blocks_ssti(self):
        """When sandbox is explicitly enabled, SSTI should be blocked."""
        tmpl = _create_jinja_template(SSTI_PAYLOAD_CLASS)
        with pytest.raises(jinja2.sandbox.SecurityError):
            tmpl.render()


# ============================================================
# Tests for ConversationBot integration with sandbox
# ============================================================


@pytest.mark.unittest
class TestConversationBotSandbox:
    """Tests that ConversationBot uses sandboxed templates."""

    def test_bot_normal_template_works(self):
        """ConversationBot should render normal conversation templates."""
        bot = ConversationBot(
            role=ConversationRole.USER,
            model=MockModel(),
            conversation_template="Hello, {{ name }}!",
            instantiation_parameters={"name": "TestUser", "conversation_starter": "Hi there"},
        )
        assert isinstance(bot.conversation_template, jinja2.Template)

    def test_bot_ssti_template_blocked_on_render(self):
        """ConversationBot with SSTI template should block on render."""
        bot = ConversationBot(
            role=ConversationRole.ASSISTANT,
            model=MockModel(),
            conversation_template=SSTI_PAYLOAD_CLASS,
            instantiation_parameters={"chatbot_name": "Bot"},
        )
        with pytest.raises(jinja2.sandbox.SecurityError):
            bot.conversation_template.render()

    def test_bot_conversation_starter_sandboxed(self):
        """ConversationBot conversation_starter template should also be sandboxed."""
        bot = ConversationBot(
            role=ConversationRole.USER,
            model=MockModel(),
            conversation_template="Hello {{ name }}",
            instantiation_parameters={
                "name": "User",
                "conversation_starter": "Normal starter {{ name }}",
            },
        )
        # conversation_starter should be a Template (sandboxed)
        assert isinstance(bot.conversation_starter, jinja2.Template)
        result = bot.conversation_starter.render(name="User")
        assert result == "Normal starter User"

    def test_bot_ssti_conversation_starter_blocked(self):
        """SSTI in conversation_starter should be blocked on render."""
        bot = ConversationBot(
            role=ConversationRole.USER,
            model=MockModel(),
            conversation_template="Hello {{ name }}",
            instantiation_parameters={
                "name": "User",
                "conversation_starter": SSTI_PAYLOAD_CLASS,
            },
        )
        assert isinstance(bot.conversation_starter, jinja2.Template)
        with pytest.raises(jinja2.sandbox.SecurityError):
            bot.conversation_starter.render()
