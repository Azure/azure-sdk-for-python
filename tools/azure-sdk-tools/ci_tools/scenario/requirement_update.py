from pypi_tools.pypi import PyPIClient
from ci_tools.parsing import ParsedSetup

DEV_BUILD_IDENTIFIER = "a"


def update_requires(setup_py_path, requires_dict):
    # This method changes package requirement by overriding the specifier
    contents = []
    with open(setup_py_path, "r") as setup_file:
        contents = setup_file.readlines()

    # find and replace all existing package requirement with new requirement
    for i in range(0, len(contents) - 1):
        keys = [k for k in requires_dict.keys() if k in contents[i]]
        for key in keys:
            contents[i] = contents[i].replace(key, requires_dict[key])

    with open(setup_py_path, "w") as setup_file:
        setup_file.writelines(contents)


def is_required_version_on_pypi(package_name, spec):
    client = PyPIClient()
    try:
        pypi_results = client.get_ordered_versions(package_name)
    except:
        pypi_results = []

    versions = [str(v) for v in pypi_results if str(v) in spec]
    return versions


def get_version(pkg_name):
    # find version for the package from source. This logic should be revisited to find version from devops feed
    glob_path = os.path.join(root_dir, "sdk", "*", pkg_name, "setup.py")
    paths = glob.glob(glob_path)
    if paths:
        setup_py_path = paths[0]
        parsed_setup = ParsedSetup.from_path(setup_py_path)
        # Remove dev build part if version for this package is already updated to dev build
        # When building package with dev build version, version for packages in same service is updated to dev build
        # and other packages will not have dev build number
        # strip dev build number so we can check if package exists in PyPI and replace

        version_obj = Version(parsed_setup.version)
        if version_obj.pre:
            if version_obj.pre[0] == DEV_BUILD_IDENTIFIER:
                version = version_obj.base_version

        return version
    else:
        logging.error("setup.py is not found for package {} to identify current version".format(pkg_name))
        exit(1)


def get_base_version(pkg_name):
    # find version for the package from source. This logic should be revisited to find version from devops feed
    glob_path = os.path.join(root_dir, "sdk", "*", pkg_name, "setup.py")
    paths = glob.glob(glob_path)
    if paths:
        setup_py_path = paths[0]
        parsed_setup = ParsedSetup.from_path(setup_py_path)

        version_obj = Version(parsed_setup.version)
        return version_obj.base_version
    else:
        logging.error("setup.py is not found for package {} to identify current version".format(pkg_name))
        exit(1)


def process_requires(setup_py_path):
    # This method process package requirement to verify if all required packages are available on PyPI
    # If any azure sdk package is not available on PyPI then requirement will be updated to refer dev version
    requires = [Requirement.parse(r) for r in ParsedSetup.from_path(setup_py_path).requires if r.startswith("azure")]

    # Find package requirements that are not available on PyPI
    requirement_to_update = {}
    for req in requires:
        pkg_name = req.key
        spec = SpecifierSet(str(req).replace(pkg_name, ""))

        if not is_required_version_on_pypi(pkg_name, spec):
            old_req = str(req)
            version = get_version(pkg_name)
            base_version = get_base_version(pkg_name)
            logging.info("Updating version {0} in requirement {1} to dev build version".format(version, old_req))
            new_req = old_req.replace(version, "{}{}".format(base_version, DEV_BUILD_IDENTIFIER))
            logging.info("New requirement for package {0}: {1}".format(pkg_name, new_req))
            requirement_to_update[old_req] = new_req

    if not requirement_to_update:
        logging.info("All required packages are available on PyPI")
    else:
        logging.info("Packages not available on PyPI:{}".format(requirement_to_update))
        update_requires(setup_py_path, requirement_to_update)
        logging.info("Package requirement is updated in setup.py")
