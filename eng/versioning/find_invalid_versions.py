import re
from os import path

from version_shared import get_packages, get_version_py

SDK_PATH = "../../sdk/"

if __name__ == '__main__':
    packages = get_packages(SDK_PATH)

    invalid_packages = []
    for package in packages:
        # TODO: This try/except trying and catching too many things
        try:
            version_py_path = get_version_py(package[0])

            with open(version_py_path, 'r') as version_py_file:
                version_contents = version_py_file.read()

                version = re.search(r'^VERSION\s*=\s*[\'"]([^\'"]*)[\'"]',  # type: ignore
                    version_contents, re.MULTILINE).group(1)

                if version != package[1][1]:
                    print(f'{package[1][0]} setup.py: {package[1][1]} _version.py: {version}' )
                    invalid_packages.append(package[1][0])
                    continue


            version_py_folder, _ = path.split(version_py_path)
            package_dunder_init = path.join(version_py_folder, '__init__.py')

            with open(package_dunder_init, 'r') as package_dunder_init_file:
                version = re.search(r'^__version__\s*=\s*VERSION',
                    package_dunder_init_file.read(), re.MULTILINE)

                if not bool(version):
                    invalid_packages.append(package[1][0])
                    continue

            # TODO: Try evaling __init__.py next to _version.py to ensure version match

        except:
            invalid_packages.append(package[1][0])

    print("=================\nInvalid Packages:\n=================\n")

    for invalid_package in invalid_packages:
        print(invalid_package)