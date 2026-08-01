import os

from ci_tools.variables import set_envvar_defaults


def test_set_envvar_defaults_does_not_add_public_pypi_extra_index(monkeypatch):
    monkeypatch.delenv("PIP_EXTRA_INDEX_URL", raising=False)

    set_envvar_defaults()

    assert "PIP_EXTRA_INDEX_URL" not in os.environ


def test_set_envvar_defaults_preserves_explicit_extra_index(monkeypatch):
    extra_index = "https://contoso.example/simple"
    monkeypatch.setenv("PIP_EXTRA_INDEX_URL", extra_index)

    set_envvar_defaults()

    assert os.environ["PIP_EXTRA_INDEX_URL"] == extra_index