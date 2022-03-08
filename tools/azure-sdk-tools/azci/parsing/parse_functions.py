import os
import ast
import textwrap
import sys

# Assumes the presence of setuptools
from pkg_resources import parse_version, parse_requirements, Requirement, WorkingSet, working_set

# this assumes the presence of "packaging"
from packaging.specifiers import SpecifierSet
from packaging.version import Version
from packaging.version import parse
from typing import Dict


NEW_REQ_PACKAGES = ["azure-core", "azure-mgmt-core"]

def parse_setup(setup_filename: str) -> (str, str, list[str], ):
    if not setup_filename.endswith("setup.py")
        setup_filename = os.path.join(setup_path, "setup.py")
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
    kwargs = {}
    global_vars = {"__setup_calls__": []}
    current_dir = os.getcwd()
    working_dir = os.path.dirname(setup_filename)
    os.chdir(working_dir)
    try:
        exec(codeobj, global_vars, local_vars)
        _, kwargs = global_vars["__setup_calls__"][0]
    finally:
        os.chdir(current_dir)

    try:
        python_requires = kwargs["python_requires"]
    # most do not define this, fall back to what we define as universal
    except KeyError as e:
        python_requires = ">=2.7"

    version = kwargs["version"]
    name = kwargs["name"]

    requires = []
    if "install_requires" in kwargs:
        requires = kwargs["install_requires"]

    is_new_sdk = name in NEW_REQ_PACKAGES or any(map(lambda x: (parse_require(x)[0] in NEW_REQ_PACKAGES), requires))

    return name, version, python_requires, requires, is_new_sdk, setup_filename


def parse_require(req: str) -> Tuple[str, str]:
    """
    Parses the incoming version specification and returns a tuple of the requirement name and specifier.

    "azure-core<2.0.0,>=1.11.0" -> [azure-core, <2.0.0,>=1.11.0]
    """
    req_object = Requirement.parse(req.split(";")[0])
    pkg_name = req_object.key
    spec = SpecifierSet(str(req_object).replace(pkg_name, ""))
    return [pkg_name, spec]


def parse_requirements_file(file_location: str) -> Dict[str, str]:
    with open(file_location, "r") as f:
        reqs = f.read()

    return dict((req.name, req) for req in parse_requirements(reqs))

# TODO: delete after I understand who uses this function
# def parse_setup_requires(setup_path):
#     _, _, python_requires, _ = parse_setup(setup_path)

#     return python_requires

def get_name_from_specifier(version: str) -> str:
    """
    Given a specifier string of format A <comparison> <versionNumber>, returns the package name.
    """
    return re.split(r"[><=]", version)[0]