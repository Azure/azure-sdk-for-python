import os
import ast
import textwrap
import re
import fnmatch
import logging

try:
    # py 311 adds this library natively
    import tomllib as toml
except:
    # otherwise fall back to pypi package tomli
    import tomli as toml

from typing import Dict, List, Tuple, Any, Optional

# this assumes the presence of "packaging"
from packaging.requirements import Requirement
from setuptools import Extension

from ci_tools.variables import str_to_bool

VERSION_PY = "_version.py"
# Auto generated code has version maintained in version.py.
# We need to handle this old file name until generated code creates _version.py for all packages
OLD_VERSION_PY = "version.py"
VERSION_REGEX = r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]'
NEW_REQ_PACKAGES = ["azure-core", "azure-mgmt-core"]

INIT_PY_FILE = "__init__.py"
INIT_EXTENSION_SUBSTRING = ".extend_path(__path__, __name__)"

# Directories to exclude from searches to avoid finding files in wrong places
EXCLUDE = {
    "venv",
    "__pycache__",
    "tests",
    "test",
    "generated_samples",
    "generated_tests",
    "samples",
    "swagger",
    "stress",
    "docs",
    "doc",
    "local",
    "scripts",
    "images",
    ".tox"
}


def discover_namespace(package_root_path: str) -> Optional[str]:
    """
    Discover the true namespace of a package by walking through its directory structure
    and finding the first __init__.py that contains actual content (not just namespace extension).
    
    :param str package_root_path: Root path of the package directory
    :rtype: str or None
    :return: The discovered namespace string, or None if no suitable namespace found
    """
    if not os.path.exists(package_root_path):
        return None
        
    namespace = None
    
    for root, subdirs, files in os.walk(package_root_path):
        # Ignore any modules with name starts with "_"
        # For e.g. _generated, _shared etc
        # Ignore build, which is created when installing a package from source.
        # Ignore tests, which may have an __init__.py but is not part of the package.
        dirs_to_skip = [x for x in subdirs if x.startswith(("_", ".", "test", "build")) or x in EXCLUDE]
        for d in dirs_to_skip:
            logging.debug("Dirs to skip: {}".format(dirs_to_skip))
            subdirs.remove(d)
            
        if INIT_PY_FILE in files:
            module_name = os.path.relpath(root, package_root_path).replace(
                os.path.sep, "."
            )
            
            # If namespace has not been set yet, try to find the first __init__.py that's not purely for extension.
            if not namespace:
                namespace = _set_root_namespace(
                    os.path.join(root, INIT_PY_FILE), module_name
                )
    
    return namespace


def _set_root_namespace(init_file_path: str, module_name: str) -> Optional[str]:
    """
    Examine an __init__.py file to determine if it represents a substantial namespace 
    or is just a namespace extension file.
    
    :param str init_file_path: Path to the __init__.py file
    :param str module_name: The module name corresponding to this __init__.py
    :rtype: str or None
    :return: The namespace if this file contains substantial content, None otherwise
    """
    try:
        with open(init_file_path, "r", encoding="utf-8") as f:
            in_docstring = False
            content = []
            for line in f:
                stripped_line = line.strip()
                # If in multi-line docstring, skip following lines until end of docstring.
                # If single-line docstring, skip the docstring line.
                if stripped_line.startswith(('"""', "'''")) and not stripped_line.endswith(('"""', "'''")):
                    in_docstring = not in_docstring
                # If comment, skip line. Otherwise, add to content.
                if not in_docstring and not stripped_line.startswith("#"):
                    content.append(line)
            
            # If there's more than one line of content, or if there's one line that's not just namespace extension
            if len(content) > 1 or (
                len(content) == 1 and INIT_EXTENSION_SUBSTRING not in content[0]
            ):
                return module_name
                
    except Exception as e:
        logging.error(f"Error reading {init_file_path}: {e}")
        
    return None


