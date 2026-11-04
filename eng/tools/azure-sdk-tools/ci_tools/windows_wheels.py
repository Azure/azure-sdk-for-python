# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Provision selected Windows interpreters using the pipeline's approved NuGet feed."""

from contextlib import contextmanager
from importlib import import_module
from importlib.util import find_spec
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


@contextmanager
def windows_wheel_config(package_dir):
    """Yield cibuildwheel arguments/environment, leaving non-pipeline builds unchanged."""
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
    # Get combinations of Python version and CPU architecture from cibuildwheel options
    configurations = windows.get_python_configurations(options.globals.build_selector, options.globals.architectures)
    cache = Path(os.environ["CIBW_CACHE_PATH"]) / "nuget-cpython"
    cache.mkdir(parents=True, exist_ok=True)
    installed = set()
    arm64_libraries = {}

    for configuration in configurations:
        if not configuration.identifier.startswith("cp"):
            continue
        architectures = [configuration.arch]
        if configuration.arch == "ARM64" and platform.machine() != "ARM64":
            architectures.append(platform.machine())
        for arch in architectures:
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
                libraries = tools / "libs"
                suffix = "t" if "t-" in configuration.identifier else ""
                library = libraries / f"python{''.join(configuration.version.split('.')[:2])}{suffix}.lib"
                if not library.is_file():
                    raise RuntimeError(f"Expected ARM64 Python import library at {library}")
                arm64_libraries[configuration.identifier] = libraries

    if not arm64_libraries:
        yield [], {}
        return

    config = {}
    if options.config_file_path:
        with options.config_file_path.open("rb") as source:
            config = tomllib.load(source)
    overrides = config.setdefault("tool", {}).setdefault("cibuildwheel", {}).setdefault("overrides", [])
    for configuration in configurations:
        # Freeze the resolved environment, including environment-variable and package
        # overrides, before adding target-specific paths. Do not evaluate build-time commands.
        with options.reader.identifier(configuration.identifier):
            environment = options.reader.get("environment", option_format=EnvironmentFormat())
        if configuration.identifier in arm64_libraries:
            libraries = shlex.quote(arm64_libraries[configuration.identifier].as_posix())
            environment += f" PYTHON_ARM64_LIB_DIR={libraries} PYO3_CROSS_LIB_DIR={libraries}"
        overrides.append({"select": configuration.identifier, "environment": environment})

    environment = os.environ.copy()
    environment.pop("CIBW_ENVIRONMENT", None)
    environment.pop("CIBW_ENVIRONMENT_WINDOWS", None)
    with TemporaryDirectory(prefix="azsdk-cibw-") as directory:
        config_path = Path(directory) / "pyproject.toml"
        config_path.write_text(tomli_w.dumps(config), encoding="utf-8")
        yield ["--config-file", str(config_path)], {"env": environment}
