# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from types import FunctionType, MethodType
from typing import Any, Callable, List, Optional, Union

from bytecode import Bytecode, Instr


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
            raise ValueError("Not all template separators are used, please switch to a compatible version of Python.")
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
            raise ValueError(
                "Injected param name {} conflicts with function args {}".format(
                    self._injected_param, generated_bytecode.argnames
                )
            )
        generated_bytecode.argnames.insert(0, self._injected_param)
        generated_bytecode.argcount += 1  # pylint: disable=no-member
        return generated_bytecode

    def _build_func(self, func: Union[FunctionType, MethodType]) -> PersistentLocalsFunction:
        generated_bytecode = self._create_base_bytecode(func)

        for template_piece, input_piece, separator in zip(
            self._template_body,
            self.split_bytecode(Bytecode.from_code(func.__code__), skip_body_instr=True),
            self._template_separators,
        ):
            generated_bytecode.extend(template_piece)
            generated_bytecode.extend(input_piece)
            if separator != self.get_body_instruction():
                generated_bytecode.append(separator)
        generated_bytecode.extend(self._template_tail)

        generated_code = generated_bytecode.to_code()
        generated_func = FunctionType(
            generated_code, func.__globals__, func.__name__, func.__defaults__, func.__closure__
        )
        return PersistentLocalsFunction(
            generated_func,
            _self=func.__self__ if isinstance(func, MethodType) else None,
            skip_locals=[self._injected_param],
        )

    def build(self, func: Callable):
        """Build a persistent locals function from the given function.
        Detailed impact is described in the docstring of the persistent_locals decorator.
        """
        if isinstance(func, (FunctionType, MethodType)):
            pass
        elif hasattr(func, "__call__"):
            func = func.__call__
        else:
            raise TypeError("func must be a function or a callable object")
        return self._build_func(func)


def persistent_locals(func):
    """
    Use bytecode injection to add try...finally statement around code to persistent the locals in the function.

    It will change the func bytecode like this:
        def func(__self, *func_args):
            try:
               the func code...
            finally:
               __self.locals = locals().copy()

    You can get the locals in func by this code:
        persistent_locals_func = persistent_locals(your_func)
        # Execute your func
        result = persistent_locals_func(*args)
        # Get the locals in the func.
        func_locals = persistent_locals_func.locals
    """
    return PersistentLocalsFunctionBuilder().build(func)
