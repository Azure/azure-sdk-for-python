# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import os
import re
import sys
import contextlib
import inspect
import importlib
from pathlib import Path
from azure.ai.ml.dsl._constants import VALID_NAME_CHARS, DSL_COMPONENT_EXECUTION
from azure.ai.ml._ml_exceptions import ErrorTarget, ComponentException


def _normalize_identifier_name(name):
    import re

    normalized_name = name.lower()
    normalized_name = re.sub(r"[\W_]", " ", normalized_name)  # No non-word characters
    normalized_name = re.sub(" +", " ", normalized_name).strip()  # No double spaces, leading or trailing spaces
    if re.match(r"\d", normalized_name):
        normalized_name = "n" + normalized_name  # No leading digits
    return normalized_name


def _sanitize_python_variable_name(name: str):
    return _normalize_identifier_name(name).replace(" ", "_")


def is_valid_name(name: str):
    """Indicate whether the name is a valid component name."""
    return all(c in VALID_NAME_CHARS for c in name)


def _resolve_source_directory():
    """Resolve source directory as last customer frame's module file dir position."""
    source_file = _resolve_source_file()
    # Fall back to current working directory if not found
    return os.getcwd() if not source_file else Path(os.path.dirname(source_file)).absolute()


def _resolve_source_file():
    """Resolve source file as last customer frame's module file position."""
    try:
        frame_list = inspect.stack()
        # We find the last frame which is in SDK code instead of customer code or dependencies code
        # by checking whether the package name of the frame belongs to azure.ai.ml.component.
        pattern = r"(^azure\.ai\.ml(?=\..*|$).*)"
        for frame, last_frame in zip(frame_list, frame_list[1:]):
            if _assert_frame_package_name(pattern, frame.frame) and not _assert_frame_package_name(
                pattern, last_frame.frame
            ):
                module = inspect.getmodule(last_frame.frame)
                return Path(module.__file__).absolute() if module else None
    except Exception:
        return None


def _assert_frame_package_name(pattern, frame):
    """Check the package name of frame is match pattern."""
    # f_globals records the function's module globals of the frame. And __package__ of module must be set.
    # https://docs.python.org/3/reference/import.html#__package__
    # Although __package__ is set when importing, it may happen __package__ does not exist in globals
    # when using exec to execute.
    package_name = frame.f_globals.get("__package__", "")
    return True if package_name and re.match(pattern, package_name) else False


def _relative_to(path, basedir, raises_if_impossible=False):
    """Compute the relative path under basedir.

    This is a wrapper function of Path.relative_to, by default Path.relative_to raises if path is not under basedir,
    In this function, it returns None if raises_if_impossible=False, otherwise raises.

    """
    # The second resolve is to resolve possible win short path.
    path = Path(path).resolve().absolute().resolve()
    basedir = Path(basedir).resolve().absolute().resolve()
    try:
        return path.relative_to(basedir)
    except ValueError:
        if raises_if_impossible:
            raise
        return None


def dsl_component_execution() -> bool:
    """Return True if dsl component is executing."""
    if os.getenv(DSL_COMPONENT_EXECUTION, "false").lower() == "true":
        return True
    return False


def is_dsl_component(function):
    return hasattr(function, "_is_dsl_component")


@contextlib.contextmanager
def inject_sys_path(path):
    original_sys_path = sys.path.copy()
    sys.path.insert(0, str(path))
    try:
        yield
    finally:
        sys.path = original_sys_path


def _force_reload_module(module):
    # Reload the module except the case that module.__spec__ is None.
    # In the case module.__spec__ is None (E.g. module is __main__), reload will raise exception.
    if module.__spec__ is None:
        return module
    path = Path(module.__spec__.loader.path).parent
    with inject_sys_path(path):
        return importlib.reload(module)


@contextlib.contextmanager
def _change_working_dir(path, mkdir=True):
    """Context manager for changing the current working directory"""

    saved_path = os.getcwd()
    if mkdir:
        os.makedirs(path, exist_ok=True)
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(saved_path)


def _import_component_with_working_dir(module_name, working_dir=None, force_reload=False):
    if working_dir is None:
        working_dir = os.getcwd()
    working_dir = str(Path(working_dir).resolve().absolute())

    with _change_working_dir(working_dir, mkdir=False), inject_sys_path(working_dir):
        try:
            py_module = importlib.import_module(module_name)
        except Exception as e:
            raise e
        except BaseException as e:
            # raise base exception like system.exit as normal exception
            raise ComponentException(
                message=str(e),
                no_personal_data_message="Failure importing component with working directory",
                target=ErrorTarget.COMPONENT,
                error=e,
            ) from e
        loaded_module_file = Path(py_module.__file__).resolve().absolute().as_posix()
        posix_working_dir = Path(working_dir).absolute().as_posix()
        if _relative_to(loaded_module_file, posix_working_dir) is None:
            if force_reload:
                # If force_reload is True, reload the module instead of raising exception.
                # This is used when we don't care the original module with the same name.
                return importlib.reload(py_module)
            raise RuntimeError(
                "Could not import module: '{}' because module with the same name has been loaded.\n"
                "Path of the module: {}\n"
                "Working dir: {}".format(module_name, loaded_module_file, posix_working_dir)
            )
        return py_module


@contextlib.contextmanager
def environment_variable_overwrite(key, val):
    if key in os.environ.keys():
        backup_value = os.environ[key]
    else:
        backup_value = None
    os.environ[key] = val

    try:
        yield
    finally:
        if backup_value:
            os.environ[key] = backup_value
        else:
            os.environ.pop(key)
