import os
import sys
import ast
import io
import textwrap
import glob
import logging

# assuming the presence of packaging
from packaging.specifiers import SpecifierSet
from packaging.version import Version

def parse_setup(setup_path):
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
    global_vars = {"__setup_calls__": []}
    current_dir = os.getcwd()
    working_dir = os.path.dirname(setup_filename)
    os.chdir(working_dir)
    exec(codeobj, global_vars, local_vars)
    os.chdir(current_dir)
    _, kwargs = global_vars["__setup_calls__"][0]

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

    return name, version, python_requires, requires

def parse_setup_requires(setup_path):
    _, _, python_requires, _ = parse_setup(setup_path)

    return python_requires

def filter_for_compatibility(package_set):
    collected_packages = []
    v = sys.version_info
    running_major_version = Version(".".join([str(v[0]), str(v[1]), str(v[2])]))

    for pkg in package_set:
        spec_set = SpecifierSet(parse_setup_requires(pkg))

        if running_major_version in spec_set:
            collected_packages.append(pkg)

    return collected_packages

def remove_omitted_packages(collected_directories):
    packages = [
        package_dir
        for package_dir in collected_directories
        if os.path.basename(package_dir) not in OMITTED_CI_PACKAGES
    ]

    return packages

def process_glob_string(
    glob_string,
    target_root_dir,
    additional_contains_filter="",
    filter_type="Build",
):
    if glob_string:
        individual_globs = glob_string.split(",")
    else:
        individual_globs = "azure-*"
    collected_top_level_directories = []

    for glob_string in individual_globs:
        globbed = glob.glob(
            os.path.join(target_root_dir, glob_string, "setup.py")
        ) + glob.glob(os.path.join(target_root_dir, "sdk/*/", glob_string, "setup.py"))
        collected_top_level_directories.extend([os.path.dirname(p) for p in globbed])

    # dedup, in case we have double coverage from the glob strings. Example: "azure-mgmt-keyvault,azure-mgmt-*"
    collected_directories = list(
        set(
            [
                p
                for p in collected_top_level_directories
                if additional_contains_filter in p
            ]
        )
    )

    # if we have individually queued this specific package, it's obvious that we want to build it specifically
    # in this case, do not honor the omission list
    if len(collected_directories) == 1:
        pkg_set_ci_filtered = filter_for_compatibility(collected_directories)
    # however, if there are multiple packages being built, we should honor the omission list and NOT build the omitted
    # packages
    else:
        allowed_package_set = remove_omitted_packages(collected_directories)
        pkg_set_ci_filtered = filter_for_compatibility(allowed_package_set)

    # Apply filter based on filter type. for e.g. Docs, Regression, Management
    pkg_set_ci_filtered = list(filter(omit_funct_dict.get(filter_type, omit_build), pkg_set_ci_filtered))
    logging.info(
        "Target packages after filtering by CI: {}".format(
            pkg_set_ci_filtered
        )
    )
    logging.info(
        "Package(s) omitted by CI filter: {}".format(
            list(set(collected_directories) - set(pkg_set_ci_filtered))
        )
    )
    return sorted(pkg_set_ci_filtered)