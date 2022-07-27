import os
import ast
import textwrap
import sys
import re
from typing import Dict, List, Tuple

# Assumes the presence of setuptools
from pkg_resources import (
    parse_version,
    parse_requirements,
    Requirement,
    WorkingSet,
    working_set,
)
import pdb

# this assumes the presence of "packaging"
from packaging.specifiers import SpecifierSet


NEW_REQ_PACKAGES = ["azure-core", "azure-mgmt-core"]


class ParsedSetup:
    """
    Python version
    """

    def __init__(
        self,
        name: str,
        version: str,
        python_requires: List[str],
        requires: List[str],
        is_new_sdk: bool,
        setup_filename: str,
        name_space: str,
        package_data: Dict,
        include_package_data: bool,
    ):
        self.name: str = name
        self.version: str = version
        self.python_requires: List[str] = python_requires
        self.requires: List[str] = requires
        self.is_new_sdk: bool = is_new_sdk
        self.setup_filename: str = setup_filename
        self.namespace = name_space
        self.package_data = package_data
        self.include_package_data = include_package_data

    @classmethod
    def from_path(cls, parse_directory_or_file: str):
        (
            name,
            version,
            python_requires,
            requires,
            is_new_sdk,
            setup_filename,
            name_space,
            package_data,
            include_package_data,
        ) = parse_setup(parse_directory_or_file)

        return cls(
            name,
            version,
            python_requires,
            requires,
            is_new_sdk,
            setup_filename,
            name_space,
            package_data,
            include_package_data,
        )


def read_setup_py_content(setup_filename: str) -> str:
    """
    Get setup.py content, returns a string.
    """
    with open(setup_filename, "r", encoding="utf-8-sig") as setup_file:
        content = setup_file.read()
        return content


def parse_setup(setup_filename: str) -> Tuple[str, str, List[str], List[str], bool, str]:
    """
    Used to evaluate a setup.py (or a directory containing a setup.py) and return a tuple containing:
    (
        <package-name>,
        <package_version>,
        <python_requires>,
        <requires>,
        <boolean indicating track1 vs track2>,
        <parsed setup.py location>,
        <namespace>,
        <package_data dict>,
        <include_package_data bool>
    )
    """
    if not setup_filename.endswith("setup.py"):
        setup_filename = os.path.join(setup_filename, "setup.py")
    mock_setup = textwrap.dedent(
        """\
    def setup(*args, **kwargs):
        __setup_calls__.append((args, kwargs))
    """
    )
    parsed_mock_setup = ast.parse(mock_setup, filename=setup_filename)
    content = read_setup_py_content(setup_filename)
    parsed = ast.parse(content)

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
    name_space = name.replace("-", ".")

    if "packages" in kwargs.keys():
        packages = kwargs["packages"]
        if packages:
            name_space = packages[0]

    requires = []
    if "install_requires" in kwargs:
        requires = kwargs["install_requires"]

    package_data = None
    if "package_data" in kwargs:
        package_data = kwargs["package_data"]

    include_package_data = None
    if "include_package_data" in kwargs:
        include_package_data = kwargs["include_package_data"]

    is_new_sdk = name in NEW_REQ_PACKAGES or any(map(lambda x: (parse_require(x)[0] in NEW_REQ_PACKAGES), requires))

    return (
        name,
        version,
        python_requires,
        requires,
        is_new_sdk,
        setup_filename,
        name_space,
        package_data,
        include_package_data,
    )


def get_install_requires(setup_path: str) -> List[str]:
    """
    Simple helper function to just directly get the installation requirements given a python package.
    """
    return ParsedSetup.from_path(setup_path).requires


def parse_require(req: str) -> Tuple[str, SpecifierSet]:
    """
    Parses the incoming version specification and returns a tuple of the requirement name and specifier.

    "azure-core<2.0.0,>=1.11.0" -> [azure-core, <2.0.0,>=1.11.0]
    """
    req_object = Requirement.parse(req.split(";")[0].lower())
    pkg_name = req_object.key
    spec_object_str = str(req_object)
    isolated_spec = str(req_object).replace(pkg_name, "")

    # we were not passed a full requirement. Instead we were passed a value of "readme-renderer" or another string without a version.
    if spec_object_str == spec_object_str:
        return [pkg_name, None]

    spec = SpecifierSet(isolated_spec)
    return [pkg_name, spec]


def parse_requirements_file(file_location: str) -> Dict[str, str]:
    """
    Takes a python requirements file and returns a dictionary representing the contents.
    """
    with open(file_location, "r") as f:
        reqs = f.read()

    return dict((req.name, req) for req in parse_requirements(reqs))


def get_name_from_specifier(version: str) -> str:
    """
    Given a specifier string of format of <package-name><comparison><versionNumber>, returns the package name.

    "azure-core<2.0.0,>=1.11.0" -> azure-core
    """
    return re.split(r"[><=]", version)[0]
