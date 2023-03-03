# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import abc
import sys
from contextlib import contextmanager
from types import FunctionType, MethodType, CodeType
from typing import Any, List, Optional, Union, Tuple, Dict
import logging

from azure.ai.ml._utils.utils import is_private_preview_enabled

logger = logging.getLogger(__name__)


class PersistentLocalsFunctionBuilder(abc.ABC):
    errors = {
        "not_callable": "func must be a function or a callable object",
        "conflict_argument": "Injected param name __self conflicts with function args {args}",
        "not_all_template_separators_used": "Not all template separators are used, "
        "please switch to a compatible version of Python.",
    }
    injected_param = "__self"

    def make_error(self, error_name: str, **kwargs):
        """Make error message with error_name and kwargs."""
        return self.errors[error_name].format(**kwargs)

    @abc.abstractmethod
    def _call(self, func, _all_kwargs) -> Tuple[Any, dict]:
        raise NotImplementedError()

    def call(self, func, _all_kwargs) -> Tuple[Any, dict]:
        """Get outputs and locals in calling func with _all_kwargs. Locals will be used to update node variable names.

        :param func: The function to execute.
        :type func: Union[FunctionType, MethodType]
        :param _all_kwargs: All kwargs to call self.func.
        :type _all_kwargs: typing.Dict[str, typing.Any]
        :return: A tuple of outputs and locals.
        :rtype: typing.Tuple[typing.Any, typing.Dict]
        """
        if isinstance(func, (FunctionType, MethodType)):
            pass
        elif hasattr(func, "__call__"):
            func = func.__call__
        else:
            raise TypeError(self.make_error("not_callable"))

        if self.injected_param in func.__code__.co_varnames:
            raise ValueError(self.make_error("conflict_argument", args=list(func.__code__.co_varnames)))

        return self._call(func, _all_kwargs)


class PersistentLocalsFunctionProfilerBuilder(PersistentLocalsFunctionBuilder):
    @staticmethod
    @contextmanager
    def replace_sys_profiler(profiler):
        """A context manager which replaces sys profiler to given profiler."""
        original_profiler = sys.getprofile()
        sys.setprofile(profiler)
        try:
            yield
        finally:
            sys.setprofile(original_profiler)

    @staticmethod
    def get_func_variable_tracer(_locals_data: Dict[str, Any], func_code: CodeType):
        """Get a tracer to trace variable names in dsl.pipeline function.

        :param _locals_data: A dict to save locals data.
        :type _locals_data: dict
        :param func_code: An code object to compare if current frame is inside user function.
        :type func_code: CodeType
        """

        def tracer(frame, event, arg):  # pylint: disable=unused-argument
            if frame.f_code == func_code and event == "return":
                # Copy the locals of user's dsl function when it returns.
                _locals_data.update(frame.f_locals.copy())

        return tracer

    def _call(self, func, _all_kwargs):
        _locals = {}
        func_variable_profiler = self.get_func_variable_tracer(_locals, func.__code__)
        with self.replace_sys_profiler(func_variable_profiler):
            outputs = func(**_all_kwargs)
        return outputs, _locals


