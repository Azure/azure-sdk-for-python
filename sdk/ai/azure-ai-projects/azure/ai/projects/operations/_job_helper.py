# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import hashlib
import math
import os
import re
import urllib.error
import urllib.request
from fnmatch import fnmatch
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, TextIO, Tuple, Union
from os import PathLike
from urllib.parse import urlparse

from azure.storage.blob import BlobClient

from ..models._enums import AssetTypes
from ..models._models import Output as _Output
from ..models._patch_jobs import CommandJob, ValidationResult

_TERMINAL_JOB_STATUSES = frozenset({"completed", "failed", "canceled", "notresponding", "paused", "unknown"})

_IN_PROGRESS_JOB_STATUSES = frozenset(
    {"notstarted", "queued", "preparing", "provisioning", "starting", "running", "cancelrequested"}
)

_FINALIZING_JOB_STATUS = "finalizing"

_FAILED_JOB_STATUS = "failed"

_FINALIZING_RUN_MARKER = "The activity completed successfully. Finalizing run..."

_DEFAULT_GET_CONTENT_TIMEOUT = (5, 120)

_POLLING_INTERVAL_MIN = int(os.environ.get("AZUREML_RUN_POLLING_INTERVAL_MIN", 2))

_POLLING_INTERVAL_MAX = int(os.environ.get("AZUREML_RUN_POLLING_INTERVAL_MAX", 60))

_COMMON_RUNTIME_STREAM_LOG_PATTERN = re.compile(r"user_logs/std_log[\D]*[0]*(?:_ps)?\.txt")

_COMMAND_JOB_LOG_PATTERN = re.compile(r"azureml-logs/[\d]{2}.+\.txt")

_MAX_CONCURRENCY = 8

_NAMED_OUTPUTS_DIR = "named-outputs"

_ARTIFACTS_DIR = "artifacts"

# Special output name that refers to the job's default artifact store.
_DEFAULT_ARTIFACT_STORE_OUTPUT_NAME = "default"

_TMP_SUFFIX = ".tmp"

_GIT_PATH_PREFIXES: Tuple[str, ...] = ("git://", "git+")


def _resolve_symlink(path: Path) -> Path:
    """Follow symlink chains until the real target is reached."""
    while path.is_symlink():
        link_path = path.resolve()
        if not link_path.is_absolute():
            link_path = path.parent.joinpath(link_path).resolve()
        path = link_path
    return path


