# Copyright The OpenTelemetry Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from logging import getLogger
from os import environ
from os.path import abspath, dirname, pathsep

from pkg_resources import iter_entry_points

from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.dependencies import (
    get_dist_dependency_conflicts,
)
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.distro import (
    BaseDistro,
    DefaultDistro
)
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.environment_variables import (
    OTEL_PYTHON_DISABLED_INSTRUMENTATIONS,
)
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.utils import (
    _python_path_without_directory
)
from azure.monitor.opentelemetry._vendor.v0_39b0.opentelemetry.instrumentation.version import (
    __version__
) 

logger = getLogger(__name__)


def _load_distros() -> BaseDistro:
    for entry_point in iter_entry_points("opentelemetry_distro"):
        try:
            distro = entry_point.load()()
            if not isinstance(distro, BaseDistro):
                logger.debug(
                    "%s is not an OpenTelemetry Distro. Skipping",
                    entry_point.name,
                )
                continue
            logger.debug(
                "Distribution %s will be configured", entry_point.name
            )
            return distro
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception(
                "Distribution %s configuration failed", entry_point.name
            )
            raise exc
    return DefaultDistro()


def _load_instrumentors(distro):
    package_to_exclude = environ.get(OTEL_PYTHON_DISABLED_INSTRUMENTATIONS, [])
    if isinstance(package_to_exclude, str):
        package_to_exclude = package_to_exclude.split(",")
        # to handle users entering "requests , flask" or "requests, flask" with spaces
        package_to_exclude = [x.strip() for x in package_to_exclude]

    for entry_point in iter_entry_points("opentelemetry_pre_instrument"):
        entry_point.load()()

    for entry_point in iter_entry_points("opentelemetry_instrumentor"):
        if entry_point.name in package_to_exclude:
            logger.debug(
                "Instrumentation skipped for library %s", entry_point.name
            )
            continue

        try:
            conflict = get_dist_dependency_conflicts(entry_point.dist)
            if conflict:
                logger.debug(
                    "Skipping instrumentation %s: %s",
                    entry_point.name,
                    conflict,
                )
                continue

            # tell instrumentation to not run dep checks again as we already did it above
            distro.load_instrumentor(entry_point, skip_dep_check=True)
            logger.debug("Instrumented %s", entry_point.name)
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Instrumenting of %s failed", entry_point.name)
            raise exc

    for entry_point in iter_entry_points("opentelemetry_post_instrument"):
        entry_point.load()()


def _load_configurators():
    configured = None
    for entry_point in iter_entry_points("opentelemetry_configurator"):
        if configured is not None:
            logger.warning(
                "Configuration of %s not loaded, %s already loaded",
                entry_point.name,
                configured,
            )
            continue
        try:
            entry_point.load()().configure(auto_instrumentation_version=__version__)  # type: ignore
            configured = entry_point.name
        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Configuration of %s failed", entry_point.name)
            raise exc


def initialize():
    # prevents auto-instrumentation of subprocesses if code execs another python process
    environ["PYTHONPATH"] = _python_path_without_directory(
        environ["PYTHONPATH"], dirname(abspath(__file__)), pathsep
    )

    try:
        distro = _load_distros()
        distro.configure()
        _load_configurators()
        _load_instrumentors(distro)
    except Exception:  # pylint: disable=broad-except
        logger.exception("Failed to auto initialize opentelemetry")


initialize()
