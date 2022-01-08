import os
import ast
import io
import re
import textwrap
from subprocess import check_call

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

def is_track2_package(reqs):
    for req in reqs:
        if req.startswith('azure-core'):
            return True
    return False

def get_package_properties(setup_py_path):
    """Parse setup.py and return package details like package name, version, whether it's new SDK
    """
    pkg_name, version, _, requires = parse_setup(setup_py_path)
    is_track2 = is_track2_package(requires)
    return pkg_name, version, is_track2, setup_py_path

def get_all_eligible_packages(path):
    eligible_libraries = []
    for root, dirs, files in os.walk(os.path.abspath(path)):
        if re.search(r"sdk[\\/][^\\/]+[\\/][^\\/]+$", root):
            if "setup.py" in files:
                try:
                    pkg_name, version, is_track2, setup_py_path = get_package_properties(root)
                    if is_track2:
                        eligible_libraries.append((pkg_name, version, setup_py_path))
                except:
                    # Skip setup.py if the package cannot be parsed
                    pass
    return eligible_libraries

def build_requirements_nightly(packages):
    file_path = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..", "..", "..",
            "./eng/scripts/smoketest",
        ))
    f = open(file_path + "/requirements-nightly.txt", 'w')
    for package in packages:
        pkg_name, _, setup_py_path = package
        f.write(pkg_name + ' ' + setup_py_path + '\n')
    f.close()

def build_requirements_release(packages):
    file_path = os.path.abspath(
        os.path.join(
            os.path.abspath(__file__),
            "..", "..", "..",
            "./eng/scripts/smoketest",
        ))
    f = open(file_path + "/requirements-release.txt", 'w')
    for package in packages:
        pkg_name, _, setup_py_path = package
        f.write(pkg_name + '\n')
    f.close()

if __name__ == '__main__':
    print("Running get_track2_packages.py")
    packages = get_all_eligible_packages('.')
    build_requirements_release(packages)
