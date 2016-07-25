import sys

package_name = '{{cookiecutter.package_name}}'

if not package_name.startswith('azure-mgmt-'):
    print('ERROR: package name must start with "azure-mgmt-"')

    # exits with status 1 to indicate failure
    sys.exit(1)