class ParsedSetup:
    """
    Used to represent a parsed setup.py or pyproject.toml file. One should use `ParsedSetup.from_path` to create new instances.
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
        ext_package: str,
        ext_modules: List[Extension],
        metapackage: bool,
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
        self.ext_package = ext_package
        self.ext_modules = ext_modules
        self.is_metapackage = metapackage

        self.is_pyproject = self.setup_filename.endswith(".toml")

        self.folder = os.path.dirname(self.setup_filename)

    @classmethod
    def from_path(cls, parse_directory_or_file: str):
        """
        Creates a new ParsedSetup instance from a path to a setup.py, pyproject.toml (with [project] member), or a directory containing either of those files.
        """
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
            ext_package,
            ext_modules,
            metapackage,
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
            ext_package,
            ext_modules,
            metapackage,
        )

    def get_build_config(self) -> Optional[Dict[str, Any]]:
        return get_build_config(self.folder)

    def get_config_setting(self, setting: str, default: Any = True) -> Any:
        return get_config_setting(self.folder, setting, default)

    def is_reporting_suppressed(self, setting: str) -> bool:
        return compare_string_to_glob_array(setting, self.get_config_setting("suppressed_skip_warnings", []))


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
    override_value = os.getenv(f"{os.path.basename(package_path).upper().replace('-','_')}_{setting.upper()}", None)

    if override_value:
        return str_to_bool(override_value)

    # if no override, check for the config setting in the pyproject.toml
    config = get_build_config(package_path)

    if config:
        if setting.lower() in config:
            return config[setting.lower()]

    return default


def get_build_config(package_path: str) -> Optional[Dict[str, Any]]:
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


def get_ci_config(package_path: str) -> Optional[Dict[str, Any]]:
    """
    Attempts to retrieve the parsed toml content of a CI.yml associated with this package.
    """
    if os.path.isfile(package_path):
        package_path = os.path.dirname(package_path)

    # this checks exactly one directory up
    # for sdk/core/azure-core
    # sdk/core/ci.yml is checked only
    ci_file = os.path.join(os.path.dirname(package_path), "ci.yml")

    if os.path.exists(ci_file):
        import yaml

        try:
            with open(ci_file, "r") as f:
                return yaml.safe_load(f)
        except Exception as e:
            logging.error(f"Failed to load ci.yml at {ci_file} due to exception {e}")

    return None


def read_setup_py_content(setup_filename: str) -> str:
    """
    Get setup.py content, returns a string.
    """
    with open(setup_filename, "r", encoding="utf-8-sig") as setup_file:
        content = setup_file.read()
        return content


def parse_setup_py(
    setup_filename: str,
) -> Tuple[
    str, str, str, List[str], bool, str, str, Dict[str, Any], bool, List[str], List[str], str, List[Extension], bool
]:
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
        <keywords>,
        <ext_packages>,
        <ext_modules>,
        <is_metapackage>
    )
    """

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
            or node.value.func.id != "setup"  # type: ignore
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

    version = kwargs.get("version")
    name = kwargs.get("name")
    name_space = name.replace("-", ".")
    packages = kwargs.get("packages", [])

    if packages:
        name_space = packages[0]
        metapackage = False
    else:
        metapackage = True

    requires = kwargs.get("install_requires", [])
    package_data = kwargs.get("package_data", None)
    include_package_data = kwargs.get("include_package_data", None)
    classifiers = kwargs.get("classifiers", [])
    keywords = kwargs.get("keywords", [])

    is_new_sdk = name in NEW_REQ_PACKAGES or any(map(lambda x: (parse_require(x).name in NEW_REQ_PACKAGES), requires))

    ext_package = kwargs.get("ext_package", None)
    ext_modules = kwargs.get("ext_modules", [])

    # fmt: off
    return (
        name,                   # str
        version,                # str
        python_requires,        # str
        requires,               # List[str]
        is_new_sdk,             # bool
        setup_filename,         # str
        name_space,             # str,
        package_data,           # Dict[str, Any],
        include_package_data,   # bool,
        classifiers,            # List[str],
        keywords,               # List[str] ADJUSTED
        ext_package,            # str
        ext_modules,            # List[Extension],
        metapackage             # bool
    )
    # fmt: on


