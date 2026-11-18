import pytest

from azpysdk.sphinx import sphinx


@pytest.mark.parametrize(
    "namespace, import_root",
    [
        ("azure.cosmos", "azure"),
        ("corehttp", "corehttp"),
    ],
)
def test_sphinx_apidoc_scans_top_level_import_root(tmp_path, monkeypatch, namespace, import_root):
    source_root = tmp_path / "unzipped"
    (source_root / import_root).mkdir(parents=True)
    (source_root / "docgen").mkdir()

    check = sphinx()
    commands = []
    monkeypatch.setattr(check, "run_venv_command", lambda executable, command, **kwargs: commands.append(command))

    assert check.sphinx_apidoc(str(tmp_path), namespace, "python") == 0

    command = commands[0]
    assert command[command.index("-o") + 2] == str(source_root / import_root)
    assert str(source_root / import_root / "test*") in command
    assert str(source_root / import_root / "example*") in command
    assert str(source_root / import_root / "sample*") in command


def test_sphinx_apidoc_falls_back_to_sdist_root_when_import_root_is_missing(tmp_path, monkeypatch):
    source_root = tmp_path / "unzipped"
    (source_root / "docgen").mkdir(parents=True)

    check = sphinx()
    commands = []
    monkeypatch.setattr(check, "run_venv_command", lambda executable, command, **kwargs: commands.append(command))

    assert check.sphinx_apidoc(str(tmp_path), "azure.cosmos", "python") == 0

    command = commands[0]
    assert command[command.index("-o") + 2] == str(source_root)
    assert str(source_root / "test*") in command
    assert str(source_root / "example*") in command
    assert str(source_root / "sample*") in command
    assert str(source_root / "setup.py") in command
