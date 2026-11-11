# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from importlib import import_module
from importlib.util import find_spec
import json
import logging
import os
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

from cibuildwheel.options import CommandLineArguments, Options
import pytest

from ci_tools import windows_wheels


FEED = "https://pkgs.dev.azure.com/azure-sdk/public/_packaging/azure-sdk-for-net/nuget/v3/index.json"
WINDOWS = import_module(
    "cibuildwheel.platforms.windows" if find_spec("cibuildwheel.platforms") else "cibuildwheel.windows"
)
RUN = subprocess.run


@pytest.fixture
def provision(tmp_path, monkeypatch):
    for name in list(os.environ):
        if name.startswith(("CIBW_", "AZURESDK_PYTHON_", "PYO3_")):
            monkeypatch.delenv(name)
    monkeypatch.setattr(windows_wheels.sys, "platform", "win32")
    monkeypatch.setattr(windows_wheels.platform, "machine", lambda: "AMD64")
    monkeypatch.setenv("AZURESDK_PYTHON_NUGET_FEED", FEED)
    monkeypatch.setenv("AZURESDK_PYTHON_ARM64_LIBS", "true")
    monkeypatch.setenv("CIBW_CACHE_PATH", str(tmp_path / "cache with spaces"))
    package = tmp_path / "package"
    package.mkdir()
    calls = []

    def install(command, **kwargs):
        if command[0] != "nuget":
            return RUN(command, **kwargs)
        assert kwargs == {"check": True}
        assert command[command.index("-Source") + 1] == FEED
        assert "https://api.nuget.org/v3/index.json" not in command
        calls.append(command)
        name = command[2]
        version = command[command.index("-Version") + 1]
        tools = Path(command[command.index("-OutputDirectory") + 1]) / f"{name}.{version}" / "tools"
        tools.mkdir(parents=True)
        (tools / "python.exe").touch()
        libraries = tools / "libs"
        libraries.mkdir()
        suffix = "t" if name.endswith("-freethreaded") else ""
        (libraries / f"python{''.join(version.split('.')[:2])}{suffix}.lib").touch()

    monkeypatch.setattr(windows_wheels.subprocess, "run", install)
    return package, calls


def write_config(package, build="cp31{0,1,2,3,4}-*", archs="AMD64 ARM64"):
    (package / "pyproject.toml").write_text(
        f"""
[project]
name = "native-test"
version = "1.0"
requires-python = ">=3.10,<3.15"
[tool.cibuildwheel]
build = "{build}"
environment = {{ KEEP = "package", PYTHON_ARM64_LIB_DIR = "old-3.10-libs" }}
before-all = "prepare-once"
before-build = "build-hook"
[tool.cibuildwheel.windows]
archs = "{archs}"
[[tool.cibuildwheel.overrides]]
select = "cp312-*"
environment = {{ KEEP = "override" }}
""",
        encoding="utf-8",
    )


def selected_options(package, config="", environment=None):
    arguments = CommandLineArguments.defaults()
    arguments.package_dir = package
    arguments.config_file = config
    return Options(platform="windows", command_line_arguments=arguments, env=environment or os.environ)


