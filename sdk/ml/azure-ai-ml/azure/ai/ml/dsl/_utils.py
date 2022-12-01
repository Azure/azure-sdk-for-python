# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import contextlib
import importlib
import inspect
import os
import re
import sys
from pathlib import Path
from types import MethodType, FunctionType

from bytecode import Label, Instr, Bytecode

from azure.ai.ml.dsl._constants import VALID_NAME_CHARS
from azure.ai.ml.exceptions import ComponentException, ErrorCategory, ErrorTarget


def _normalize_identifier_name(name):
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
    """Resolve source directory as last customer frame's module file dir
    position."""
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
    except Exception:  # pylint: disable=broad-except
        return None


def _assert_frame_package_name(pattern, frame):
    """Check the package name of frame is match pattern."""
    # f_globals records the function's module globals of the frame. And __package__ of module must be set.
    # https://docs.python.org/3/reference/import.html#__package__
    # Although __package__ is set when importing, it may happen __package__ does not exist in globals
    # when using exec to execute.
    package_name = frame.f_globals.get("__package__", "")
    return package_name and re.match(pattern, package_name)


def _relative_to(path, basedir, raises_if_impossible=False):
    """Compute the relative path under basedir.

    This is a wrapper function of Path.relative_to, by default
    Path.relative_to raises if path is not under basedir, In this
    function, it returns None if raises_if_impossible=False, otherwise
    raises.
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
    """Context manager for changing the current working directory."""

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


def persistent_locals(func):
    """
    Use bytecode injection to add try...finally statement around code to persistent the locals in the function.

    It will change the func bytecode like this:
        def func(__self, *func_args):
            try:
               the func code...
            finally:
               __self._locals = locals().copy()
               del __self._locals['__self']

    You can get the locals in func by this code:
        persistent_locals_func = persistent_locals(your_func)
        # Execute your func
        result = persistent_locals_func(*args)
        # Get the locals in the func.
        func_locals = persistent_locals_func._locals
    """
    bytecode = Bytecode.from_code(func.__code__)

    # Add `try` at the begining of the code
    finally_label = Label()
    bytecode.insert(0, Instr("SETUP_FINALLY", finally_label))
    # Add `final` at the end of the code
    added_param = '__self'

    copy_locals_instructions = [
        # __self._locals = locals().copy()
        Instr("LOAD_GLOBAL", 'locals'),
        Instr("CALL_FUNCTION", 0),
        Instr("LOAD_ATTR", 'copy'),
        Instr("CALL_FUNCTION", 0),
        Instr("LOAD_FAST", added_param),
        Instr("STORE_ATTR", '_locals'),
    ]

    remove_param_instructions = [
        # del __self._locals['__self']
        Instr("LOAD_FAST", added_param),
        Instr("LOAD_ATTR", '_locals'),
        Instr("LOAD_CONST", added_param),
        Instr("DELETE_SUBSCR"),
    ]

    if sys.version_info < (3, 8):
        # python 3.6 and 3.7
        bytecode.extend([finally_label] + copy_locals_instructions + remove_param_instructions +
                        [Instr("END_FINALLY"), Instr("LOAD_CONST", None), Instr("RETURN_VALUE")])
    elif sys.version_info < (3, 9):
        # In python 3.8, add new instruction CALL_FINALLY
        # https://docs.python.org/3.8/library/dis.html?highlight=call_finally#opcode-CALL_FINALLY
        bytecode.insert(-1, Instr("CALL_FINALLY", finally_label))
        bytecode.extend(
            [finally_label] + copy_locals_instructions + remove_param_instructions +
            [Instr("END_FINALLY"), Instr("LOAD_CONST", None), Instr("RETURN_VALUE")])
    elif sys.version_info < (3, 10):
        # In python 3.9, add new instruction RERAISE and CALL_FINALLY is removed.
        # https://docs.python.org/3.9/library/dis.html#opcode-RERAISE
        raise_error = Label()
        extend_instructions = \
            copy_locals_instructions + remove_param_instructions + \
            [Instr("JUMP_FORWARD", raise_error), finally_label] + \
            copy_locals_instructions + remove_param_instructions + [Instr("RERAISE"), raise_error]
        bytecode[-1:-1] = extend_instructions
    else:
        # python 3.10
        bytecode[-1:-1] = copy_locals_instructions + remove_param_instructions
        bytecode.extend([finally_label] + copy_locals_instructions + remove_param_instructions + [Instr("RERAISE", 0)])
    # Add __self to function args
    bytecode.argnames.insert(0, added_param)
    bytecode.argcount = bytecode.argcount + 1
    code = bytecode.to_code()
    func = FunctionType(code, func.__globals__, func.__name__, func.__defaults__, func.__closure__)
    return PersistentLocalsFunction(func)


class PersistentLocalsFunction(object):
    """Wrapper class for the 'persistent_locals' decorator.

    Refer to the docstring of instances for help about the wrapped
    function.
    """

    def __init__(self, func):
        self._locals = {}
        # make function an instance method
        self._func = MethodType(func, self)

    def __call__(self, *args, **kwargs):
        return self._func(*args, **kwargs)  # pylint: disable=not-callable
