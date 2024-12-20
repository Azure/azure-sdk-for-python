# FunctionTool Specifications

FunctionTool is the utility allowing developers to provide functions within their code and invoke during streaming or running.   

## Example of Function

Here is an example of a function:
```python
def fetch_weather(location: str) -> str:
    """
    Fetches the weather information for the specified location.
 
    :param location (str): The location to fetch weather for.
    :return: Weather information as a JSON string.
    :rtype: str
    """
    # In a real-world scenario, you'd integrate with a weather API.
    mock_weather_data = {"New York": "Sunny, 25°C", "London": "Cloudy, 18°C", "Tokyo": "Rainy, 22°C"}
    weather = mock_weather_data.get(location, "Weather data not available for this location.")
    weather_json = json.dumps({"weather": weather})
    return weather_json
```

Here is an example to attach this function definition to create_agent

```python
functions = FunctionTool({fetch_weather})

agent = project_client.agents.create_agent(
    model=os.environ["MODEL_DEPLOYMENT_NAME"],
    name="my-assistant",
    instructions="You are a helpful assistant",
    tools=functions.definitions,
)
```

To verify that the SDK parsed the docstring properly, you can print the definition:

```python
[print(json.dumps(tool.as_dict(), indent=4)) for tool in functions.definitions]
```

Alternatively user can print the tools property in newly created agent:

```python
[print(json.dumps(tool.as_dict(), indent=4)) for tool in agent.tools if tool.type == "function"]
```

The terminal will display the definition as below:

```json
[
    {
        "type": "function",
        "function": {
            "name": "fetch_weather",
            "description": "Fetches the weather information for the specified location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The location to fetch weather for."
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["Celsius", "Fahrenheit", "Kelvin"],
                        "description": "The unit of temperature measurement."
                    }
                },
                "required": [
                    "location"
                ]
            }
        }
    }
]
```

## Requirements for FunctionTool

To ensure `FunctionTool` operates correctly and generates accurate function definitions that agents can reliably call, adhere to the following standards:
 
1. **Type Annotations**
   
    All function parameters and return types should be explicitly type-annotated using Python's type hinting.
 
1. **Structured Docstrings**

    Utilize a consistent docstring format similar to the example above (see also related agent samples in this repository).

    Include clear descriptions for each function and parameter.
 
1. **Supported Types**
 
    `FunctionTool` maps common Python types to their JSON Schema equivalents, ensuring accurate representation without complex type details:
 
   - **Strings and Numbers**
     - `str` → `string`
     - `int` → `integer`
     - `float` → `number`
     - `bool` → `boolean`
 
   - **Collections**
     - `list` → `array`
     - `dict` → `object`
 
   - **Nullable Types**
     - `Optional[type]` includes `null`

2. **Enum enforcement**
    
    To use an Enum, the parameter should be of type `str`. You can specify the constraint of the values in the parameter's description. In most cases, OpenAI can understand the description and apply the constraint accordingly. However, the `FunctionTool` class cannot parse the description to generate this constraint in the definition. Therefore, it is recommended to add this constraint programmatically. Here is an example:

    ```python
    def fetch_weather(location: str, unit: str) -> str:
        """
        Fetches the weather information for the specified location.
    
        :param location (str): The location to fetch weather for.
        :param unit (str): The temperature unit to use.
        :return: Weather information as a JSON string.
        :rtype: str
        """
        # In a real-world scenario, you'd integrate with a weather API.
        # Here, we'll mock the response.
        mock_weather_data = {"New York": "Sunny, 25°C", "London": "Cloudy, 18°C", "Tokyo": "Rainy, 22°C"}
        if unit == "Fahrenheit":
            mock_weather_data = {"New York": "Sunny, 77°F", "London": "Cloudy, 64°F", "Tokyo": "Rainy, 72°F"}
    
        weather = mock_weather_data.get(location, "Weather data not available for this location.")
        weather_json = json.dumps({"weather": weather})
        return weather_json
    ```

    In the example above, the function must be call with `unit` equals to `Celsius` or `Fahrenheit`.

    To apply this constraint, call:

    ```python
    functions.update_parameter_property_value(
        function_name="fetch_weather",
        parameter_name="unit",
        property_name=FunctionToolParameterProperty.ENUM,
        value=["Celsius", "Fahrenheit"],
    )
    ```
        
    This code wil introduce `enum` to unit as follow:

    ```json
    "unit": {
        "type": "string",
        "description": "The temperature unit to use.",
        "enum": [
            "Celsius",
            "Fahrenheit"
        ]
    }    
    ```


