from typing import List, Any
import os

# arguments: |
#       -c "${{ replace(convertToJson(parameters.CondaArtifacts), '"', '\"') }}"
#       -w "$(Build.SourcesDirectory)/conda/conda-recipes"
#
# Sample configuration yaml. This is converted to json before being passed a blob to the invoking script. (see directly above for conversion)
#   - name: azure-core
#     common_root: azure
#     in_batch: ${{ parameters.release_azure_core }}
#     checkout:
#     - package: azure-core
#         checkout_path: sdk/core
#         version: 1.24.0
#   - name: azure-storage
#     common_root: azure
#     in_batch: ${{ parameters.release_azure_storage }}
#     checkout:
#     - package: azure-storage-blob
#         checkout_path: sdk/storage
#         version: 12.12.0
#     - package: azure-storage-queue
#         checkout_path: sdk/storage
#         version: 12.3.0
#     - package: azure-storage-file-share
#         checkout_path: sdk/storage
#         version: 12.8.0
#     - package: azure-storage-file-datalake
#         checkout_path: sdk/storage
#         version: 12.7.0


class CheckoutConfiguration:
    def __init__(self, raw_json: dict):
        # we should always have a package name

        if "package" in raw_json:
            self.package = raw_json["package"]
        else:
            raise ValueError("A checkout configuration MUST have a package name defined in key 'package'.")

        if "checkout_path" in raw_json:
            self.checkout_path = raw_json["checkout_path"]
        else:
            self.checkout_path = None

        if "version" in raw_json:
            self.version = raw_json["version"]
        else:
            self.version = None

        if "download_uri" in raw_json:
            self.download_uri = raw_json["download_uri"]
        else:
            self.download_uri = None

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
            return f"""- {self.package} from cloned source
  {self.checkout_path}
  {self.version}"""


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
        created_sdist_path: str = "",
    ):
        self.name = name
        self.common_root = common_root
        self.in_batch = in_batch
        self.checkout = checkout
        self.created_sdist_path = created_sdist_path

    @classmethod
    def from_json(cls, raw_json_blob: dict):
        name = raw_json_blob["name"]
        common_root = raw_json_blob["common_root"] if raw_json_blob["common_root"] else "azure"
        in_batch = raw_json_blob["in_batch"]
        checkout_config = parse_checkout_config(raw_json_blob["checkout"])

        return cls(name, common_root, in_batch, checkout_config)

    def __str__(self) -> str:
        checkout = f"{os.linesep}".join([str(c_config) for c_config in self.checkout])

        return f"""====================================
\"{self.name}\" generated from:
{checkout}
====================================

        """

    def prepare_local_folder(self) -> None:
        pass
