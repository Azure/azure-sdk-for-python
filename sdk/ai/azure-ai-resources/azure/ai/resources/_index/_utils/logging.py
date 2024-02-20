# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""Logging utilities."""
import inspect
import logging
import sys
from contextlib import contextmanager, suppress
from functools import lru_cache
from typing import Optional

import pkg_resources  # type: ignore[import]

COMPONENT_NAME = "azure.ai.resources._index"
instrumentation_key = ""

# Gather versions of packages that are used in the RAG codebase to aid in discovering
# compatibility issues and advising users on how to determine compatible versions
packages_versions_for_compatibility = {
    "azure-ai-generative": "",
    "langchain": "",
    "azure-search-documents": ""
}

for package in packages_versions_for_compatibility:
    with suppress(Exception):
        packages_versions_for_compatibility[package] = pkg_resources.get_distribution(package).version

langchain_version = packages_versions_for_compatibility["langchain"]
version = packages_versions_for_compatibility["azure-ai-generative"]

default_custom_dimensions = {"source": COMPONENT_NAME, "version": version, "langchain_version": langchain_version, "azure-search-documents_version": packages_versions_for_compatibility.get("azure-search-documents")}
STACK_FMT = "%s, line %d in function %s."
DEFAULT_ACTIVITY_TYPE = "InternalCall"

try:
    import os

    from azureml._base_sdk_common import _ClientSessionId
    from azureml.telemetry import INSTRUMENTATION_KEY, get_telemetry_log_handler
    from azureml.telemetry.activity import ActivityLoggerAdapter
    from azureml.telemetry.activity import log_activity as _log_activity

    session_id = _ClientSessionId
    current_folder = os.path.dirname(os.path.realpath(__file__))
    telemetry_config_path = os.path.join(current_folder, "_telemetry.json")

    verbosity = logging.INFO
    instrumentation_key = INSTRUMENTATION_KEY
    telemetry_enabled = True
except Exception:
    from uuid import uuid4

    _ClientSessionId = str(uuid4())

    verbosity = 0
    telemetry_enabled = False

    class ActivityLoggerAdapter(logging.LoggerAdapter):  # type: ignore[no-redef]
        """Make logger look like Activity Logger."""

        def __init__(self, logger, activity_info):
            """Initialize a new instance of the class."""
            self._activity_info = activity_info
            super().__init__(logger, None)

        @property
        def activity_info(self):
            """Return current activity info."""
            return self._activity_info

        def process(self, msg, kwargs):
            """Process the log message."""
            return msg, kwargs


@contextmanager
def _run_without_logging(logger, activity_name, activity_type, custom_dimensions):
    yield ActivityLoggerAdapter(logger, {})


known_modules = [
    "crack_and_chunk",
    "create_faiss_index",
    "create_promptflow",
    "data_import_acs",
    "git_clone",
    "generate_embeddings_parallel",
    "qa_data_generation",
    "register_mlindex_asset",
    "update_acs_index"
]