def test_selected_versions_and_matching_arm64_libraries(provision, monkeypatch):
    package, calls = provision
    write_config(package)
    # Exercise 3.14 even on Python 3.10 hosts, whose cibuildwheel 2.x metadata
    # predates it. All other targets and versions come from the installed metadata.
    configurations = WINDOWS.get_python_configurations(
        selected_options(package).globals.build_selector, selected_options(package).globals.architectures
    )
    if not any(configuration.identifier.startswith("cp314-") for configuration in configurations):
        configurations += [
            WINDOWS.PythonConfiguration(version="3.14.8", arch=arch, identifier=f"cp314-{tag}")
            for arch, tag in (("64", "win_amd64"), ("ARM64", "win_arm64"))
        ]
    monkeypatch.setattr(WINDOWS, "get_python_configurations", lambda *args: configurations)
    monkeypatch.setenv("CIBW_ENVIRONMENT", 'KEEP="pipeline" EXTRA="$PYTHON_VERSION"')
    original = (package / "pyproject.toml").read_bytes()
    before = os.environ.copy()

    with windows_wheels.windows_wheel_config(package) as (arguments, kwargs):
        assert arguments[0] == "--config-file"
        config = Path(arguments[1])
        options = selected_options(package, str(config), kwargs["env"])
        assert options.globals.build_selector == selected_options(package).globals.build_selector
        assert options.globals.architectures == selected_options(package).globals.architectures
        for configuration in configurations:
            build = options.build_options(configuration.identifier)
            environment = build.environment.as_dictionary({"PYTHON_VERSION": configuration.version})
            assert environment["KEEP"] == "pipeline"
            assert environment["EXTRA"] == configuration.version
            assert build.before_all == "prepare-once"
            assert build.before_build == "build-hook"
            if configuration.arch == "ARM64":
                expected = (
                    Path(os.environ["CIBW_CACHE_PATH"])
                    / "nuget-cpython"
                    / f"pythonarm64.{configuration.version}"
                    / "tools"
                    / "libs"
                )
                assert Path(environment["PYTHON_ARM64_LIB_DIR"]) == expected
                assert Path(environment["PYO3_CROSS_LIB_DIR"]) == expected
                assert "PYO3_CONFIG_FILE" not in environment
                target = json.loads((expected / "build-details.json").read_text(encoding="utf-8"))
                major, minor = configuration.version.split(".")[:2]
                assert environment["PYO3_CROSS_PYTHON_VERSION"] == f"{major}.{minor}"
                assert target["language"]["version"] == f"{major}.{minor}"
                assert target["implementation"]["name"] == "cpython"
                assert target["abi"]["extension_suffix"] == f".cp{major}{minor}-win_arm64.pyd"
                assert target["abi"]["flags"] == []
            else:
                assert "PYO3_CROSS_LIB_DIR" not in environment
                assert "PYTHON_ARM64_LIB_DIR" not in environment
                assert "PYO3_CONFIG_FILE" not in environment
                assert "PYO3_CROSS_PYTHON_VERSION" not in environment
        assert os.environ == before

    assert not config.exists()
    assert (package / "pyproject.toml").read_bytes() == original
    expected = {(configuration.version, configuration.arch) for configuration in configurations}
    actual = {
        (command[command.index("-Version") + 1], "ARM64" if command[2] == "pythonarm64" else "64") for command in calls
    }
    assert actual == expected
    assert len(calls) == len(expected)
    assert {version.split(".")[1] for version, _ in actual} == {"10", "11", "12", "13", "14"}


@pytest.mark.parametrize("archs", ["AMD64 ARM64", "ARM64", "AMD64"])
@pytest.mark.parametrize("rust", ["true", "false"])
def test_cp310_only_and_cache_reuse(provision, monkeypatch, archs, rust):
    package, calls = provision
    write_config(package, build="cp310-*", archs=archs)
    monkeypatch.setenv("AZURESDK_PYTHON_ARM64_LIBS", rust)
    options = selected_options(package)
    configurations = WINDOWS.get_python_configurations(options.globals.build_selector, options.globals.architectures)
    expected_versions = {configuration.version for configuration in configurations}
    assert configurations
    assert all(configuration.identifier.startswith("cp310-") for configuration in configurations)
    for _ in range(2):
        with windows_wheels.windows_wheel_config(package) as (arguments, kwargs):
            assert bool(arguments) is (rust == "true" and "ARM64" in archs)
    assert {command[command.index("-Version") + 1] for command in calls} == expected_versions
    assert {command[2] for command in calls} == ({"python", "pythonarm64"} if "ARM64" in archs else {"python"})
    assert len(calls) == (2 if "ARM64" in archs else 1)


@pytest.mark.parametrize("platform_environment", [None, 'KEEP="windows" EXPAND="$PYTHON_VERSION"'])
def test_package_overrides_and_windows_environment_are_preserved(provision, monkeypatch, platform_environment):
    package, calls = provision
    write_config(package)
    if platform_environment:
        monkeypatch.setenv("CIBW_ENVIRONMENT_WINDOWS", platform_environment)
    original = selected_options(package)
    configurations = WINDOWS.get_python_configurations(original.globals.build_selector, original.globals.architectures)
    with windows_wheels.windows_wheel_config(package) as (arguments, kwargs):
        options = selected_options(package, arguments[1], kwargs["env"])
        for configuration in configurations:
            previous = {"PYTHON_VERSION": configuration.version}
            expected = original.build_options(configuration.identifier).environment.as_dictionary(previous)
            actual = options.build_options(configuration.identifier).environment.as_dictionary(previous)
            if configuration.arch == "ARM64":
                actual.pop("PYTHON_ARM64_LIB_DIR")
                actual.pop("PYO3_CROSS_LIB_DIR")
                actual.pop("PYO3_CROSS_PYTHON_VERSION")
                expected.pop("PYTHON_ARM64_LIB_DIR", None)
            assert actual == expected


