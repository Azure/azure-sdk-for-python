# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from pathlib import Path
from typing import Any, Set
from urllib.parse import urlparse

from ..models._enums import AssetTypes
from ..models._models import Output as _Output


_TERMINAL_JOB_STATUSES = frozenset({"completed", "failed", "canceled", "notresponding", "paused"})

_MAX_CONCURRENCY = 4

_NAMED_OUTPUTS_DIR = "named-outputs"

_DEFAULT_OUTPUT_NOT_SUPPORTED_MSG = (
    "Downloading the 'default' output is not yet supported. The default output is identified "
    "by an 'azureai://data/ExperimentRun/dcid.{jobName}' URI, but no service-side API currently "
    "exists to resolve this URI to a storage account + SAS credential. "
    "TODO: add a service API such as `POST /training/jobs/{name}/artifacts/credentials` returning "
    "a `BlobReference`. For now, use `output_name='<your-named-output>'` to download a specific "
    "registered output."
)


def _blob_uri_to_prefix(blob_uri: str) -> str:
    parsed = urlparse(blob_uri)
    path = parsed.path.lstrip("/")
    if not path:
        raise ValueError(f"Blob URI '{blob_uri}' is missing a container segment.")
    parts = path.split("/", 1)
    prefix = parts[1] if len(parts) > 1 else ""
    return prefix.rstrip("/")


def _is_folder_marker(blob: Any, all_names: Set[str]) -> bool:
    if blob.metadata and blob.metadata.get("hdi_isfolder", "").lower() == "true":
        return True
    prefix_token = blob.name + "/"
    return any(other != blob.name and other.startswith(prefix_token) for other in all_names)


def _ensure_dir(p: Path) -> None:
    if p.exists() and not p.is_dir():
        p.unlink()
    p.mkdir(parents=True, exist_ok=True)


def _validate_output_for_download(output_name: str, output: _Output) -> None:
    if not output.asset_name or not output.asset_version:
        raise ValueError(
            f"Output '{output_name}' has no registered asset (assetName / assetVersion is missing). "
            "Downloading the default job artifact store is not yet supported. "
        )

    out_type = output.type
    if out_type in (AssetTypes.URI_FILE, AssetTypes.URI_FOLDER):
        return

    if out_type == AssetTypes.SAFETENSORS_MODEL:
        raise NotImplementedError(
            f"Output '{output_name}' is a 'safetensors_model'. Downloading model outputs is not yet "
            "supported \u2014 the required Models operations and AssetCredentialRequest model are not "
            "available in this SDK build."
        )

    raise ValueError(
        f"Output '{output_name}' has unsupported jobOutputType '{out_type}'. "
        f"Supported types: uri_file, uri_folder."
    )
