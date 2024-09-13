import inspect
import typing
from typing import Annotated
from typing_extensions import Doc

ToolsFuncSchema = dict
_TOOLS_FUNCTION_ARG_TYPE_MAP = {str: "string", bool: "boolean", int: "integer", float: "number"}

# See https://platform.openai.com/docs/guides/function-calling
# See https://peps.python.org/pep-0727/ 

def _make_tools_function_parameters_properties_schema(
      args: inspect.FullArgSpec, key: str) -> typing.Dict[str, typing.Any]:
   """
   This function returns a dictionary that represents the JSON
   that can be assigned to the "tools->function->parameters->properties" 
   element in a chat completions request body.
   All function arguments must be annotated according to https://peps.python.org/pep-0727/.
   Only "int", "float", "bool" and "str" input argument types are supported.

   Args:
      args (inspect.FullArgSpe): The function arguments
      key (str): The function argument name
      A Python function. Each function

   Returns:
      dict: A Dictionary that should be converted to JSON string and used in chat
      completions request body.
   """
   # See https://docs.python.org/3/howto/annotations.html
   # TODO: Test on Python 3.8
   ann = getattr(args, 'annotations', None)
   if ann == None:
      ann = getattr(args, '__annotations__', None)
   if ann == None:
      raise Exception("Missing annotations for function arguments")

   if key in ann:
      if ann[key].__origin__ not in _TOOLS_FUNCTION_ARG_TYPE_MAP:
         raise TypeError(f"Function arguments in tool definitions can only be `str`, `bool`, `int` or `float`. Type `{ann[key].__origin__}` is not supported")
      # TODO: Test all options here... e.g. missing Doc(), empty doc string, and raise appropriate exception
      if not ann[key].__metadata__[0].documentation:
         raise Exception(f"Missing the documentation annotation on for function argument `{key}`")
      return {
         "type": _TOOLS_FUNCTION_ARG_TYPE_MAP[ann[key].__origin__],
         "description": ann[key].__metadata__[0].documentation
      }
   else:
      raise Exception(f"Missing annotation for function argument `{key}` in tool defintion")


def _make_tools_function_schema(func: typing.Callable[..., typing.Any]) -> ToolsFuncSchema:
   """
   This function returns a dictionary that represents the JSON
   that can be assigned to the "tools->function" element in a chat completions
   request body.
   See: https://learn.microsoft.com/azure/ai-studio/reference/reference-model-inference-chat-completions#functionobject

   Args:
      func (Callable[]): A Python function. Each function
      must have a description using docstring, and function arguments
      must all be annotated according to https://peps.python.org/pep-0727/.
      Only "int", "float", "bool" and "str" input argument types are supported.

   Returns:
      dict: A Dictionary that when converted to JSON, represents the "tools.function"
      payload in a chat completions request.
   """
   argspec = inspect.getfullargspec(func)
   if argspec.varargs or argspec.varkw:
      raise ValueError("I cannot create a schema for a function with *args or **kwargs")
   args = [arg for arg in argspec.args + argspec.kwonlyargs]
   defaults = (argspec.kwonlydefaults or {}).copy()
   defaults.update(
      dict(zip(argspec.args[-len(argspec.defaults or []) :], argspec.defaults or []))
   )
   parameters_schema = {
      "type": "object",
      "properties": {argname: _make_tools_function_parameters_properties_schema(argspec, argname) for argname in args},
      "required": [arg for arg in args if not arg in defaults],
   }
   function_schema = {"name": func.__name__}
   if func.__doc__:
      function_schema["description"] = func.__doc__
   elif hasattr(func, "_class__") and func.__class__.__doc__:
      function_schema["description"] = func.__class__.__doc__
   function_schema["parameters"] = parameters_schema
   return function_schema


def _make_tools_schema(
    funcs: typing.Iterable[typing.Callable[..., typing.Any]]
) -> typing.List[typing.Dict[str, ToolsFuncSchema]]:
   """
   This function returns a dictionary that represents the JSON
   that can be assigned to the "tools" element in a chat completions
   request body.
   See: https://learn.microsoft.com/azure/ai-studio/reference/reference-model-inference-chat-completions#chatcompletiontool

   Args:
      funcs (Iterable[typing.Callable[]]): An array of one or more Python functions. Each function
      must have a description using docstring, and function arguments
      must all be annotated according to https://peps.python.org/pep-0727/.
      Only "int", "float", "bool" and "str" input argument types are supported.

   Returns:
      dict: A Dictionary that when converted to JSON, represents the "tools"
      payload in a chat completions request.
   """
   return [{
      "type": "function",
      "function": _make_tools_function_schema(func)
    } for func in funcs]


if __name__ == "__main__":

   def test_tools_function_1(
      a: Annotated[str, Doc("Doc for `a`")],
      b: Annotated[int, Doc("Doc for `b`")], # = 1, Function tools should not have defaults?
      *,
      c: Annotated[bool, Doc("Doc for `c`. Default is False")] = False,
      d: Annotated[float, Doc("Doc for `d`. Default is 2.3")] = 2.3,
   ) ->  Annotated[str, "Doc for returned value"]:
      """
      first function, first doc line
      first function, second doc line
      """
      ...

   def test_tools_function_2(
      x: Annotated[str, Doc("Doc for variable `x`")],
      y: Annotated[int, Doc("Doc for variable `y`")], # = 1, Function tools should not have defaults?
      *,
      z: Annotated[bool, Doc("Doc for variable `z`")], # = False,
   ) ->  Annotated[str, "Doc for returned value"]:
      """
      Second function doc line
      """
      ...

   def test_tools_function_3() ->  Annotated[str, "doc for returned value"]:
      """
      Third function doc line
      """
      ...


   tools = _make_tools_schema([test_tools_function_1, test_tools_function_2, test_tools_function_3])
   import json
   print(json.dumps(tools, indent=2))