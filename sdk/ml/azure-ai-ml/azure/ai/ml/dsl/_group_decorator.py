# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# pylint: disable=protected-access, redefined-builtin
# disable redefined-builtin to use globals/locals as argument name

# Attribute on customized group class to mark a value type as a group of inputs/outputs.
import _thread
import functools

from azure.ai.ml import Input, Output
from azure.ai.ml.constants._component import IOConstants
from azure.ai.ml.entities._inputs_outputs import GroupInput, _get_param_with_standard_annotation


def group(_cls):
    """Group decorator to make user-defined class as a group of inputs/outputs.

    Usage:
        Group a set of component inputs make component configuration easier.

        e.g. Define a group

        .. code-block:: python

            # define a group
            @dsl.group
            class ParamClass:
                str_param: str
                int_param: int = 1


            # see the help of auto-gen __init__ function
            help(ParamClass.__init__)

        e.g. Define a group with inheritance

        .. code-block:: python

            # define the parent group
            @dsl.group
            class ParentClass:
                str_param: str
                int_param: int = 1


            @dsl.group
            class GroupClass(ParentClass):
                float_param: float
                str_param: str = "test"


            # see the help of auto-gen __init__ function
            help(GroupClass.__init__)

        e.g. Define a multi-level group

        .. code-block:: python

            # define a sub group
            @dsl.group
            class SubGroupClass:
                str_param: str
                int_param: int = 1


            @dsl.group
            class ParentClass:
                param_group1: SubGroupClass
                # declare a sub group field with default
                param_group2: SubGroupClass = SubGroupClass(str_param="test")


            # see the help of auto-gen __init__ function
            help(ParentClass.__init__)

        e.g. Link and assign Group

        .. code-block:: python

            # create a sub group value
            my_param_group = SubGroupClass(str_param="dataset", int_param=2)

            # create a parent group value
            my_parent_group = ParentClass(param_group1=my_param_group)


            # option 1. use annotation to declare the input is a group.
            @pipeline
            def pipeline_func(params: SubGroupClass):
                component = component_func(
                    string_parameter=params.str_param, int_parameter=params.int_param
                )
                return component.outputs


            # create a pipeline instance
            pipeline = pipeline_func(my_param_group)


            # option 2. use default of input to declare itself a group.
            @pipeline
            def pipeline_func(params=my_param_group):
                component = component_func(
                    string_parameter=params.str_param, int_parameter=params.int_param
                )
                return component.outputs


            # create a pipeline instance
            pipeline = pipeline_func()


            # use multi-level group in pipeline.
            @pipeline
            def parent_func(params: ParentClass):
                # pass sub group to sub pipeline.
                pipeline = pipeline_func(params.param_group1)
                return pipeline.outputs

    Supported Types:
        * Primitive type: int, str, float, bool
            * Declare with python type annotation: `param: int`
            * Declare with Input annotation: `param: Input(type='integer', min=1, max=5)`

        * For sub group class
            * Sub group class should be decorated with `dsl.group`

    Restrictions:
        * Each group member's name must be public (not start with '_').
        * When use group as a pipeline input, user **MUST** write the type annotation
          or give it a non-None default value to infer the group class.
    """

    def _create_fn(name, args, body, *, globals=None, locals=None, return_type):
        """To generate function in class."""
        # Reference: Source code of dataclasses.dataclass
        # Doc link: https://docs.python.org/3/library/dataclasses.html
        # Reference code link:
        # https://github.com/python/cpython/blob/17b16e13bb444001534ed6fccb459084596c8bcf/Lib/dataclasses.py#L412
        # Note that we mutate locals when exec() is called
        if locals is None:
            locals = {}
        if "BUILTINS" not in locals:
            import builtins

            locals["BUILTINS"] = builtins
        locals["_return_type"] = return_type
        return_annotation = "->_return_type"
        args = ",".join(args)
        body = "\n".join(f"  {b}" for b in body)
        # Compute the text of the entire function.
        txt = f" def {name}({args}){return_annotation}:\n{body}"
        local_vars = ", ".join(locals.keys())
        txt = f"def __create_fn__({local_vars}):\n{txt}\n return {name}"
        ns = {}
        exec(txt, globals, ns)  # pylint: disable=exec-used # nosec
        return ns["__create_fn__"](**locals)

    def _create_init_fn(cls, fields):  # pylint: disable=unused-argument
        """Generate the __init__ function for user-defined class."""

        # Reference code link:
        # https://github.com/python/cpython/blob/17b16e13bb444001534ed6fccb459084596c8bcf/Lib/dataclasses.py#L523
        def _get_data_type_from_annotation(anno: Input):
            if isinstance(anno, GroupInput):
                return anno._group_class
            # keep original annotation for Outputs
            if isinstance(anno, Output):
                return anno
            try:
                # convert to primitive type annotation if possible
                return IOConstants.PRIMITIVE_STR_2_TYPE[anno.type]
            except KeyError:
                # otherwise, keep original annotation
                return anno

        def _get_default(key):
            # will set None as default value when default not exist so won't need to reorder the init params
            val = fields[key]
            if hasattr(val, "default"):
                return val.default
            return None

        locals = {f"_type_{key}": _get_data_type_from_annotation(val) for key, val in fields.items()}
        # Collect field defaults if val is parameter and is optional
        defaults = {f"_default_{key}": _get_default(key) for key, val in fields.items()}
        locals.update(defaults)
        # Ban positional init as we reordered the parameter.
        _init_param = ["self", "*"]
        for key in fields:
            _init_param.append(f"{key}:_type_{key}=_default_{key}")

        body_lines = [f"self.{key}={key}" for key in fields]
        # If no body lines, use 'pass'.
        if not body_lines:
            body_lines = ["pass"]
        return _create_fn("__init__", _init_param, body_lines, locals=locals, return_type=None)

    def _create_repr_fn(fields):
        """Generate the __repr__ function for user-defined class."""
        # Reference code link:
        # https://github.com/python/cpython/blob/17b16e13bb444001534ed6fccb459084596c8bcf/Lib/dataclasses.py#L582
        fn = _create_fn(
            "__repr__",
            ("self",),
            ['return self.__class__.__qualname__ + f"(' + ", ".join([f"{k}={{self.{k}!r}}" for k in fields]) + ')"'],
            return_type=str,
        )

        # This function's logic is copied from "recursive_repr" function in
        # reprlib module to avoid dependency.
        def _recursive_repr(user_function):
            # Decorator to make a repr function return "..." for a recursive
            # call.
            repr_running = set()

            @functools.wraps(user_function)
            def wrapper(self):
                key = id(self), _thread.get_ident()
                if key in repr_running:
                    return "..."
                repr_running.add(key)
                try:
                    result = user_function(self)
                finally:
                    repr_running.discard(key)
                return result

            return wrapper

        return _recursive_repr(fn)

    def _process_class(cls, all_fields):
        """Generate some functions into class."""
        setattr(cls, "__init__", _create_init_fn(cls, all_fields))
        setattr(cls, "__repr__", _create_repr_fn(all_fields))
        return cls

    def _wrap(cls):
        all_fields = _get_param_with_standard_annotation(cls)
        # Set group info on cls
        setattr(cls, IOConstants.GROUP_ATTR_NAME, GroupInput(all_fields, _group_class=cls))
        # Add init, repr, eq to class with user-defined annotation type
        return _process_class(cls, all_fields)

    return _wrap(_cls)
