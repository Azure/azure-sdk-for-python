# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import sys
from types import FunctionType, MethodType

from bytecode import Instr, Label, Bytecode


def _persistent_locals_below_3_11(func):
    if not isinstance(func, (FunctionType, MethodType)):
        # If user pass a callable class instance, we will try to get the __call__ method of it, which
        # will have __code__.
        # Maybe raise error here if the instance is not callable?
        func = func.__call__

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
        # python 3.10 and above
        bytecode[-1:-1] = copy_locals_instructions + remove_param_instructions
        bytecode.extend([finally_label] + copy_locals_instructions + remove_param_instructions + [Instr("RERAISE", 0)])

    # Add __self to function args
    bytecode.argnames.insert(0, added_param)
    bytecode.argcount = bytecode.argcount + 1

    code = bytecode.to_code()
    generated_func = FunctionType(code, func.__globals__, func.__name__, func.__defaults__, func.__closure__)
    if isinstance(func, MethodType):
        return PersistentLocalsFunction(generated_func, _self=func.__self__)
    return PersistentLocalsFunction(generated_func)


class PersistentLocalsTemplate(object):
    def __init__(self):
        self._locals = {}

    @staticmethod
    def source_template_func(mock_arg):
        return mock_arg

    def target_template_func(self, mock_arg):
        try:
            return mock_arg
        finally:
            self._locals = locals().copy()  # pylint: disable=protected-access
            del self._locals['self']  # pylint: disable=protected-access


def source_template_func(mock_arg):
    return mock_arg


def target_template_func(__self, mock_arg):
    try:
        return mock_arg
    finally:
        __self._locals = locals().copy()  # pylint: disable=protected-access
        del __self._locals['__self']  # pylint: disable=protected-access


def _clear_code(bytecode, block_to_remove=None):
    for instr in bytecode:
        if isinstance(instr, Instr):
            instr.location = None

    if block_to_remove is None:
        return
    for instr in block_to_remove:
        bytecode.remove(instr)


def _persistent_locals(func):
    if isinstance(func, FunctionType):
        _self = None
        template_obj = PersistentLocalsTemplate()
        target_template = Bytecode.from_code(template_obj.target_template_func.__code__)
        source_template = Bytecode.from_code(template_obj.source_template_func.__code__)
    elif isinstance(func, MethodType):
        _self = func.__self__
        target_template = Bytecode.from_code(target_template_func.__code__)
        source_template = Bytecode.from_code(source_template_func.__code__)
    elif hasattr(func, '__call__'):
        func = func.__call__
        _self = func.__self__
        target_template = Bytecode.from_code(target_template_func.__code__)
        source_template = Bytecode.from_code(source_template_func.__code__)
    else:
        raise TypeError('func must be a function, a method or a callable object')

    bytecode = Bytecode.from_code(func.__code__)
    generated_bytecode = Bytecode.from_code(func.__code__)
    generated_bytecode.clear()

    _clear_code(target_template)
    _clear_code(source_template)
    _clear_code(bytecode)

    pre_ins, code_ins, return_ins = source_template
    code_i, return_i = target_template.index(code_ins), target_template.index(return_ins)
    generated_bytecode.extend(target_template[:code_i])
    generated_bytecode.extend(bytecode[bytecode.index(pre_ins) + 1: bytecode.index(return_ins)])
    generated_bytecode.extend(target_template[code_i + 1: return_i])
    generated_bytecode.extend(bytecode[bytecode.index(return_ins):])
    generated_bytecode.extend(target_template[return_i + 1:])

    add_param = target_template.argnames[0]
    if add_param in generated_bytecode.argnames:
        raise ValueError('The name of the first parameter of the function is not '
                         'allowed to be the same as {}'.format(add_param))
    generated_bytecode.argnames.insert(0, add_param)
    generated_bytecode.argcount += 1

    code = generated_bytecode.to_code()
    generated_func = FunctionType(
        code, func.__globals__, func.__name__, func.__defaults__, func.__closure__
    )
    return PersistentLocalsFunction(generated_func, _self=_self)


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
    if sys.version_info < (3, 11):
        return _persistent_locals_below_3_11(func)
    return _persistent_locals(func)


class PersistentLocalsFunction(object):
    """Wrapper class for the 'persistent_locals' decorator.

    Refer to the docstring of instances for help about the wrapped
    function.
    """

    def __init__(self, _func, _self=None):
        """
        :param _func: The function to be wrapped.
        :param _self: If original func is a method, _self should be provided, which is the instance of the method.
        """
        self._locals = {}
        self._self = _self
        # make function an instance method
        self._func = MethodType(_func, self)

    def __call__(self, *args, **kwargs):
        if self._self:
            return self._func(self._self, *args, **kwargs)  # pylint: disable=not-callable
        return self._func(*args, **kwargs)  # pylint: disable=not-callable
