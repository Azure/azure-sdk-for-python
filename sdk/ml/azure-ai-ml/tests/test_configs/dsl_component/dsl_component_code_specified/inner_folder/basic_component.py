from mldesigner import command_component


@command_component(code="..")
def basic_module(
    port1: str,
    param1: int,
):
    """ module run logic goes here """
    print("Hello Hod")