def _load_gitignore_patterns(directory: Path) -> List[str]:
    """Load patterns from a .gitignore file in the given directory."""
    gitignore_file = ".gitignore"
    gitignore = directory / gitignore_file
    if not gitignore.is_file():
        return []
    patterns = []
    with open(gitignore, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            if line and not line.startswith("#"):
                patterns.append(line)
    return patterns


def _is_excluded(rel_path: str, patterns: List[str]) -> bool:
    """Check if a relative path matches any gitignore-style pattern."""
    rel_path = rel_path.replace("\\", "/")
    parts = rel_path.split("/")
    for pattern in patterns:
        stripped = pattern.rstrip("/")
        for part in parts:
            if fnmatch(part, stripped):
                return True
        if fnmatch(rel_path, pattern):
            return True
    return False


def _update_hash(path: Path, sha: "hashlib._Hash") -> None:
    """Read file at *path* in chunks and feed each chunk into *sha*."""
    chunk_size = 1024
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            sha.update(chunk)


def _collect_files(directory: Path, ignore_patterns: List[str]) -> List[Tuple[Path, str]]:
    """Collect all files in a directory, respecting gitignore patterns and resolving symlinks.

    Returns a sorted list of (resolved_path, relative_posix_path) tuples.
    """
    files: List[Tuple[Path, str]] = []
    for root, _, filenames in os.walk(directory, followlinks=True):
        for filename in filenames:
            abs_path = Path(root, filename)
            rel_path = abs_path.relative_to(directory).as_posix()
            if not _is_excluded(rel_path, ignore_patterns):
                files.append((_resolve_symlink(abs_path), rel_path))
    return sorted(files, key=lambda x: x[1].lower())


def _content_hash(path: Path) -> str:
    """Compute a truncated SHA-256 content hash for a file or directory.

    Respects ``.gitignore`` when hashing directories.
    """
    path = _resolve_symlink(path)
    sha = hashlib.sha256()
    if path.is_file():
        file_list = [(path, path.name)]
    else:
        ignore_patterns = _load_gitignore_patterns(path)
        file_list = _collect_files(path, ignore_patterns)
    sha.update(str(len(file_list)).encode())
    for abs_path, rel_path in file_list:
        sha.update(("#" + rel_path + "#").encode())
        sha.update(str(os.path.getsize(abs_path)).encode())
    for abs_path, _ in file_list:
        _update_hash(abs_path, sha)
    return sha.hexdigest()[:8]


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


def _get_sorted_streamable_logs(
    logs_iterable: Iterable[str],
    processed_logs: Optional[Dict[str, int]] = None,
) -> List[str]:
    """Return streamable CommandJob log file names, sorted, starting from the last processed entry."""
    processed_logs = processed_logs if processed_logs else {}
    logs = list(logs_iterable)
    filtered_logs = [x for x in logs if _COMMON_RUNTIME_STREAM_LOG_PATTERN.search(x)]
    if not filtered_logs:
        filtered_logs = [x for x in logs if _COMMAND_JOB_LOG_PATTERN.search(x)]
    filtered_logs.sort()
    previously_printed_index = 0
    for i, name in enumerate(filtered_logs):
        if processed_logs.get(name):
            previously_printed_index = i
        else:
            break
    return filtered_logs[previously_printed_index:]


def _incremental_print(
    log: str,
    processed_logs: Dict[str, int],
    current_log_name: str,
    fileout: TextIO,
) -> None:
    """Print only the new lines of *log* that have not yet been written for *current_log_name*."""
    lines = log.splitlines()
    doc_length = len(lines)
    if doc_length == 0:
        return
    previous_printed_lines = processed_logs.get(current_log_name, 0)
    if previous_printed_lines == 0:
        fileout.write("\n")
        fileout.write("Streaming " + current_log_name + "\n")
        fileout.write("=" * (len(current_log_name) + 10) + "\n")
        fileout.write("\n")
    for line in lines[previous_printed_lines:]:
        fileout.write(line + "\n")
    processed_logs[current_log_name] = doc_length


def _wait_before_polling(current_seconds: float) -> int:
    """Sigmoid backoff bounded by ``_POLLING_INTERVAL_MIN`` and ``_POLLING_INTERVAL_MAX``."""
    if current_seconds < 0:
        raise ValueError("current_seconds must be positive")
    duration = int(_POLLING_INTERVAL_MAX / (1.0 + 100 * math.exp(-current_seconds / 20.0)))
    return max(_POLLING_INTERVAL_MIN, duration)


def _download_log_text(
    url: str,
    timeout: Tuple[float, float] = _DEFAULT_GET_CONTENT_TIMEOUT,
) -> str:
    """Fetch the body of a log file URL as text, returning ``""`` on 404."""
    _, read_timeout = timeout
    try:
        with urllib.request.urlopen(url, timeout=read_timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return ""
        raise


def _safe_join(dest: Path, rel: str) -> Path:
    """Join *rel* under *dest*, rejecting traversal escapes and OS-absolute relpaths."""
    if not rel:
        raise ValueError("Empty artifact path.")
    rel_path = Path(rel)
    if rel_path.is_absolute() or rel_path.drive:
        raise ValueError(f"Artifact path '{rel}' must be relative.")
    dest_root = dest.resolve()
    candidate = (dest_root / rel_path).resolve()
    try:
        candidate.relative_to(dest_root)
    except ValueError as exc:
        raise ValueError(f"Artifact path '{rel}' escapes the destination directory.") from exc
    return candidate


def _atomic_write(local_path: Path, downloader: Any) -> None:
    """Stream *downloader* to ``<local_path>.tmp`` then atomically rename to *local_path*."""
    tmp_path = local_path.with_name(local_path.name + _TMP_SUFFIX)
    try:
        with open(tmp_path, "wb") as fh:
            downloader.readinto(fh)
        os.replace(tmp_path, local_path)
    except BaseException:
        try:
            tmp_path.unlink()
        except OSError:
            pass
        raise


def _sweep_tmp_files(root: Path) -> None:
    """Best-effort removal of stale ``*.tmp`` files left by previous interrupted runs."""
    if not root.exists():
        return
    for stale in root.rglob("*" + _TMP_SUFFIX):
        try:
            stale.unlink()
        except OSError:
            pass


def _collect_artifact_paths(
    list_artifacts: Callable[..., Any],
    name: str,
    experiment_id: str,
) -> List[str]:
    """Page through the list-artifacts API and return every artifact path."""
    paths: List[str] = []
    continuation: Optional[str] = None
    while True:
        page = list_artifacts(
            name,
            experiment_id,
            name,
            continuation_token_parameter=continuation,
        )
        for artifact in page.value or []:
            if artifact.path:
                paths.append(artifact.path)
        continuation = page.continuation_token
        if not continuation:
            break
    return paths


def _group_paths_by_prefix(paths: Iterable[str]) -> Set[str]:
    """Return the unique top-level path segments (or full path if no ``/``)."""
    return {p.split("/", 1)[0] for p in paths if p}


def _resolve_artifact_uris(
    get_content_information: Callable[..., Any],
    name: str,
    experiment_id: str,
    prefixes: Iterable[str],
) -> Dict[str, Tuple[str, int]]:
    """Page API 3 once per prefix and return ``path -> (content_uri, content_length)``."""
    uri_map: Dict[str, Tuple[str, int]] = {}
    for prefix in prefixes:
        if not prefix:
            continue
        continuation: Optional[str] = None
        while True:
            page = get_content_information(
                name,
                experiment_id,
                name,
                path=prefix,
                continuation_token_parameter=continuation,
            )
            for item in page.value or []:
                if item.path and item.content_uri:
                    uri_map[item.path] = (item.content_uri, item.content_length or 0)
            continuation = page.continuation_token
            if not continuation:
                break
    return uri_map


def _download_artifact_to_path(
    content_uri: str,
    local_path: Path,
    max_chunks_per_file: int,
) -> int:
    """Download a single SAS-signed blob to *local_path* atomically; return bytes written."""
    local_path.parent.mkdir(parents=True, exist_ok=True)
    with BlobClient.from_blob_url(blob_url=content_uri) as blob_client:
        downloader = blob_client.download_blob(max_concurrency=max_chunks_per_file)
        size = downloader.size or 0
        _atomic_write(local_path, downloader)
    return size
