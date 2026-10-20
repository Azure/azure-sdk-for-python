import argparse
import io
import os
import sys
import tarfile
from pathlib import Path
from unittest.mock import Mock

import pytest

from azpysdk.sphinx import sphinx
from ci_tools.parsing import ParsedSetup


@pytest.fixture
def sphinx_run(tmp_path, monkeypatch):
    package = tmp_path / "azure-cosmos"
    package.mkdir()
    source = package / "azure" / "cosmos"
    source.mkdir(parents=True)
    (source / "__init__.py").write_text("", encoding="utf-8")
    prebuilt = tmp_path / "prebuilt"
    artifacts = prebuilt / "azure-cosmos"
    artifacts.mkdir(parents=True)
    staging = tmp_path / "staging"
    staging.mkdir()

    sdist = artifacts / "azure_cosmos-4.17.1.tar.gz"
    with tarfile.open(sdist, "w:gz") as archive:
        for name, content in (
            ("README.md", b"# Cosmos documentation\n"),
            ("azure/cosmos/__init__.py", b""),
        ):
            entry = tarfile.TarInfo("azure_cosmos-4.17.1/" + name)
            entry.size = len(content)
            archive.addfile(entry, io.BytesIO(content))

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PREBUILT_WHEEL_DIR", str(prebuilt))
    monkeypatch.delenv("SETDEVVERSION", raising=False)
    monkeypatch.setattr("azpysdk.sphinx.set_envvar_defaults", lambda: None)
    monkeypatch.setattr("azpysdk.sphinx.in_ci", lambda: False)
    monkeypatch.setattr(
        "ci_tools.functions.get_interpreter_compatible_tags",
        lambda: ["cp310-abi3-manylinux_2_28_x86_64", "py3-none-any"],
    )
    monkeypatch.setattr("ci_tools.scenario.generation.get_pip_command", lambda _: [sys.executable, "-m", "pip"])
    install = Mock()
    monkeypatch.setattr("ci_tools.scenario.generation.subprocess.check_call", install)
    build = Mock(side_effect=AssertionError("Prebuilt docs must not compile the package"))
    monkeypatch.setattr("ci_tools.scenario.generation.build_and_discover_package", build)
    monkeypatch.setattr("azpysdk.sphinx.install_into_venv", Mock())

    check = sphinx()
    check.get_executable = Mock(return_value=(sys.executable, str(staging)))
    check.install_dev_reqs = Mock()
    check.sphinx_apidoc = Mock(return_value=0)
    check.sphinx_build = Mock(return_value=0)

    def run(*, cibuildwheel=False, extension=False, wheels=()):
        config = (
            '[build-system]\nrequires = ["setuptools"]\nbuild-backend = "setuptools.build_meta"\n'
            '[project]\nname = "azure-cosmos"\nversion = "4.17.1"\n'
            'description = "Docs fixture"\nrequires-python = ">=3.10"\ndependencies = []\n'
        )
        if cibuildwheel:
            config += '[tool.cibuildwheel]\nbuild = "cp310-*"\n'
        if extension:
            config += '[[tool.setuptools.ext-modules]]\nname = "azure.cosmos._extension"\nsources = ["extension.c"]\n'
        (package / "pyproject.toml").write_text(config, encoding="utf-8")
        for wheel in wheels:
            (artifacts / wheel).touch()
        check.get_targeted_directories = Mock(return_value=[ParsedSetup.from_path(str(package))])
        return check.run(argparse.Namespace(isolate=True, command="sphinx", next=False, in_ci=False))

    return argparse.Namespace(
        run=run, install=install, build=build, check=check, staging=staging, sdist=sdist, artifacts=artifacts
    )


@pytest.mark.parametrize("cibuildwheel,extension", [(True, False), (False, True), (True, True)])
def test_compiled_docs_install_compatible_wheel_and_keep_sdist_sources(sphinx_run, cibuildwheel, extension):
    wheel = "azure_cosmos-4.17.1-cp310-abi3-manylinux_2_28_x86_64.whl"
    assert (
        sphinx_run.run(
            cibuildwheel=cibuildwheel,
            extension=extension,
            wheels=(
                "azure_cosmos-4.17.1-cp310-abi3-win_amd64.whl",
                "azure_cosmos-4.17.1-cp310-abi3-manylinux_2_28_aarch64.whl",
                wheel,
            ),
        )
        == 0
    )

    sphinx_run.install.assert_called_once()
    command = sphinx_run.install.call_args.args[0]
    assert command[:4] == [sys.executable, "-m", "pip", "install"]
    assert Path(command[4]) == sphinx_run.artifacts / wheel
    assert not any(argument.endswith(".tar.gz") for argument in command)
    sphinx_run.build.assert_not_called()
    assert (sphinx_run.staging / sphinx_run.sdist.name).is_file()
    assert (sphinx_run.staging / wheel).is_file()
    sources = sphinx_run.staging / "unzipped"
    assert (sources / "README.md").read_text(encoding="utf-8") == "# Cosmos documentation\n"
    assert (sources / "azure" / "cosmos" / "__init__.py").is_file()
    assert "# Cosmos documentation" in (sources / "docgen" / "index.md").read_text(encoding="utf-8")
    sphinx_run.check.sphinx_apidoc.assert_called_once()
    sphinx_run.check.sphinx_build.assert_called_once()


def test_pure_python_docs_keep_installing_sdist(sphinx_run):
    assert sphinx_run.run(wheels=("azure_cosmos-4.17.1-py3-none-any.whl",)) == 0
    sphinx_run.install.assert_called_once()
    assert Path(sphinx_run.install.call_args.args[0][4]) == sphinx_run.sdist
    sphinx_run.build.assert_not_called()
    sphinx_run.check.sphinx_build.assert_called_once()


@pytest.mark.parametrize(
    "wheels",
    [
        (),
        ("azure_cosmos-4.17.1-cp310-abi3-win_amd64.whl",),
        ("azure_cosmos-4.17.2-cp310-abi3-manylinux_2_28_x86_64.whl",),
    ],
)
def test_compiled_docs_do_not_fall_back_to_installing_sdist(sphinx_run, wheels):
    with pytest.raises(SystemExit) as caught:
        sphinx_run.run(cibuildwheel=True, wheels=wheels)
    assert caught.value.code == 1
    sphinx_run.install.assert_not_called()
    sphinx_run.build.assert_not_called()
    sphinx_run.check.sphinx_apidoc.assert_not_called()
    sphinx_run.check.sphinx_build.assert_not_called()


def test_compiled_docs_still_require_source_archive(sphinx_run):
    os.remove(sphinx_run.sdist)
    with pytest.raises(SystemExit) as caught:
        sphinx_run.run(cibuildwheel=True, wheels=("azure_cosmos-4.17.1-cp310-abi3-manylinux_2_28_x86_64.whl",))
    assert caught.value.code == 1
    sphinx_run.install.assert_not_called()
    sphinx_run.build.assert_not_called()
