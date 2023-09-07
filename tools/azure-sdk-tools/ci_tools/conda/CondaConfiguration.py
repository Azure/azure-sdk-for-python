from typing import List, Any
import os
import bs4
import urllib3
from ci_tools.functions import str_to_bool

http = urllib3.PoolManager()
# arguments: |
#       -c "${{ replace(convertToJson(parameters.CondaArtifacts), '"', '\"') }}"
#       -w "$(Build.SourcesDirectory)/conda/conda-recipes"
#
# # Sample configuration yaml. This is converted to json before being passed a blob to the invoking script. (see directly above for conversion)
#     - name: uamqp
#         common_root: uamqp
#         in_batch: true
#         conda_py_versions:
#         - "38"
#         - "39"
#         - "310"
#         - "311"
#         checkout:
#         - package: uamqp
#         download_uri: https://files.pythonhosted.org/packages/0b/d8/fc24d95e6f6c80851ae6738c78da081cd535c924b02c5a4928b108b9ed42/uamqp-1.6.5.tar.gz
#   - name: azure-core
#     common_root: azure
#     in_batch: ${{ parameters.release_azure_core }}
#     channels: "conda-forge"
#     checkout:
#     - package: azure-core
#       version: 1.24.0
#     - package: azure-core
#       version: 1.24.0
#   - name: azure-storage
#     common_root: azure
#     in_batch: ${{ parameters.release_azure_storage }}
#     checkout:
#     - package: azure-storage-blob
#       checkout_path: sdk/storage
#       version: 12.12.0
#     - package: azure-storage-queue
#       checkout_path: sdk/storage
#       version: 12.3.0
#     - package: azure-storage-file-share
#       checkout_path: sdk/storage
#       version: 12.8.0
#     - package: azure-storage-file-datalake
#       checkout_path: sdk/storage
#       version: 12.7.0


def get_pypi_page(package: str, version: str) -> bs4.BeautifulSoup:
    url = f"https://pypi.org/project/{package}/{version}/"

    try:
        r = http.request("GET", url)
    except Exception as e:
        raise RuntimeError(
            f'This package "{package}" has been configured to retrieve package source distribution from PyPI at URL "{url}".'
            + "Unable to retrieve these bits from PyPI. Check conda package configuration in conda-sdk-client.yml and retry."
        )

    return bs4.BeautifulSoup(r.data.decode("utf-8"), "html.parser")


def get_package_sdist_url(package: str, version: str) -> str:
    soup = get_pypi_page(package, version)

    # source distribution always first on the page
    try:
        target_zip = soup.select("div.file__card a")[0]["href"]
    except Exception as e:
        print(f"Can't get data from {package} and {version}")
        raise e
    filename = os.path.basename(target_zip)

    if filename.endswith("tar.gz") or filename.endswith(".zip"):
        return target_zip
    else:
        raise ValueError(f"Unable to find a source distribution for {package}@{version}.")


class CheckoutConfiguration:
    def __init__(self, raw_json: dict):
        # we should always have a package name

        if "package" in raw_json:
            self.package = raw_json["package"]
        else:
            raise ValueError("A checkout configuration MUST have a package name defined in key 'package'.")

        self.checkout_path = raw_json.get("checkout_path", None)
        self.version = raw_json.get("version", None)
        self.download_uri = raw_json.get("download_uri", None)

        if self.version and self.checkout_path is None:
            self.download_uri = get_package_sdist_url(self.package, self.version)

        if not self.checkout_path and not self.download_uri:
            raise ValueError(
                "When defining a checkout configuration, one must either have a valid PyPI download url"
                " (download_uri) or a path and version in the repo (checkout_path, version)."
            )

    def __str__(self) -> str:
        if self.download_uri:
            return f"""- {self.package} downloaded from pypi
  {self.download_uri}"""
        else:
            return f"""- {self.checkout_path}/{self.package} from git @ {self.version}"""


def parse_checkout_config(checkout_configs: List[Any]) -> List[CheckoutConfiguration]:
    configs = []
    for checkout_config in checkout_configs:
        configs.append(CheckoutConfiguration(checkout_config))

    return configs


class CondaConfiguration:
    def __init__(
        self,
        name: str,
        common_root: str,
        in_batch: bool,
        checkout: List[CheckoutConfiguration],
        created_sdist_path: str = None,
        service: str = "",
        conda_py_versions: List[str] = [],
        channels: List[str] = [],
    ):
        self.name: str = name
        self.common_root: str = common_root
        self.in_batch: bool = in_batch
        self.checkout: List[CheckoutConfiguration] = checkout
        self.created_sdist_path: str = created_sdist_path
        self.service: str = service
        self.conda_py_versions = conda_py_versions
        self.channels = channels

    @classmethod
    def from_json(cls, raw_json_blob: dict):
        name = raw_json_blob.get("name")
        common_root = raw_json_blob.get("common_root", None)
        in_batch = str_to_bool(raw_json_blob["in_batch"])
        checkout_config = parse_checkout_config(raw_json_blob.get("checkout"))
        conda_py_versions = raw_json_blob.get("conda_py_versions", [])
        service = raw_json_blob.get("service", None)
        channels = raw_json_blob.get("channels", [])

        # default the service
        if any([a.checkout_path for a in checkout_config]) and not service:
            valid_checkout_config = next((x for x in checkout_config if x.checkout_path is not None), None)
            if valid_checkout_config:
                service = valid_checkout_config.checkout_path.split("/")[1].strip()

        if not service and name.startswith("azure"):
            raise ValueError(
                f"Tooling cannot auto-detect targeted service for conda package {name}, nor is there a checkout_path that we can parse the service from. Please correct and retry."
            )

        return cls(name, common_root, in_batch, checkout_config, None, service, conda_py_versions, channels)

    def __str__(self) -> str:
        checkout = f"{os.linesep}".join([str(c_config) for c_config in self.checkout])

        return f"""====================================
\"{self.name}\" generated from:
{checkout}
====================================
"""

    def prepare_local_folder(self) -> None:
        pass
