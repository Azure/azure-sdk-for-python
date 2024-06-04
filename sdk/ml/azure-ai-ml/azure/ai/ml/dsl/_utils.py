# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import contextlib
import importlib
import inspect
import os
import re
import sys
import types
from pathlib import Path
from typing import Generator, Optional, Union

from azure.ai.ml.dsl._constants import VALID_NAME_CHARS
from azure.ai.ml.exceptions import ComponentException, ErrorCategory, ErrorTarget


def _normalize_identifier_name(name: str) -> str:
    normalized_name = name.lower()
    normalized_name = re.sub(r"[\W_]", " ", normalized_name)  # No non-word characters
    normalized_name = re.sub(" +", " ", normalized_name).strip()  # No double spaces, leading or trailing spaces
    if re.match(r"\d", normalized_name):
        normalized_name = "n" + normalized_name  # No leading digits
    return normalized_name


def _sanitize_python_variable_name(name: str) -> str:
    return _normalize_identifier_name(name).replace(" ", "_")


def is_valid_name(name: str) -> bool:
    """Indicate whether the name is a valid component name.

    :param name: The component name
    :type name: str
    :return: True if name is a valid name for a component, False otherwise
    :rtype: bool
    """
    return all(c in VALID_NAME_CHARS for c in name)


def _resolve_source_directory() -> Optional[Union[str, Path]]:
    """Resolve source directory as last customer frame's module file dir position.

    :return: The directory path of the last customer owner frame in the callstack
    :rtype: Optional[Union[str, Path]]
    """
    source_file = _resolve_source_file()
    # Fall back to current working directory if not found
    return os.getcwd() if not source_file else Path(os.path.dirname(source_file)).absolute()


def _resolve_source_file() -> Optional[Path]:
    """Resolve source file as last customer frame's module file position.


    :return: The filepath of the last customer owner frame in the callstack
    :rtype: Optional[Path]
    """
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
                return Path(str(module.__file__)).absolute() if module else None
    except Exception:  # pylint: disable=W0718
        pass
    return None


def _assert_frame_package_name(pattern: str, frame: types.FrameType) -> bool:
    """Check the package name of frame is match pattern.

    :param pattern: The pattern to match the package name of `frame` against.
    :type pattern: str
    :param frame: The stack frame
    :type frame: types.FrameType
    :return: True if the package name of the frame matches pattern, False otherwise
    :rtype: bool
    """
    # f_globals records the function's module globals of the frame. And __package__ of module must be set.
    # https://docs.python.org/3/reference/import.html#__package__
    # Although __package__ is set when importing, it may happen __package__ does not exist in globals
    # when using exec to execute.
    package_name = frame.f_globals.get("__package__", "")
    return bool(package_name and re.match(pattern, package_name))


def _relative_to(
    path: Union[str, os.PathLike], basedir: Union[str, os.PathLike], raises_if_impossible: bool = False
) -> Optional[Path]:
    """Compute the relative path under basedir.

    This is a wrapper function of Path.relative_to, by default Path.relative_to raises if path is not under basedir, In
    this function, it returns None if raises_if_impossible=False, otherwise raises.

    :param path: A path
    :type path: Union[str, os.PathLike]
    :param basedir: The base path to compute `path` relative to
    :type basedir: Union[str, os.PathLike]
    :param raises_if_impossible: Whether to raise if :attr:`pathlib.Path.relative_to` throws. Defaults to False.
    :type raises_if_impossible: bool
    :return:
        * None if raises_if_impossible is False and basedir is not a parent of path
        * path.relative_to(basedir) otherwise
    :rtype: Optional[Path]
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


@contextlib.contextmanager
def inject_sys_path(path: object) -> Generator:
    original_sys_path = sys.path.copy()
    sys.path.insert(0, str(path))
    try:
        yield
    finally:
        sys.path = original_sys_path


def _force_reload_module(module: types.ModuleType) -> types.ModuleType:
    # Reload the module except the case that module.__spec__ is None.
    # In the case module.__spec__ is None (E.g. module is __main__), reload will raise exception.
    if module.__spec__ is None:
        return module
    path = Path(module.__spec__.loader.path).parent  # type: ignore
    with inject_sys_path(path):
        return importlib.reload(module)


@contextlib.contextmanager
# pylint: disable-next=docstring-missing-return,docstring-missing-rtype
def _change_working_dir(path: Union[str, os.PathLike], mkdir: bool = True) -> Generator:
    """Context manager for changing the current working directory.

    :param path: The path to change to
    :type path: Union[str, os.PathLike]
    :param mkdir: Whether to ensure `path` exists, creating it if it doesn't exists. Defaults to True.
    :type mkdir: bool
    """

    saved_path = os.getcwd()
    if mkdir:
        os.makedirs(path, exist_ok=True)
    os.chdir(str(path))
    try:
        yield
    finally:
        os.chdir(saved_path)


def _import_component_with_working_dir(
    module_name: str, working_dir: Optional[str] = None, force_reload: bool = False
) -> types.ModuleType:
    if working_dir is None:
        working_dir = os.getcwd()
    working_dir = str(Path(working_dir).resolve().absolute())

    with _change_working_dir(working_dir, mkdir=False), inject_sys_path(working_dir):
        try:
            py_module = importlib.import_module(module_name)
        except Exception as e:
            raise ComponentException(
                message=str(e),
                no_personal_data_message="Failure importing component with working directory",
                target=ErrorTarget.COMPONENT,
                error=e,
                error_category=ErrorCategory.SYSTEM_ERROR,
            ) from e
        except BaseException as e:
            # raise base exception like system.exit as normal exception
            raise ComponentException(
                message=str(e),
                no_personal_data_message="Failure importing component with working directory",
                target=ErrorTarget.COMPONENT,
                error=e,
                error_category=ErrorCategory.USER_ERROR,
            ) from e
        loaded_module_file = Path(str(py_module.__file__)).resolve().absolute().as_posix()
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
def environment_variable_overwrite(key: str, val: str) -> Generator:
    if key in os.environ:
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
