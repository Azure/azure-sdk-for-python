from typing import Annotated, get_type_hints

class Doc:
    def __init__(self, doc):
        self.doc = doc

def example_function(a: Annotated[str, Doc("Doc for variable `a`")]):
    pass

# Extract type hints
type_hints = get_type_hints(example_function)

# Extract the type and the documentation annotation
arg_type = type_hints['a'].__origin__
arg_doc = type_hints['a'].__metadata__[0].doc

print(f"Type of argument 'a': {arg_type}")
print(f"Documentation for argument 'a': {arg_doc}")
