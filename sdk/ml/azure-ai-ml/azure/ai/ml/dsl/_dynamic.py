# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import logging
import types
from inspect import Parameter, Signature
from typing import Any, Callable, Dict, Sequence, cast

from azure.ai.ml.entities import Component
from azure.ai.ml.exceptions import ErrorCategory, ErrorTarget, UnexpectedKeywordError, ValidationException

module_logger = logging.getLogger(__name__)


class KwParameter(Parameter):
    """A keyword-only parameter with a default value.

    :param name: The name of the parameter.
    :type name: str
    :param default: The default value of the parameter.
    :param annotation: The annotation type of the parameter, defaults to `Parameter.empty`.
    :type annotation: Any
    :param _type: The type of the parameter, defaults to "str".
    :type _type: str
    :param _optional: Indicates if the parameter is optional, defaults to False.
    :type _optional: bool
    """

    def __init__(
        self, name: str, default: Any, annotation: Any = Parameter.empty, _type: str = "str", _optional: bool = False
    ) -> None:
        super().__init__(name, Parameter.KEYWORD_ONLY, default=default, annotation=annotation)
        self._type = _type
        self._optional = _optional


def _replace_function_name(func: types.FunctionType, new_name: str) -> types.FunctionType:
    """Replaces the name of a function with a new name

    :param func: The function to update
    :type func: types.FunctionType
    :param new_name: The new function name
    :type new_name: str
    :return: The function with a replaced name, but otherwise unchanged body
    :rtype: types.FunctionType
    """
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

            # Bug Item number: 2881688
            code = types.CodeType(  # type: ignore
                code_template.co_argcount,
                code_template.co_kwonlyargcount,
                code_template.co_nlocals,
                code_template.co_stacksize,
                code_template.co_flags,
                code_template.co_code,  # type: ignore
                code_template.co_consts,  # type: ignore
                code_template.co_names,
                code_template.co_varnames,
                code_template.co_filename,  # type: ignore
                new_name,  # Use the new name for the new code object.
                code_template.co_firstlineno,  # type: ignore
                code_template.co_lnotab,  # type: ignore
                # The following two values are required for closures.
                code_template.co_freevars,  # type: ignore
                code_template.co_cellvars,  # type: ignore
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
    except BaseException:  # pylint: disable=W0718
        # If the dynamic replacing failed in corner cases, simply set the two fields.
        func.__name__ = func.__qualname__ = new_name
        return func


# pylint: disable-next=docstring-missing-param
def _assert_arg_valid(kwargs: dict, keys: list, func_name: str) -> None:
    """Assert the arg keys are all in keys."""
    # pylint: disable=protected-access
    # validate component input names
    Component._validate_io_names(kwargs, raise_error=True)
    lower2original_parameter_names = {x.lower(): x for x in keys}
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
                        "Component input name %s, treat it as %s", key, lower2original_parameter_names[lower_key]
                    )
            else:
                raise UnexpectedKeywordError(func_name=func_name, keyword=key, keywords=keys)
    # update kwargs to align with yaml definition
    for key in kwargs_need_to_update:
        kwargs[lower2original_parameter_names[key.lower()]] = kwargs.pop(key)


def _update_dct_if_not_exist(dst: Dict, src: Dict) -> None:
    """Computes the union of `src` and `dst`, in-place within `dst`

    If a key exists in `dst` and `src` the value in `dst` is preserved

    :param dst: The destination to compute the union within
    :type dst: Dict
    :param src: A dictionary to include in the union
    :type src: Dict
    """
    for k, v in src.items():
        if k not in dst:
            dst[k] = v


def create_kw_function_from_parameters(
    func: Callable,
    parameters: Sequence[Parameter],
    flattened_group_keys: list,
    func_name: str,
    documentation: str,
) -> Callable:
    """Create a new keyword-only function with provided parameters.

    :param func: The original function to be wrapped.
    :type func: Callable
    :param parameters: The sequence of parameters for the new function.
    :type parameters: Sequence[Parameter]
    :param flattened_group_keys: The list of valid group keys.
    :type flattened_group_keys: list
    :param func_name: The name of the new function.
    :type func_name: str
    :param documentation: The documentation string for the new function.
    :type documentation: str
    :return: The new keyword-only function.
    :rtype: Callable
    :raises ValidationException: If the provided function parameters are not keyword-only.
    """
    if any(p.default == p.empty or p.kind != Parameter.KEYWORD_ONLY for p in parameters):
        msg = "This function only accept keyword only parameters."
        raise ValidationException(
            message=msg,
            no_personal_data_message=msg,
            error_category=ErrorCategory.USER_ERROR,
            target=ErrorTarget.COMPONENT,
        )
    default_kwargs = {p.name: p.default for p in parameters}

    def f(**kwargs: Any) -> Any:
        # We need to make sure all keys of kwargs are valid.
        # Merge valid group keys with original keys.
        _assert_arg_valid(kwargs, [*list(default_kwargs.keys()), *flattened_group_keys], func_name=func_name)
        # We need to put the default args to the kwargs before invoking the original function.
        _update_dct_if_not_exist(kwargs, default_kwargs)
        return func(**kwargs)

    f = _replace_function_name(cast(types.FunctionType, f), func_name)
    # Set the signature so jupyter notebook could have param hint by calling inspect.signature()
    # Bug Item number: 2883223
    f.__signature__ = Signature(parameters)  # type: ignore
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
    f.__module__ = None  # type: ignore
    return f
