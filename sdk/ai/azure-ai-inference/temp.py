import inspect
import typing
FuncSchema = dict
_TYPE_MAP = {str: "string", bool: "boolean", int: "integer", float: "number"}

def _make_schema(args: inspect.FullArgSpec, key: str) -> typing.Dict[str, typing.Any]:
    if key in args.annotations:
        try:
            return {"type": _TYPE_MAP[args.annotations[key]]}
        except KeyError:
            return schema(args.annotations[key].__init__)
    else:
        return {}

def functions(
    funcs: typing.Iterable[typing.Callable[..., typing.Any]]
) -> typing.List[typing.Dict[str, FuncSchema]]:
    return [{
            "name": func.__name__,
            "parameters": schema(func)
    }
    for func in funcs]

def schema(func: typing.Callable[..., typing.Any]) -> FuncSchema:
    argspec = inspect.getfullargspec(func)
    if argspec.varargs or argspec.varkw:
        raise ValueError(
            "I cannot create a schema for a function with *args or **kwargs"
        )
    args = [arg for arg in argspec.args + argspec.kwonlyargs]
    defaults = (argspec.kwonlydefaults or {}).copy()
    defaults.update(
        dict(zip(argspec.args[-len(argspec.defaults or []) :], argspec.defaults or []))
    )
    function_schema = {
        "type": "object",
        "properties": {argname: _make_schema(argspec, argname) for argname in args},
        "required": [arg for arg in args if not arg in defaults],
    }
    if func.__doc__:
        function_schema["description"] = func.__doc__
    elif hasattr(func, "_class__") and func.__class__.__doc__:
        function_schema["description"] = func.__class__.__doc__
    return function_schema

if __name__ == "__main__":
    class Thing:
        """Things are cool, right!"""
        def __init__(self, foo: str, *, bar: int = 7):
            ...
    def do_smurf(a: str, thing: Thing, b: int = 1, *, c: bool = False, d) -> str:
        """
        Do smurfy things to a to d:s

        Parameters:
        a (str): my first input argument.
        thing (Thing): My second input argument.
        b (int): My third input argument.
        c (bool): My fourth input argument.
        d: My fifth input argument.

        Returns:
        str: Some string.
        """
        ...

    s = functions([do_smurf])
    import json
    print(json.dumps(s, indent=2))