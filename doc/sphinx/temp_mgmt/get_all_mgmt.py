import glob
import pathlib
from pypi_tools.pypi import PyPIClient

root = file_path = pathlib.Path(__file__).resolve().parent.parent.parent.parent


def mgmt():
    client = PyPIClient()
    service_directories = glob.glob(f"{root}/sdk/*/", recursive = True)
    mgmt = {}
    for service in service_directories:
        packages = glob.glob(f"{service}*/", recursive = True)
        for package in packages:
            package_path = pathlib.Path(package)
            package_name = package_path.name
            service_directory = package_path.parent.name
            if "mgmt" in package_name:
                mgmt[package_name] = {}
                mgmt[package_name].update({"service_directory": service_directory})
                latest = client.get_ordered_versions(package_name)[-1]
                mgmt[package_name].update({"version": str(latest)})
    return mgmt


packages = mgmt()
with open("mgmt.txt", "w+") as fd:
  for pkg, details in packages.items():
      fd.write(f"      {pkg}:\n        ServiceDirectory: {details['service_directory']}\n        Version: '{details['version']}'\n")