def parse_pyproject(
    pyproject_filename: str,
) -> Tuple[
    str, str, str, List[str], bool, str, str, Dict[str, Any], bool, List[str], List[str], str, List[Extension], bool
]:
    """
    Used to evaluate a pyproject (or a directory containing a pyproject.toml) with a [project] configuration within.
    Returns a tuple containing:
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
        <keywords>,
        <ext_packages>,
        <ext_modules>,
        <is_metapackage>
    )
    """
    toml_dict = get_pyproject_dict(pyproject_filename)

    project_config = toml_dict.get("project", None)

    assert project_config is not None, f"Unable to find [project] section in {pyproject_filename}. Please ensure it is present."

    # to pull a version from pyproject.toml, we need to get a dynamic version out. We can ask
    # setuptools to give us the metadata for a package, but that will involve _partially building_ the package
    # to create an egginfo folder. This is a very expensive operation goes against the entire point of
    # "give me the package metadata for this folder."
    # We can avoid this expensive operation if we parse the version out of the _version or version file directly.
    parsed_version = project_config.get("version", None)

    if not parsed_version:
        parsed_version_py = get_version_py(pyproject_filename)

        if parsed_version_py:
            with open(parsed_version_py, "r") as f:
                parsed_version = re.search(VERSION_REGEX, f.read(), re.MULTILINE)

                if parsed_version:
                    parsed_version = parsed_version.group(1)
                else:
                    parsed_version = "0.0.0"
        else:
            raise ValueError(
                f'Unable to find a version value directly set in "{pyproject_filename}", nor is it available in a "version.py" or "_version.py."'
            )

    name = project_config.get("name")
    version = parsed_version
    python_requires = project_config.get("requires-python")
    requires = project_config.get("dependencies")
    is_new_sdk = name in NEW_REQ_PACKAGES or any(map(lambda x: (parse_require(x).name in NEW_REQ_PACKAGES), requires))

    # Discover the actual namespace by walking the package directory
    package_directory = os.path.dirname(pyproject_filename)
    discovered_namespace = discover_namespace(package_directory)
    name_space = discovered_namespace if discovered_namespace else name.replace("-", ".")
    package_data = get_value_from_dict(toml_dict, "tool.setuptools.package-data", None)
    include_package_data = get_value_from_dict(toml_dict, "tool.setuptools.include-package-data", True)
    classifiers = project_config.get("classifiers", [])
    keywords = project_config.get("keywords", [])
    metapackage = False

    # as of setuptools 74.1 ext_packages and ext_modules are now present in tool.setuptools config namespace
    ext_package = get_value_from_dict(toml_dict, "tool.setuptools.ext-package", None)
    ext_modules = get_value_from_dict(toml_dict, "tool.setuptools.ext-modules", [])
    ext_modules = [Extension(**moduleArgDict) for moduleArgDict in ext_modules]

    # fmt: off
    return (
        name,                   # str
        version,                # str
        python_requires,        # str
        requires,               # List[str]
        is_new_sdk,             # bool
        pyproject_filename,     # str
        name_space,             # str,
        package_data,           # Dict[str, Any],
        include_package_data,   # bool,
        classifiers,            # List[str],
        keywords,               # List[str] ADJUSTED
        ext_package,            # str
        ext_modules,            # List[Extension]
        metapackage             # bool
    )
    # fmt: on


