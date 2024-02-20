# this file shall not be imported by any other files
from mldesigner import Output, command_component


@command_component
def basic_component_func(bool_param: bool, int_param: int, float_param: float, str_param: str):
    print("bool_param:", bool_param)
    print("int_param:", int_param)
    print("float_param:", float_param)
    print("str_param:", str_param)


@command_component
def component_with_boolean_output() -> Output(type="boolean", is_control=True):
    return True


@command_component
def component_with_integer_output() -> Output(type="integer", is_control=True):
    return 0


@command_component
def component_with_number_output() -> Output(type="number", is_control=True):
    return 3.14


@command_component
def component_with_string_output() -> Output(type="string", is_control=True):
    return "string"