try:
    from bytecode import Bytecode, Instr

    class PersistentLocalsFunction(object):
        def __init__(self, _func, *, _self: Optional[Any] = None, skip_locals: Optional[List[str]] = None):
            """
            :param _func: The function to be wrapped.
            :param _self: If original func is a method, _self should be provided, which is the instance of the method.
            :param skip_locals: A list of local variables to skip when saving the locals.
            """
            self.locals = {}
            self._self = _self
            # make function an instance method
            self._func = MethodType(_func, self)
            self._skip_locals = skip_locals

        def __call__(__self, *args, **kwargs):  # pylint: disable=no-self-argument
            # Use __self in case self is also passed as a named argument in kwargs
            __self.locals.clear()
            try:
                if __self._self:
                    return __self._func(__self._self, *args, **kwargs)  # pylint: disable=not-callable
                return __self._func(*args, **kwargs)  # pylint: disable=not-callable
            finally:
                # always pop skip locals even if exception is raised in user code
                if __self._skip_locals is not None:
                    for skip_local in __self._skip_locals:
                        __self.locals.pop(skip_local, None)

    def _source_template_func(mock_arg):
        return mock_arg

    def _target_template_func(__self, mock_arg):
        try:
            return mock_arg
        finally:
            __self.locals = locals().copy()

    class PersistentLocalsFunctionBytecodeBuilder(PersistentLocalsFunctionBuilder):
        def __init__(self):
            self._template_separators = self.get_instructions(_source_template_func)

            self._template_body = self._split_instructions(self.get_instructions(_target_template_func))
            # after split, the length of self._template_body will be len(self._separators) + 1
            # pop tail to make zip work
            self._template_tail = self._template_body.pop()

        # region methods depending on package bytecode
        @classmethod
        def get_instructions(cls, func):
            return list(Bytecode.from_code(func.__code__))

        @classmethod
        def is_instr_equal(cls, instr1: Instr, instr2: Instr) -> bool:
            if instr1 is None and instr2 is None:
                return True
            if instr1 is None or instr2 is None:
                return False
            if instr1.__class__ != instr2.__class__:
                return False
            if isinstance(instr1, Instr):
                return instr1.opcode == instr2.opcode and instr1.arg == instr2.arg
            # objects like Label and TryBegin
            return True

        @classmethod
        def is_body_instruction(cls, instr: Instr) -> bool:
            """Get the body execution instruction in template."""
            return instr.name == "LOAD_FAST" and instr.arg == "mock_arg"

        def _create_code(self, instructions: List[Instr], base_func: Union[FunctionType, MethodType]):
            """Create the base bytecode for the function to be generated.

            Will keep information of the function, such as name, globals, etc., but skip all instructions.
            """
            fn_code = Bytecode.from_code(base_func.__code__)
            fn_code.clear()
            fn_code.extend(instructions)
            fn_code.argcount += 1
            fn_code.argnames.insert(0, self.injected_param)
            return fn_code.to_code()

        # endregion

        def _split_instructions(self, instructions, *, skip_body_instr=False) -> List[List[Any]]:
            """Split instructions into several pieces by template separators.
            For example, in Python 3.11, the template separators will be:
            [
                Instr('RESUME', 0),  # initial instruction shared by all functions
                Instr('LOAD_FAST', 'mock_arg'),  # the body execution instruction
                Instr('RETURN_VALUE'),  # the return instruction shared by all functions
            ]
            Then we will split the target template bytecode into 4 pieces.
            For passed in bytecode, we should skip the body execution instruction, which is from template,
            and split it into 3 pieces.
            """
            pieces = []
            piece = []

            separator_iter = iter(self._template_separators)

            def get_next_separator():
                try:
                    _s = next(separator_iter)
                    if skip_body_instr and self.is_body_instruction(_s):
                        _s = next(separator_iter)
                    return _s
                except StopIteration:
                    return None

            cur_separator = get_next_separator()
            for instr in instructions:
                if self.is_instr_equal(instr, cur_separator):
                    # skip the separator
                    pieces.append(piece)
                    cur_separator = get_next_separator()
                    piece = []
                else:
                    piece.append(instr)
            pieces.append(piece)

            if cur_separator is not None:
                raise ValueError(self.make_error("not_all_template_separators_used"))
            return pieces

        def _build_func(self, func: Union[FunctionType, MethodType]) -> PersistentLocalsFunction:
            """Build a persistent locals function from the given function. Use bytecode injection to add try...finally
            statement around code to persistent the locals in the function.

            It will change the func bytecode in this way:
                def func(__self, *func_args):
                    try:
                       the func code...
                    finally:
                       __self.locals = locals().copy()

            You can get the locals in func by this code:
                builder = PersistentLocalsFunctionBuilder()
                persistent_locals_func = builder.build(your_func)
                # Execute your func
                result = persistent_locals_func(*args)
                # Get the locals in the func.
                func_locals = persistent_locals_func.locals
            """
            generated_instructions = []

            for template_piece, input_piece, separator in zip(
                self._template_body,
                self._split_instructions(self.get_instructions(func), skip_body_instr=True),
                self._template_separators,
            ):
                generated_instructions.extend(template_piece)
                generated_instructions.extend(input_piece)
                if not self.is_body_instruction(separator):
                    generated_instructions.append(separator)
            generated_instructions.extend(self._template_tail)

            generated_func = FunctionType(
                self._create_code(generated_instructions, func),
                func.__globals__,
                func.__name__,
                func.__defaults__,
                func.__closure__,
            )
            return PersistentLocalsFunction(
                generated_func,
                _self=func.__self__ if isinstance(func, MethodType) else None,
                skip_locals=[self.injected_param],
            )

        def _call(self, func, _all_kwargs) -> Tuple[Any, dict]:
            persistent_func = self._build_func(func)
            outputs = persistent_func(**_all_kwargs)
            return outputs, persistent_func.locals

except ImportError:
    # Fall back to the old implementation
    class PersistentLocalsFunctionBytecodeBuilder(PersistentLocalsFunctionProfilerBuilder):
        pass


def get_outputs_and_locals(func, _all_kwargs):
    """Get outputs and locals from self.func. Locals will be used to update node variable names.

    :param func: The function to execute.
    :type func: Union[FunctionType, MethodType]
    :param _all_kwargs: All kwargs to call self.func.
    :type _all_kwargs: typing.Dict[str, typing.Any]
    :return: A tuple of outputs and locals.
    :rtype: typing.Tuple[typing.Dict, typing.Dict]
    """
    if is_private_preview_enabled():
        return PersistentLocalsFunctionBytecodeBuilder().call(func, _all_kwargs)
    return PersistentLocalsFunctionProfilerBuilder().call(func, _all_kwargs)
