import pytest
from jinja2.exceptions import SecurityError, TemplateSyntaxError

from azure.ai.evaluation._legacy.prompty._exceptions import JinjaTemplateError, PromptyException
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

    def test_sandbox_escape_is_not_reported_as_a_template_error(self):
        """SecurityError subclasses TemplateError, but a blocked escape is not an
        authoring mistake and must stay distinguishable from one."""
        with pytest.raises(PromptyException) as exc_info:
            render_jinja_template("{{ ''.__class__.__mro__ }}")
        assert not isinstance(exc_info.value, JinjaTemplateError)


@pytest.mark.unittest
class TestJinjaTemplateErrors:
    """Template authoring failures surface as JinjaTemplateError, not the generic type."""

    def test_syntax_error_raises_jinja_template_error(self):
        with pytest.raises(JinjaTemplateError, match="TemplateSyntaxError") as exc_info:
            render_jinja_template('Return {{ {"score" message} }}')
        assert isinstance(exc_info.value.__cause__, TemplateSyntaxError)

    def test_undefined_attribute_raises_jinja_template_error(self):
        with pytest.raises(JinjaTemplateError, match="UndefinedError"):
            render_jinja_template("Hello {{ missing.attribute }}")

    def test_jinja_template_error_is_still_a_prompty_exception(self):
        """Existing `except PromptyException` handlers must keep working."""
        with pytest.raises(PromptyException):
            render_jinja_template('Return {{ {"score" message} }}')

    def test_non_template_failure_stays_a_prompty_exception(self):
        class Boom:
            def __str__(self):
                raise RuntimeError("not a template problem")

        with pytest.raises(PromptyException) as exc_info:
            render_jinja_template("Hello {{ boom }}", boom=Boom())
        assert not isinstance(exc_info.value, JinjaTemplateError)
