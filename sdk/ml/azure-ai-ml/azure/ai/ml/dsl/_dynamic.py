# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import types
from inspect import Parameter, Signature
from typing import Callable, Sequence

from azure.ai.ml._ml_exceptions import ErrorCategory, ErrorTarget, ValidationException
from azure.ai.ml.entities._job.pipeline._exceptions import UnexpectedKeywordError, UserErrorException

module_logger = logging.getLogger(__name__)


class KwParameter(Parameter):
    """A keyword only parameter with a default value."""

    def __init__(self, name, default, annotation=Parameter.empty, _type="str", _optional=False):
        super().__init__(name, Parameter.KEYWORD_ONLY, default=default, annotation=annotation)
        self._type = _type
        self._optional = _optional


def _replace_function_name(func: types.FunctionType, new_name):
    """Return a function with the same body but a new name."""
    try:
        # Use the original code of the function to initialize a new code object for the new function.
        code_template = func.__code__
        # For python>=3.8, it is recommended to use `CodeType.replace`, since the interface is change in py3.8
        # See https://github.com/python/cpython/blob/384621c42f9102e31ba2c47feba144af09c989e5/Objects/codeobject.c#L646
        # The interface has been changed in py3.8, so the CodeType initializing code is invalid.
        # See https://github.com/python/cpython/blob/384621c42f9102e31ba2c47feba144af09c989e5/Objects/codeobject.c#L446
        if hasattr(code_template, "replace"):
            code = code_template.replace(co_name=new_name)
        else:
            # Before python<3.8, replace is not available, we can only initialize the code as following.
            # https://github.com/python/cpython/blob/v3.7.8/Objects/codeobject.c#L97
            code = types.CodeType(
                code_template.co_argcount,
                code_template.co_kwonlyargcount,
                code_template.co_nlocals,
                code_template.co_stacksize,
                code_template.co_flags,
                code_template.co_code,
                code_template.co_consts,
                code_template.co_names,
                code_template.co_varnames,
                code_template.co_filename,
                new_name,  # Use the new name for the new code object.
                code_template.co_firstlineno,
                code_template.co_lnotab,
                # The following two values are required for closures.
                code_template.co_freevars,
                code_template.co_cellvars,
            )
        # Initialize a new function with the code object and the new name, see the following ref for more details.
        # https://github.com/python/cpython/blob/4901fe274bc82b95dc89bcb3de8802a3dfedab32/Objects/clinic/funcobject.c.h#L30
        return types.FunctionType(
            code,
            globals=func.__globals__,
            name=new_name,
            argdefs=func.__defaults__,
            # Closure must be set to make sure free variables work.
            closure=func.__closure__,
        )
    except BaseException:
        # If the dynamic replacing failed in corner cases, simply set the two fields.
        func.__name__ = func.__qualname__ = new_name
        return func


def _assert_arg_valid(kwargs, keys, func_name):
    """Assert the arg keys are all in keys."""
    # validate whether two input name only with case difference
    lower2original_kwargs = {}
    for key in kwargs:
        lower_key = key.lower()
        if lower_key in lower2original_kwargs:
            raise UserErrorException(
                f"Invalid component input names {key} and {lower2original_kwargs[lower_key]}, which are equal ignore "
                f"case."
            )
        else:
            lower2original_kwargs[lower_key] = key

    lower2original_parameter_names = {x.lower(): x for x in keys.keys()}
    kwargs_need_to_update = []
    for key in kwargs:
        if key not in keys:
            lower_key = key.lower()
            if lower_key in lower2original_parameter_names:
                # record key that need to update
                kwargs_need_to_update.append(key)
                if key != lower_key:
                    # raise warning if name not match sanitize version
                    module_logger.warning(
                        f"Component input name {key}, treat it as {lower2original_parameter_names[lower_key]}"
                    )
            else:
                raise UnexpectedKeywordError(func_name=func_name, keyword=key, keywords=keys)
    # update kwargs to align with yaml definition
    for key in kwargs_need_to_update:
        kwargs[lower2original_parameter_names[key.lower()]] = kwargs.pop(key)


def _update_dct_if_not_exist(dst, src):
    """Update the dst dict with the source dict if the key is not in the dst
    dict."""
    for k, v in src.items():
        if k not in dst:
            dst[k] = v


def create_kw_function_from_parameters(
    func: Callable,
    parameters: Sequence[Parameter],
    func_name: str,
    documentation: str,
) -> Callable:
    """Create a new keyword only function with provided parameters."""
    if any(p.default == p.empty or p.kind != Parameter.KEYWORD_ONLY for p in parameters):
        msg = "This function only accept keyword only parameters."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.COMPONENT,
        )
    default_kwargs = {p.name: p.default for p in parameters}

    def f(**kwargs):
        # We need to make sure all keys of kwargs are valid.
        _assert_arg_valid(kwargs, default_kwargs, func_name=func_name)
        # We need to put the default args to the kwargs before invoking the original function.
        _update_dct_if_not_exist(kwargs, default_kwargs)
        return func(**kwargs)

    f = _replace_function_name(f, func_name)
    # Set the signature so jupyter notebook could have param hint by calling inspect.signature()
    f.__signature__ = Signature(parameters)
    # Set doc/name/module to make sure help(f) shows following expected result.
    # Expected help(f):
    #
    # Help on function FUNC_NAME:
    # FUNC_NAME(SIGNATURE)
    #     FUNC_DOC
    #
    f.__doc__ = documentation  # Set documentation to update FUNC_DOC in help.
    # Set module = None to avoid showing the sentence `in module 'azure.ai.ml.component._dynamic' in help.`
    # See https://github.com/python/cpython/blob/2145c8c9724287a310bc77a2760d4f1c0ca9eb0c/Lib/pydoc.py#L1757
    f.__module__ = None
    return f
