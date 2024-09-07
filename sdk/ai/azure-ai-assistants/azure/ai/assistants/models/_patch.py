# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Customize generated code here.

Follow our quickstart for examples: https://aka.ms/azsdk/python/dpcodegen/python/customize
"""
from typing import List, Dict, Any
import inspect
import json


class AssistantFunctions:
    def __init__(self, functions: Dict[str, Any]):
        """
        Initialize AssistantFunctions with a dictionary of functions.

        :param functions: A dictionary where keys are function names and values are the function objects.
        """
        self.functions = functions
        self.definitions = self._build_function_definitions(functions)

    def _build_function_definitions(self, functions: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Build function definitions for each function provided.

        :param functions: A dictionary of functions to analyze.
        :return: A list of specifications for each function.
        """
        specs = []
        type_map = {
            'str': 'string',
            'int': 'integer',
            'float': 'number',
            'bool': 'boolean',
            'default': 'string'
        }
        
        for name, func in functions.items():
            sig = inspect.signature(func)
            params = sig.parameters
            docstring = inspect.getdoc(func)
            description = docstring.split('\n')[0] if docstring else 'No description'
            
            properties = {
                param_name: {
                    'type': type_map.get(param.annotation.__name__, type_map['default'])
                }
                for param_name, param in params.items()
                if param.annotation != inspect._empty
            }
            
            spec = {
                'type': 'function',
                'function': {
                    'name': name,
                    'description': description,
                    'parameters': {
                        'type': 'object',
                        'properties': properties,
                        'required': list(params.keys()),
                    },
                }
            }
            specs.append(spec)
        
        return specs

    def invoke_functions(self, tool_calls):
        """
        Invoke a list of function calls with their specified arguments.

        :param tool_calls: A list of tool call objects, each containing a function name and arguments.
        :return: A list of tool outputs containing the results of the function calls.
        """
        tool_outputs = []

        for tool_call in tool_calls:
            function_response = str(self._handle_function_call(tool_call.function.name, tool_call.function.arguments))
            tool_output = {
                "tool_call_id": tool_call.id,
                "output": function_response,
            }
            tool_outputs.append(tool_output)

        return tool_outputs

    def _handle_function_call(self, function_name, arguments):
        """
        Handle the invocation of a single function call with the given arguments.

        :param function_name: The name of the function to call.
        :param arguments: A JSON string of arguments to pass to the function.
        :return: The result of the function call.
        """

        if function_name in self.functions:
            function = self.functions[function_name]
            
            try:
                parsed_arguments = json.loads(arguments)
            except json.JSONDecodeError:
                parsed_arguments = {}

            if isinstance(parsed_arguments, dict):
                if not parsed_arguments:
                    return function()
                else:
                    try:
                        return function(**parsed_arguments)
                    except TypeError as e:
                        return None
            else:
                return None

        else:
            return None


__all__: List[str] = [
    "AssistantFunctions"

]  # Add all objects you want publicly available to users at this package level


def patch_sdk():
    """Do not remove from this file.

    `patch_sdk` is a last resort escape hatch that allows you to do customizations
    you can't accomplish using the techniques described in
    https://aka.ms/azsdk/python/dpcodegen/python/customize
    """
