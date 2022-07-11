import ast
import io
import os
import textwrap

# This was taken from /scripts/analyze_deps.py


def parse_setup(setup_filename):
    kwargs = parse_kwargs(setup_filename)

    version = kwargs["version"]
    name = kwargs["name"]
    requires = []
    if "install_requires" in kwargs:
        requires += kwargs["install_requires"]
    if "extras_require" in kwargs:
        for extra in kwargs["extras_require"].values():
            requires += extra
    return name, version, requires


def parse_kwargs(setup_filename):
    mock_setup = textwrap.dedent(
        """\
    def setup(*args, **kwargs):
        __setup_calls__.append((args, kwargs))
    """
    )
    parsed_mock_setup = ast.parse(mock_setup, filename=setup_filename)
    with io.open(setup_filename, "r", encoding="utf-8-sig") as setup_file:
        parsed = ast.parse(setup_file.read())
        for index, node in enumerate(parsed.body[:]):
            if (
                not isinstance(node, ast.Expr)
                or not isinstance(node.value, ast.Call)
                or not hasattr(node.value.func, "id")
                or node.value.func.id != "setup"
            ):
                continue
            parsed.body[index:index] = parsed_mock_setup.body
            break

    fixed = ast.fix_missing_locations(parsed)
    codeobj = compile(fixed, setup_filename, "exec")
    local_vars = {}
    global_vars = {"__setup_calls__": []}
    current_dir = os.getcwd()
    working_dir = os.path.dirname(setup_filename)
    os.chdir(working_dir)
    exec(codeobj, global_vars, local_vars)
    os.chdir(current_dir)
    _, kwargs = global_vars["__setup_calls__"][0]

    return kwargs


# todo what is the type of this?
def get_install_requires(setup_filename: str):
    kwargs = parse_kwargs(setup_filename)
    requires = []
    if "install_requires" in kwargs:
        requires += kwargs["install_requires"]
    return requires