class LoggerFactory:
    """Factory for creating loggers."""

    def __init__(self, stdout=False, mlflow=True, verbosity=logging.INFO):
        """Initialize the logger factory."""
        self.loggers = {}
        self.verbosity = verbosity
        self.stdout = None
        self.with_stdout(stdout)
        self.appinsights = None
        self.azuremonitor = None
        try:
            import mlflow
            self.mlflow = mlflow
        except Exception:
            self.mlflow = False

    def with_mlflow(self, mlflow=True):
        """Set whether to log to mlflow."""
        try:
            import mlflow
            self.mlflow = mlflow
        except Exception:
            print("MLFlow is not installed, skipping mlflow logging.")
            self.mlflow = False
        return self

    def with_stdout(self, stdout=True, verbosity=logging.INFO):
        """Set whether to log to stdout."""
        if stdout:
            # Add stdout handler to any loggers created before enabling stdout.
            self.stdout = logging.StreamHandler(stream=sys.stdout)
            self.stdout.setLevel(verbosity)
            self.stdout.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)-8s %(name)s - %(message)s (%(filename)s:%(lineno)s)", "%Y-%m-%d %H:%M:%S"))
            for logger in self.loggers.values():
                if self.stdout:
                    logger.addHandler(self.stdout)
        return self

    def with_appinsights(self, verbosity=logging.INFO):
        """Set whether to log track_* events to appinsights."""
        if telemetry_enabled and self.appinsights is None:
            import atexit

            self.appinsights = get_telemetry_log_handler(component_name=COMPONENT_NAME, path=telemetry_config_path)
            atexit.register(self.appinsights.flush)

    def get_logger(self, name, level=None):
        """Get a logger with the given name and level."""
        if name not in self.loggers:
            logger = logging.getLogger(f"azure.ai.resources._index.{name}")
            if level is not None:
                logger.setLevel(level)
            else:
                logger.setLevel(self.verbosity)
            if self.stdout:
                logger.addHandler(self.stdout)
            self.loggers[name] = logger
        return self.loggers[name]

    def track_activity(self, logger, name, activity_type=DEFAULT_ACTIVITY_TYPE, custom_dimensions={}):
        """Track the activity of the given logger."""
        if self.appinsights:
            stack = self.get_stack()
            custom_dimensions.update({**default_custom_dimensions, "trace": stack})
            run_info = self._try_get_run_info()
            if run_info is not None:
                custom_dimensions.update(run_info)
            child_logger = logger.getChild(name)
            child_logger.addHandler(self.appinsights)
            return _log_activity(child_logger, name, activity_type, custom_dimensions)
        else:
            return _run_without_logging(logger, name, activity_type, custom_dimensions)

    def telemetry_info(self, logger, message, custom_dimensions={}):
        """Track info with given logger."""
        if self.appinsights:
            payload = custom_dimensions
            payload.update(default_custom_dimensions)
            child_logger = logger.getChild("appinsights")
            child_logger.addHandler(self.appinsights)
            if ActivityLoggerAdapter:
                activity_logger = ActivityLoggerAdapter(child_logger, payload)
                activity_logger.info(message)

    def telemetry_error(self, logger, message, custom_dimensions={}):
        """Track error with given logger."""
        if self.appinsights:
            payload = custom_dimensions
            payload.update(default_custom_dimensions)
            child_logger = logger.getChild("appinsights")
            child_logger.addHandler(self.appinsights)
            if ActivityLoggerAdapter:
                activity_logger = ActivityLoggerAdapter(child_logger, payload)
                activity_logger.error(message)

    @staticmethod
    def get_stack(limit=3, start=1) -> Optional[str]:
        """Get the stack trace as a string."""
        try:
            stack = inspect.stack()
            # The index of the first frame to print.
            begin = start + 2
            # The index of the last frame to print.
            end = min(begin + limit, len(stack)) if limit else len(stack)

            lines = []
            for frame in stack[begin:end]:
                file, line, func = frame[1:4]
                parts = file.rsplit("\\", 4)
                parts = parts if len(parts) > 1 else file.rsplit("/", 4)
                file = "|".join(parts[-3:])
                lines.append(STACK_FMT % (file, line, func))
            return "\n".join(lines)
        except Exception:
            pass
        return None

    @staticmethod
    @lru_cache(maxsize=1)
    def _try_get_run_info():
        info = {
            "subscription": os.environ.get("AZUREML_ARM_SUBSCRIPTION", ""),
            "run_id": os.environ.get("AZUREML_RUN_ID", ""),
            "resource_group": os.environ.get("AZUREML_ARM_RESOURCEGROUP", ""),
            "workspace_name": os.environ.get("AZUREML_ARM_WORKSPACE_NAME", ""),
            "experiment_id": os.environ.get("AZUREML_EXPERIMENT_ID", "")
        }
        try:
            import re
            location = os.environ.get("AZUREML_SERVICE_ENDPOINT")
            location = re.compile("//(.*?)\\.").search(location).group(1)
        except Exception:
            location = os.environ.get("AZUREML_SERVICE_ENDPOINT", "")
        info["location"] = location
        try:
            from azureml.core import Run
            run: Run = Run.get_context() # type: ignore[annotation-unchecked]
            if hasattr(run, "experiment"):
                info["parent_run_id"] = run.properties.get("azureml.pipelinerunid", "Unknown")
                info["mlIndexAssetKind"] = run.properties.get("azureml.mlIndexAssetKind", "Unknown")
                info["mlIndexAssetSource"] = run.properties.get("azureml.mlIndexAssetSource", "Unknown")
                module_name = run.properties.get("azureml.moduleName", "Unknown")
                info["moduleName"] = module_name if module_name in known_modules or module_name.startswith("llm_") else "Unknown"
                if info["moduleName"] != "Unknown":
                    info["moduleVersion"] = run.properties.get("azureml.moduleVersion", "Unknown")
        except Exception:
            pass
        return info


_logger_factory = LoggerFactory()


def enable_stdout_logging(verbosity=logging.INFO):
    """Enable logging to stdout."""
    _logger_factory.with_stdout(True, verbosity)


def enable_appinsights_logging():
    """Enable logging to appinsights."""
    _logger_factory.with_appinsights()


def get_logger(name, level=logging.INFO):
    """Get a logger with the given name and level."""
    return _logger_factory.get_logger(name, level)


def track_activity(logger, name, activity_type=DEFAULT_ACTIVITY_TYPE, custom_dimensions={}):
    """Track the activity with given logger."""
    enable_appinsights_logging()
    return _logger_factory.track_activity(logger, name, activity_type, custom_dimensions)


def track_info(logger, message, custom_dimensions={}):
    """Track info with given logger."""
    return _logger_factory.telemetry_info(logger, message, custom_dimensions)


def track_error(logger, message, custom_dimensions={}):
    """Track error with given logger."""
    return _logger_factory.telemetry_error(logger, message, custom_dimensions)


# def get_tracer(name):
#     """Get a tracer with the given name"""
#     return trace.get_tracer(name)


def disable_mlflow():
    """Disable mlflow logging."""
    _logger_factory.mlflow = False


def mlflow_enabled():
    """Check if mlflow logging is enabled."""
    return _logger_factory.mlflow


def safe_mlflow_log_metric(*args, logger, **kwargs):
    """Log metric to mlflow if enabled."""
    if mlflow_enabled():
        import mlflow
        try:
            if mlflow.active_run():
                mlflow.log_metric(*args, **kwargs)
        except Exception as e:
            message = str(e)
            if "Max retries exceeded" in message:
                logger.warning("MLFlow endpoint is not available right now, skipping log_metrics.")
            else:
                raise


@contextmanager
def safe_mlflow_start_run(*args, logger, **kwargs):
    """Start mlflow run if enabled."""
    if mlflow_enabled():
        import mlflow
        try:
            with mlflow.start_run() as run:
                yield run
        except Exception as e:
            message = str(e)
            if "Max retries exceeded" in message:
                logger.warning("MLFlow endpoint is not available right now, skipping start_run.")
                yield None
            else:
                raise
    else:
        yield None
