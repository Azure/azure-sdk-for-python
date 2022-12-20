# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import sys
from contextlib import contextmanager
from types import FunctionType, MethodType
from typing import Any, Callable, List, Optional, Union



@contextmanager
def replace_sys_profiler(profiler):
    """A context manager which replaces sys profiler to given profiler."""
    original_profiler = sys.getprofile()
    sys.setprofile(profiler)
    try:
        yield
    finally:
        sys.setprofile(original_profiler)


def get_func_variable_tracer(_locals_data, func_code):
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


def _get_output_and_locals_old(func, _all_kwargs):
    _locals = {}

    if not hasattr(func, '__code__'):
        if hasattr(func, '__call__'):
            func = func.__call__
        else:
            raise TypeError('func must be a function or a callable object')

    if "__self" in func.__code__.co_varnames:
        raise ValueError('Injected param name __self conflicts with function '
                         'args {}'.format(list(func.__code__.co_varnames)))

    func_variable_profiler = get_func_variable_tracer(_locals, func.__code__)
    with replace_sys_profiler(func_variable_profiler):
        outputs = func(**_all_kwargs)
    return outputs, _locals

class PersistentLocalsFunction(object):
    """Wrapper class for the 'persistent_locals' decorator.

    Refer to the docstring of instances for help about the wrapped
    function.
    """

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


try:
    from bytecode import Bytecode, Instr

    class PersistentLocalsFunctionBuilder(object):
        def __init__(self):
            self._template_separators = self._clear_location(Bytecode.from_code(_source_template_func.__code__))

            template = self._clear_location(Bytecode.from_code(_target_template_func.__code__))
            self._template_body = self.split_bytecode(template)
            # after split, len(self._template_body) will be len(self._separators) + 1
            # pop tail to make zip work
            self._template_tail = self._template_body.pop()
            self._injected_param = template.argnames[0]

        def split_bytecode(self, bytecode: Bytecode, *, skip_body_instr=False) -> List[List[Instr]]:
            """Split bytecode into several parts by template separators.
            For example, in Python 3.11, the template separators will be:
            [
                Instr('RESUME', 0),  # initial instruction shared by all functions
                Instr('LOAD_FAST', 'mock_arg'),  # the body execution instruction
                Instr('RETURN_VALUE'),  # the return instruction shared by all functions
            ]
            Then we will split the target template bytecode into 4 parts.
            For passed in bytecode, we should skip the body execution instruction, which is from template,
            and split it into 3 parts.
            """
            pieces = []
            piece = Bytecode()

            separator_iter = iter(self._template_separators)

            def get_next_separator():
                try:
                    _s = next(separator_iter)
                    if skip_body_instr and _s == self.get_body_instruction():
                        _s = next(separator_iter)
                    return _s
                except StopIteration:
                    return None

            cur_separator = get_next_separator()
            for instr in self._clear_location(bytecode):
                if instr == cur_separator:
                    # skip the separator
                    pieces.append(piece)
                    cur_separator = get_next_separator()
                    piece = Bytecode()
                else:
                    piece.append(instr)
            pieces.append(piece)

            if cur_separator is not None:
                raise ValueError("Not all template separators are used, "
                                 "please switch to a compatible version of Python.")
            return pieces

        @classmethod
        def get_body_instruction(cls):
            """Get the body execution instruction in template."""
            return Instr("LOAD_FAST", "mock_arg")

        @classmethod
        def _clear_location(cls, bytecode: Bytecode) -> Bytecode:
            """Clear location information of bytecode instructions and return the cleared bytecode."""
            for i, instr in enumerate(bytecode):
                if isinstance(instr, Instr):
                    bytecode[i] = Instr(instr.name, instr.arg)
            return bytecode

        def _create_base_bytecode(self, func: Union[FunctionType, MethodType]) -> Bytecode:
            """Create the base bytecode for the function to be generated.
            Will keep information of the function, such as name, globals, etc., but skip all instructions.
            """
            generated_bytecode = Bytecode.from_code(func.__code__)
            generated_bytecode.clear()

            if self._injected_param in generated_bytecode.argnames:
                raise ValueError("Injected param name {} conflicts with function args {}".format(
                    self._injected_param,
                    generated_bytecode.argnames)
                )
            generated_bytecode.argnames.insert(0, self._injected_param)
            generated_bytecode.argcount += 1  # pylint: disable=no-member
            return generated_bytecode

        def _build_func(self, func: Union[FunctionType, MethodType]) -> PersistentLocalsFunction:
            generated_bytecode = self._create_base_bytecode(func)

            for template_piece, input_piece, separator in zip(
                self._template_body,
                self.split_bytecode(
                    Bytecode.from_code(func.__code__),
                    skip_body_instr=True
                ),
                self._template_separators,
            ):
                generated_bytecode.extend(template_piece)
                generated_bytecode.extend(input_piece)
                if separator != self.get_body_instruction():
                    generated_bytecode.append(separator)
            generated_bytecode.extend(self._template_tail)

            generated_code = generated_bytecode.to_code()
            generated_func = FunctionType(
                generated_code,
                func.__globals__,
                func.__name__,
                func.__defaults__,
                func.__closure__
            )
            return PersistentLocalsFunction(
                generated_func,
                _self=func.__self__ if isinstance(func, MethodType) else None,
                skip_locals=[self._injected_param],
            )

        def build(self, func: Callable):
            """Build a persistent locals function from the given function.
            Use bytecode injection to add try...finally statement around code to persistent the locals in the function.

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
            if isinstance(func, (FunctionType, MethodType)):
                pass
            elif hasattr(func, '__call__'):
                func = func.__call__
            else:
                raise TypeError('func must be a function or a callable object')
            return self._build_func(func)
except ImportError:
    pass


def get_output_and_locals(func, _all_kwargs):
    """Get outputs and locals from self.func.
    Locals will be used to update node variable names.

    :param func: The function to execute.
    :type func: Union[FunctionType, MethodType]
    :param _all_kwargs: All kwargs to call self.func.
    :type _all_kwargs: typing.Dict[str, typing.Any]
    :return: A tuple of outputs and locals.
    :rtype: typing.Tuple[typing.Dict, typing.Dict]
    """
    try:
        persistent_func = PersistentLocalsFunctionBuilder().build(func)
        outputs = persistent_func(**_all_kwargs)
        return outputs, persistent_func.locals
    except NameError:
        # Fallback to the old way.
        return _get_output_and_locals_old(func, _all_kwargs)