def test_temporary_config_preserves_actual_cli_build_identifiers(provision):
    package, calls = provision
    write_config(package)
    options = selected_options(package)
    expected = [
        configuration.identifier
        for configuration in WINDOWS.get_python_configurations(
            options.globals.build_selector, options.globals.architectures
        )
    ]
    with windows_wheels.windows_wheel_config(package) as (arguments, kwargs):
        result = RUN(
            [
                sys.executable,
                "-m",
                "cibuildwheel",
                "--platform",
                "windows",
                "--print-build-identifiers",
                *arguments,
                str(package),
            ],
            capture_output=True,
            text=True,
            check=True,
            **kwargs,
        )
        assert result.stdout.splitlines() == expected


def test_free_threaded_package_and_libraries_match(provision, monkeypatch):
    package, calls = provision
    write_config(package)
    configuration = SimpleNamespace(identifier="cp314t-win_arm64", version="3.14.8", arch="ARM64")
    monkeypatch.setattr(WINDOWS, "get_python_configurations", lambda *args: [configuration])
    with windows_wheels.windows_wheel_config(package) as (arguments, kwargs):
        options = selected_options(package, arguments[1], kwargs["env"])
        environment = options.build_options(configuration.identifier).environment.as_dictionary({})
        libraries = Path(environment["PYTHON_ARM64_LIB_DIR"])
        assert libraries.parent.parent.name == "pythonarm64-freethreaded.3.14.8"
        assert (libraries / "python314t.lib").is_file()
        assert Path(environment["PYO3_CROSS_LIB_DIR"]) == libraries
        assert environment["PYO3_CROSS_PYTHON_VERSION"] == "3.14t"
        assert "PYO3_CONFIG_FILE" not in environment
        target = json.loads((libraries / "build-details.json").read_text(encoding="utf-8"))
        assert target["language"]["version"] == "3.14"
        assert target["abi"]["flags"] == ["t"]
        assert target["abi"]["extension_suffix"] == ".cp314t-win_arm64.pyd"
    assert {command[2] for command in calls} == {"python-freethreaded", "pythonarm64-freethreaded"}


@pytest.mark.parametrize("features", [["extension-module", "abi3-py310"], ["extension-module"]])
def test_arm64_does_not_override_package_abi_mode(provision, features):
    package, calls = provision
    write_config(package, build="cp310-*")
    cargo = package / "Cargo.toml"
    cargo.write_text(
        '[package]\nname = "native-test"\nversion = "1.0.0"\n'
        f'[dependencies]\npyo3 = {{ version = "0.22", features = {json.dumps(features)} }}\n',
        encoding="utf-8",
    )
    original = cargo.read_bytes()
    with windows_wheels.windows_wheel_config(package) as (arguments, kwargs):
        options = selected_options(package, arguments[1], kwargs["env"])
        for identifier in ("cp310-win_amd64", "cp310-win_arm64"):
            environment = options.build_options(identifier).environment.as_dictionary({})
            assert "PYO3_CONFIG_FILE" not in environment
            assert "PYO3_NO_PYTHON" not in environment
            if identifier.endswith("arm64"):
                assert environment["PYO3_CROSS_PYTHON_VERSION"] == "3.10"
                libraries = Path(environment["PYO3_CROSS_LIB_DIR"])
                details = json.loads((libraries / "build-details.json").read_text(encoding="utf-8"))
                assert details["language"]["version"] == "3.10"
                assert details["abi"]["flags"] == []
            else:
                assert "PYO3_CROSS_PYTHON_VERSION" not in environment
                assert "PYO3_CROSS_LIB_DIR" not in environment
        assert not list(Path(arguments[1]).parent.glob("pyo3-*.txt"))
    assert cargo.read_bytes() == original
    assert {command[2] for command in calls} == {"python", "pythonarm64"}


def test_existing_interpreter_metadata_is_not_overwritten(tmp_path):
    path = tmp_path / "build-details.json"
    original = '{"schema_version":"1.0","provided_by":"interpreter"}\n'
    path.write_text(original, encoding="utf-8")
    configuration = SimpleNamespace(identifier="cp310-win_arm64", version="3.10.11")
    windows_wheels._write_build_details(configuration, tmp_path)
    assert path.read_text(encoding="utf-8") == original


def test_package_pyo3_config_remains_authoritative(provision):
    package, calls = provision
    write_config(package, build="cp310-*")
    config = package / "pyproject.toml"
    config.write_text(
        config.read_text(encoding="utf-8") + '\n[[tool.cibuildwheel.overrides]]\nselect = "*-win_arm64"\n'
        'environment = { PYO3_CONFIG_FILE = "package-owned-config.txt" }\n',
        encoding="utf-8",
    )
    with windows_wheels.windows_wheel_config(package) as (arguments, kwargs):
        options = selected_options(package, arguments[1], kwargs["env"])
        environment = options.build_options("cp310-win_arm64").environment.as_dictionary({})
        assert environment["PYO3_CONFIG_FILE"] == "package-owned-config.txt"


