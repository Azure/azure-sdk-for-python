# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Provision selected Windows interpreters using the pipeline's approved NuGet feed."""

from contextlib import contextmanager
from importlib import import_module
from importlib.util import find_spec
import json
import os
from pathlib import Path
import platform
import shlex
import subprocess
import sys
from tempfile import TemporaryDirectory

import tomli_w

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def _write_build_details(configuration, libraries):
    """Describe the cached interpreter without overriding the package's PyO3 ABI mode."""
    path = libraries / "build-details.json"
    if path.exists():
        return
    major, minor = configuration.version.split(".")[:2]
    free_threaded = "t-" in configuration.identifier
    abi_flags = "t" if free_threaded else ""
    details = {
        "schema_version": "1.0",
        "language": {"version": f"{major}.{minor}"},
        "implementation": {"name": "cpython"},
        "abi": {
            "flags": ["t"] if free_threaded else [],
            "extension_suffix": f".cp{major}{minor}{abi_flags}-win_arm64.pyd",
        },
    }
    path.write_text(json.dumps(details) + "\n", encoding="utf-8")


@contextmanager
def windows_wheel_config(package_dir):
    """Yield cibuildwheel arguments/environment, leaving non-pipeline builds unchanged."""
    # The pipeline sets this variable after authenticating to the approved feed.
    # Keep ordinary local builds and non-Windows builds on cibuildwheel's normal path.
    feed = os.environ.get("AZURESDK_PYTHON_NUGET_FEED")
    if sys.platform != "win32" or not feed:
        yield [], {}
        return

    from cibuildwheel.options import CommandLineArguments, EnvironmentFormat, Options

    # cibuildwheel 3+ moved its platform modules; Python 3.10 hosts still resolve 2.x.
    module = "cibuildwheel.platforms.windows" if find_spec("cibuildwheel.platforms") else "cibuildwheel.windows"
    windows = import_module(module)
    arguments = CommandLineArguments.defaults()
    arguments.package_dir = Path(package_dir)
    options = Options(platform="windows", command_line_arguments=arguments, env=os.environ)
    # Let cibuildwheel combine package config and CIBW_* variables. This keeps
    # build, skip, requires-python, and architecture selection in one authority.
    configurations = windows.get_python_configurations(options.globals.build_selector, options.globals.architectures)
    cache = Path(os.environ["CIBW_CACHE_PATH"]) / "nuget-cpython"
    cache.mkdir(parents=True, exist_ok=True)
    installed = set()
    arm64_libraries = {}

    for configuration in configurations:
        if not configuration.identifier.startswith("cp"):
            continue
        architectures = [configuration.arch]
        # An ARM64 wheel built on an AMD64 agent needs two Python packages:
        # ARM64 provides the target import libraries, while AMD64 runs the build tools.
        if configuration.arch == "ARM64" and platform.machine() != "ARM64":
            architectures.append(platform.machine())
        for arch in architectures:
            # Ask cibuildwheel for its NuGet package name so free-threaded and
            # architecture naming stays aligned with the installed version.
            package = windows.get_nuget_args(configuration.version, arch, "t-" in configuration.identifier, cache)[0]
            tools = cache / f"{package}.{configuration.version}" / "tools"
            if tools not in installed:
                if not tools.exists():
                    subprocess.run(
                        [
                            "nuget",
                            "install",
                            package,
                            "-Version",
                            configuration.version,
                            "-Source",
                            feed,
                            "-OutputDirectory",
                            str(cache),
                            "-NonInteractive",
                        ],
                        check=True,
                    )
                if not (tools / "python.exe").is_file():
                    raise RuntimeError(f"Expected CPython executable at {tools / 'python.exe'}")
                installed.add(tools)
            if arch == "ARM64" and os.environ.get("AZURESDK_PYTHON_ARM64_LIBS", "").lower() == "true":
                # PyO3 must link against the target Python's import library
                libraries = tools / "libs"
                suffix = "t" if "t-" in configuration.identifier else ""
                library = libraries / f"python{''.join(configuration.version.split('.')[:2])}{suffix}.lib"
                if not library.is_file():
                    raise RuntimeError(f"Expected ARM64 Python import library at {library}")
                arm64_libraries[configuration.identifier] = libraries

    if not arm64_libraries:
        # Interpreter packages are now cached for cibuildwheel. A temporary
        # config is only needed when target-specific ARM64 library paths are required.
        yield [], {}
        return

    config = {}
    if options.config_file_path:
        with options.config_file_path.open("rb") as source:
            config = tomllib.load(source)
    # Preserve each target's resolved environment, adding its matching Python
    # import-library path only to ARM64 targets.
    overrides = config.setdefault("tool", {}).setdefault("cibuildwheel", {}).setdefault("overrides", [])
    # Keep the generated config alive while cibuildwheel runs. TemporaryDirectory
    # removes it after success or failure.
    with TemporaryDirectory(prefix="azsdk-cibw-") as directory:
        directory = Path(directory)
        for configuration in configurations:
            with options.reader.identifier(configuration.identifier):
                environment = options.reader.get("environment", option_format=EnvironmentFormat())
            if configuration.identifier in arm64_libraries:
                libraries = arm64_libraries[configuration.identifier]
                _write_build_details(configuration, libraries)
                version = ".".join(configuration.version.split(".")[:2])
                if "t-" in configuration.identifier:
                    version += "t"
                # Let Maturin generate its ABI-aware PyO3 config from Cargo features.
                # An explicit PYO3_CONFIG_FILE bypasses that feature resolution.
                environment += (
                    f" PYTHON_ARM64_LIB_DIR={shlex.quote(libraries.as_posix())}"
                    f" PYO3_CROSS_LIB_DIR={shlex.quote(libraries.as_posix())}"
                    f" PYO3_CROSS_PYTHON_VERSION={version}"
                )
            overrides.append({"select": configuration.identifier, "environment": environment})

        environment = os.environ.copy()
        environment.pop("CIBW_ENVIRONMENT", None)
        environment.pop("CIBW_ENVIRONMENT_WINDOWS", None)
        config_path = directory / "pyproject.toml"
        config_path.write_text(tomli_w.dumps(config), encoding="utf-8")
        yield ["--config-file", str(config_path)], {"env": environment}