def get_version_py(setup_path: str) -> Optional[str]:
    """
    Given the path to pyproject.toml or setup.py, attempts to find a (_)version.py file and return its location.
    """
    file_path, _ = os.path.split(setup_path)

    # Find path to _version.py recursively
    for root, dirs, files in os.walk(file_path):
        dirs[:] = [d for d in dirs if d not in EXCLUDE and not d.endswith(".egg-info")]

        if VERSION_PY in files:
            return os.path.join(root, VERSION_PY)
        elif OLD_VERSION_PY in files:
            return os.path.join(root, OLD_VERSION_PY)

    return None


def get_pyproject(folder: str) -> Optional[str]:
    """
    Given a folder, attempts to find a pyproject.toml file with a "project" configuration and return its location.
    """
    pyproject_filename = os.path.join(folder, "pyproject.toml")

    if os.path.exists(pyproject_filename):
        project_config = get_value_from_dict(get_pyproject_dict(pyproject_filename), "project", None)
        if project_config:
            return pyproject_filename

    return None


def get_setup_py(folder: str) -> Optional[str]:
    """
    Given a folder, attempts to find a setup.py file and return its location.
    """
    setup_filename = os.path.join(folder, "setup.py")

    if os.path.exists(setup_filename):
        return setup_filename

    return None


def parse_setup(
    setup_filename_or_folder: str,
):
    """
    Used to evaluate a pyproject.toml or setup.py (or a directory containing either) and return a tuple containing:
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
        <keywords>,
        <ext_packages>,
        <ext_modules>,
        <is_metapackage>
    )

    If a pyproject.toml (containing [project]) or a setup.py is NOT found, a ValueError will be raised.
    """
    targeted_path = setup_filename_or_folder
    if os.path.isfile(setup_filename_or_folder):
        targeted_path = os.path.dirname(setup_filename_or_folder)

    resolved_filename = get_pyproject(targeted_path) or get_setup_py(targeted_path)
    if not resolved_filename:
        raise ValueError(f"Unable to find a setup.py or pyproject.toml in {setup_filename_or_folder}")

    if resolved_filename.endswith(".toml"):
        return parse_pyproject(resolved_filename)
    else:
        return parse_setup_py(resolved_filename)


def get_pyproject_dict(pyproject_file: str) -> Dict[str, Any]:
    """
    Given a pyproject.toml file, returns a dictionary of a target section. Defaults to `project` section.
    """

    with open(pyproject_file, "rb") as f:
        pyproject_dict = toml.load(f)

    return pyproject_dict


def get_value_from_dict(pyproject_dict: Dict[str, Any], keystring: str, default_if_not_present: Any = None) -> Any:
    """
    Given a dictionary, offers an easy interface for nested objects via `.` notation.
    Example usage -> get_value_from_dict(pyproject_dict, "tool.setuptools.include-package-data", True)
    """
    keys = keystring.split(".")

    current_selection = pyproject_dict

    for index, key in enumerate(keys):
        if index == len(keys) - 1:
            return current_selection.get(key, default_if_not_present)
        if key in current_selection:
            current_selection = current_selection[key]
        else:
            return default_if_not_present

    return default_if_not_present


def get_install_requires(setup_path: str) -> List[str]:
    """
    Simple helper function to just directly get the installation requirements given a python package.
    """
    return ParsedSetup.from_path(setup_path).requires


def parse_require(req: str) -> Requirement:
    """
    Parses a PEP 508 requirement string into a Requirement object.

    Example: "azure-core<2.0.0,>=1.11.0"
    """
    return Requirement(req)


def get_name_from_specifier(version: str) -> str:
    """
    Given a specifier string of format of <package-name><comparison><versionNumber>, returns the package name.

    "azure-core<2.0.0,>=1.11.0" -> azure-core
    """
    return re.split(r"[><=]", version)[0]


def compare_string_to_glob_array(string: str, glob_array: List[str]) -> bool:
    """
    This function is used to easily compare a string to a set of glob strings, if it matches any of them, returns True.
    """
    return any([fnmatch.fnmatch(string, glob) for glob in glob_array])
