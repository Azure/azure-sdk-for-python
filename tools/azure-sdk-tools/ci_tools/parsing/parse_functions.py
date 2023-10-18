import os
import ast
import textwrap
import re

try:
    # py 311 adds this library natively
    import tomllib as toml
except:
    # otherwise fall back to pypi package tomli
    import tomli as toml

from typing import Dict, List, Tuple, Any

# Assumes the presence of setuptools
from pkg_resources import (
    parse_version,
    parse_requirements,
    Requirement,
    WorkingSet,
    working_set,
)

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
        python_requires: str,
        requires: List[str],
        is_new_sdk: bool,
        setup_filename: str,
        name_space: str,
        package_data: Dict[str, Any],
        include_package_data: bool,
        classifiers: List[str],
        keywords: List[str],
    ):
        self.name: str = name
        self.version: str = version
        self.python_requires: str = python_requires
        self.requires: List[str] = requires
        self.is_new_sdk: bool = is_new_sdk
        self.setup_filename: str = setup_filename
        self.namespace: str = name_space
        self.package_data: Dict[str, Any] = package_data
        self.include_package_data: bool = include_package_data
        self.classifiers: List[str] = classifiers
        self.keywords: List[str] = keywords

        self.folder = os.path.dirname(self.setup_filename)

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
            classifiers,
            keywords,
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
            classifiers,
            keywords,
        )

    def get_build_config(self) -> Dict[str, Any]:
        return get_build_config(self.folder)


def update_build_config(package_path: str, new_build_config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Attempts to update a pyproject.toml's [tools.azure-sdk-tools] section with a new check configuration.
    
    This function can only append or override existing check values. It cannot delete them.
    """
    if os.path.isfile(package_path):
        package_path = os.path.dirname(package_path)

    toml_file = os.path.join(package_path, "pyproject.toml")

    if os.path.exists(toml_file):
        with open(toml_file, "rb") as f:
            toml_dict = toml.load(f)
            if "tool" in toml_dict:
                tool_configs = toml_dict["tool"]
                if "azure-sdk-build" in tool_configs:
                    tool_configs["azure-sdk-build"] = new_build_config
    else:
        toml_dict = {"tool": {"azure-sdk-build": new_build_config}}

    with open(toml_file, "wb") as f:
        import tomli_w
        tomli_w.dump(toml_dict, f)

    return new_build_config


def get_config_setting(package_path: str, setting: str, default: Any = True) -> Any:
    """
    Attempts to retrieve a specific setting within the [tools.azure-sdk-tools] section of a discovered
    pyproject.toml. If the input 'setting' does NOT exist, the provided default value will be returned.
    """
    # we should always take the override if one is present
    override_value = os.getenv(f"{os.path.basename(package_path).upper()}_{setting.upper()}", None)
    if override_value:
        return override_value

    # if no override, check for the config setting in the pyproject.toml
    config = get_build_config(package_path)

    if config:
        if setting.lower() in config:
            return config[setting.lower()]

    return default


def get_build_config(package_path: str) -> Dict[str, Any]:
    """
    Attempts to retrieve all values within [tools.azure-sdk-build] section of a pyproject.toml.

    If passed an actual file in package_path arg, the pyproject.toml will be found alongside the targeted file.
    """
    if os.path.isfile(package_path):
        package_path = os.path.dirname(package_path)

    toml_file = os.path.join(package_path, "pyproject.toml")

    if os.path.exists(toml_file):
        try:
            with open(toml_file, "rb") as f:
                toml_dict = toml.load(f)
                if "tool" in toml_dict:
                    tool_configs = toml_dict["tool"]
                    if "azure-sdk-build" in tool_configs:
                        return tool_configs["azure-sdk-build"]
        except:
            return {}


def read_setup_py_content(setup_filename: str) -> str:
    """
    Get setup.py content, returns a string.
    """
    with open(setup_filename, "r", encoding="utf-8-sig") as setup_file:
        content = setup_file.read()
        return content


def parse_setup(
    setup_filename: str,
) -> Tuple[str, str, str, List[str], bool, str, str, Dict[str, Any], bool, List[str]]:
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
        <include_package_data bool>,
        <classifiers>,
        <keywords>
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

    classifiers = []
    if "classifiers" in kwargs:
        classifiers = kwargs["classifiers"]

    keywords = []
    if "keywords" in kwargs:
        keywords = kwargs["keywords"]

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
        classifiers,
        keywords,
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

    # we were not passed a full requirement. Instead we were passed a value of "readme-renderer" or another string without a version.
    if not req_object.specifier:
        return [pkg_name, None]

    # regex details ripped from https://peps.python.org/pep-0508/
    isolated_spec = re.sub(r"^([a-zA-Z0-9\-\_\.]+)(\[[a-zA-Z0-9\-\_\.\,]*\])?", "", str(req_object))
    spec = SpecifierSet(isolated_spec)
    return (pkg_name, spec)


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
