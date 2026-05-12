# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from pathlib import Path
from typing import Any, Optional, Set, Tuple, Union
from os import PathLike
from urllib.parse import urlparse

from ..models._enums import AssetTypes
from ..models._models import Output as _Output
from ..models._patch_jobs import CommandJob, ValidationResult

_TERMINAL_JOB_STATUSES = frozenset({"completed", "failed", "canceled", "notresponding", "paused"})

_MAX_CONCURRENCY = 4

_NAMED_OUTPUTS_DIR = "named-outputs"

_DEFAULT_OUTPUT_NOT_SUPPORTED_MSG = (
    "Downloading the 'default' output is not yet supported. The default output is identified "
    "by an 'azureai://data/ExperimentRun/dcid.{jobName}' URI, but no service-side API currently "
    "exists to resolve this URI to a storage account + SAS credential. "
    "TODO: add a service API such as `POST /jobs/{name}/artifacts/credentials` returning "
    "a `BlobReference`. For now, use `output_name='<your-named-output>'` to download a specific "
    "registered output."
)

_GIT_PATH_PREFIXES: Tuple[str, ...] = ("git://", "git+")


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
        f"Output '{output_name}' has unsupported jobOutputType '{out_type}'. " f"Supported types: uri_file, uri_folder."
    )


def _path_looks_local(value: Any) -> bool:
    """Return True if *value* looks like a local filesystem path (vs. a remote URI or asset reference)."""
    if not isinstance(value, str) or not value:
        return False
    if "://" in value:
        return False
    if value.startswith("azureai:"):
        return False
    # name:version pattern (skip Windows drive letters where the part before ':' is a single letter).
    if ":" in value:
        head = value.split(":", 1)[0]
        if len(head) > 1:
            return False
    return True


def _check_local_path(
    result: ValidationResult,
    path_value: str,
    yaml_path: str,
    base_path: Optional[Union[str, "PathLike[str]"]] = None,
) -> None:
    """Verify a local path exists; record missing paths as errors and IO failures as warnings."""
    candidate = Path(path_value)
    if not candidate.is_absolute() and base_path is not None:
        candidate = (Path(base_path) / candidate).resolve()
    try:
        exists = candidate.exists()
    except OSError as exc:
        result.append_warning(
            yaml_path,
            f"Could not verify local path '{path_value}': {exc}",
            error_code="PATH_CHECK_FAILED",
            value=path_value,
        )
        return
    if not exists:
        result.append_error(
            yaml_path,
            f"Local path '{path_value}' does not exist.",
            error_code="PATH_NOT_FOUND",
            value=path_value,
        )


def _validate_command_job(job: CommandJob) -> ValidationResult:
    """Run local validation checks on a CommandJob, collecting every finding into a ValidationResult."""
    result = ValidationResult()

    # Required-field checks.
    if not job.command or not job.command.strip():
        result.append_error(
            "command", "'command' is required and cannot be empty for a CommandJob.", error_code="MISSING_FIELD"
        )
    if not job.environment_image_reference or not job.environment_image_reference.strip():
        result.append_error(
            "environment_image_reference",
            "'environment_image_reference' is required and cannot be empty for a CommandJob.",
            error_code="MISSING_FIELD",
        )
    if not job.compute or not job.compute.strip():
        result.append_error(
            "compute", "'compute' is required and cannot be empty for a CommandJob.", error_code="MISSING_FIELD"
        )

    # Code-field checks.
    if isinstance(job.code, str):
        if not job.code.strip():
            result.append_error(
                "code",
                "'code' cannot be an empty string. Omit it or provide a valid local path or datastore URI.",
                error_code="INVALID_VALUE",
                value=job.code,
            )
        elif job.code.startswith(_GIT_PATH_PREFIXES):
            result.append_error(
                "code",
                f"Invalid code value: {job.code}. Git paths are not supported.",
                error_code="INVALID_VALUE",
                value=job.code,
            )
        elif _path_looks_local(job.code):
            _check_local_path(result, job.code, "code", base_path=job._base_path)

    # Inputs: verify any local-looking paths exist.
    if job.inputs:
        for key, job_input in job.inputs.items():
            path_value = getattr(job_input, "path", None)
            if isinstance(path_value, str) and _path_looks_local(path_value):
                _check_local_path(result, path_value, f"inputs.{key}.path", base_path=job._base_path)

    # Outputs: verify any local-looking paths exist.
    if job.outputs:
        for key, job_output in job.outputs.items():
            path_value = getattr(job_output, "path", None)
            if isinstance(path_value, str) and _path_looks_local(path_value):
                _check_local_path(result, path_value, f"outputs.{key}.path", base_path=job._base_path)

    return result
