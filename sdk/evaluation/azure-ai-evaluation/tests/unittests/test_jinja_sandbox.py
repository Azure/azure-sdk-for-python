import pytest
from jinja2.exceptions import SecurityError

from azure.ai.evaluation._legacy.prompty._exceptions import PromptyException
from azure.ai.evaluation._legacy.prompty._utils import render_jinja_template


@pytest.mark.unittest
class TestJinjaSandbox:
    """Regression tests: SandboxedEnvironment must block SSTI payloads (CWE-1336)."""

    def test_render_normal_template(self):
        result = render_jinja_template("Hello, {{ name }}!", name="world")
        assert result == "Hello, world!"

    def test_render_blocks_mro_traversal(self):
        with pytest.raises(PromptyException, match="SecurityError") as exc_info:
            render_jinja_template("{{ ''.__class__.__mro__ }}")
        assert isinstance(exc_info.value.__cause__, SecurityError)

    def test_render_blocks_subclass_enumeration(self):
        with pytest.raises(PromptyException, match="SecurityError") as exc_info:
            render_jinja_template("{{ ''.__class__.__mro__[1].__subclasses__() }}")
        assert isinstance(exc_info.value.__cause__, SecurityError)

    def test_render_blocks_init_globals_access(self):
        with pytest.raises(PromptyException, match="SecurityError") as exc_info:
            render_jinja_template("{{ cycler.__init__.__globals__ }}")
        assert isinstance(exc_info.value.__cause__, SecurityError)