def test_native_arm64_host_does_not_provision_amd64(provision, monkeypatch):
    package, calls = provision
    write_config(package, build="cp310-*", archs="ARM64")
    monkeypatch.setattr(windows_wheels.platform, "machine", lambda: "ARM64")
    with windows_wheels.windows_wheel_config(package):
        pass
    assert [command[2] for command in calls] == ["pythonarm64"]


@pytest.mark.parametrize("is_pyproject", [True, False])
@pytest.mark.parametrize("stream", [False, True])
def test_sdk_build_uses_temporary_config_and_cleans_up_on_failure(provision, monkeypatch, is_pyproject, stream):
    from ci_tools import build

    package, calls = provision
    write_config(package, build="cp310-*")
    monkeypatch.setattr(
        build.ParsedSetup,
        "from_path",
        lambda _: SimpleNamespace(
            is_pyproject=is_pyproject, ext_modules=True, uses_cibuildwheel=True, folder=str(package)
        ),
    )
    configs = []
    install = windows_wheels.subprocess.run
    monkeypatch.setattr(build.logger, "level", logging.DEBUG if stream else logging.INFO)

    def run(command, **kwargs):
        if command[0] == "nuget":
            return install(command, **kwargs)
        assert command[2] == "cibuildwheel"
        config = Path(command[command.index("--config-file") + 1])
        assert config.is_file()
        assert "CIBW_ENVIRONMENT" not in kwargs["env"]
        assert kwargs["cwd"] == str(package)
        assert kwargs["check"] is True
        assert kwargs["text"] is True
        assert ("stdout" not in kwargs) is stream
        assert kwargs["stderr"] == subprocess.STDOUT
        configs.append(config)
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(windows_wheels.subprocess, "run", run)
    with pytest.raises(subprocess.CalledProcessError):
        build.create_package(str(package), str(package / "dist"), enable_sdist=False)
    assert len(configs) == 1
    assert not configs[0].exists()


def test_sdist_only_does_not_provision_interpreters(provision, monkeypatch):
    from ci_tools import build

    package, calls = provision
    monkeypatch.setattr(
        build.ParsedSetup,
        "from_path",
        lambda _: SimpleNamespace(is_pyproject=True, ext_modules=True, uses_cibuildwheel=True, folder=str(package)),
    )
    commands = []
    monkeypatch.setattr(build, "run_logged", lambda command, **kwargs: commands.append(command))
    build.create_package(str(package), str(package / "dist"), enable_wheel=False)
    assert not calls
    assert len(commands) == 1
    assert commands[0][2] == "build"


def test_skip_requires_python_and_environment_architecture_selection(provision, monkeypatch):
    package, calls = provision
    write_config(package)
    monkeypatch.setenv("CIBW_SKIP", "cp310-*")
    monkeypatch.setenv("CIBW_PROJECT_REQUIRES_PYTHON", ">=3.10,<3.12")
    monkeypatch.setenv("CIBW_ARCHS_WINDOWS", "AMD64")
    with windows_wheels.windows_wheel_config(package) as result:
        assert result == ([], {})
    assert [(command[2], command[command.index("-Version") + 1]) for command in calls] == [("python", "3.11.9")]


@pytest.mark.parametrize("failure", ["nuget", "executable", "libraries"])
def test_provisioning_errors_propagate(provision, monkeypatch, failure):
    package, calls = provision
    write_config(package, build="cp310-*", archs="ARM64")
    install = windows_wheels.subprocess.run

    def fail(command, **kwargs):
        if failure == "nuget":
            raise subprocess.CalledProcessError(1, command)
        install(command, **kwargs)
        tools = Path(command[command.index("-OutputDirectory") + 1]) / "pythonarm64.3.10.11" / "tools"
        if failure == "executable":
            (tools / "python.exe").unlink()
        else:
            (tools / "libs" / "python310.lib").unlink()

    monkeypatch.setattr(windows_wheels.subprocess, "run", fail)
    with pytest.raises(subprocess.CalledProcessError if failure == "nuget" else RuntimeError):
        with windows_wheels.windows_wheel_config(package):
            pytest.fail("A failed provision must not start cibuildwheel")


@pytest.mark.parametrize("platform,feed", [("linux", FEED), ("darwin", FEED), ("win32", "")])
def test_non_pipeline_builds_are_unchanged(tmp_path, monkeypatch, platform, feed):
    monkeypatch.setattr(windows_wheels.sys, "platform", platform)
    monkeypatch.setenv("AZURESDK_PYTHON_NUGET_FEED", feed)
    with windows_wheels.windows_wheel_config(tmp_path) as result:
        assert result == ([], {})
