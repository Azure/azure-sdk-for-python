# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Manual performance comparison: native Rust bindings vs pure-Python transfer path.

This is NOT part of any automated test infrastructure. Run it manually:

    python manual_perf_test.py --account-name <account>

It benchmarks ``azure-storage-blob`` upload and download for a range of blob sizes,
comparing the transparent native acceleration (``azure-storage-extensions-transfer``)
against the built-in pure-Python implementation. The two paths are toggled in-process
via the ``AZURE_STORAGE_DISABLE_NATIVE_TRANSFER`` environment variable, which the SDK's
dispatch layer honors on every call.

Prerequisites:
  - The native extension is built and installed (maturin develop / pip install -e .).
  - You are logged in so DefaultAzureCredential can authenticate
    (e.g. `az login` or appropriate environment variables).
  - A target storage account, passed via --account-name (or AZURE_STORAGE_ACCOUNT_NAME),
    with your identity granted 'Storage Blob Data Contributor' on it.

Configuration is via command-line arguments (see --help). The only environment variable
this script reads directly is AZURE_STORAGE_ACCOUNT_NAME (as a fallback for --account-name);
AZURE_STORAGE_DISABLE_NATIVE_TRANSFER is set internally to toggle the transfer path.

Pass --sas to authenticate blob clients with a client-side user delegation SAS instead of the
AAD credential. Because a SAS authenticates via the URL, the native path skips the per-operation
token callback into Python, which is useful for isolating token-acquisition overhead from raw
transfer throughput.

Each case runs a number of warmup iterations (to account for connection setup / credential
caching) followed by the measured iterations. Results are reported as min / mean / median
wall-clock time and throughput (MiB/s), plus the native speedup.
"""

import argparse
import contextlib
import logging
import os
import re
import statistics
import time
import uuid
from datetime import datetime, timedelta, timezone

from azure.identity import DefaultAzureCredential

from azure.storage.blob import (
    BlobClient,
    BlobServiceClient,
    ContainerClient,
    ContainerSasPermissions,
    generate_container_sas,
)
from azure.storage.extensions.transfer import is_available

_DISABLE_ENV_VAR = "AZURE_STORAGE_DISABLE_NATIVE_TRANSFER"
_DISPATCH_LOGGER = "azure.storage.blob._transfer_native"

_MIB = 1024 * 1024

_DEFAULT_SIZES = "10KiB,1MiB,100MiB,1GiB"
_DEFAULT_ITERATIONS = 3
_DEFAULT_WARMUPS = 1
_DEFAULT_MAX_CONCURRENCY = 32
_DEFAULT_CONTAINER = "transfer-ext-perf"
_DEFAULT_SAS_EXPIRY_HOURS = 2.0

_SIZE_UNITS = {
    "": 1,
    "B": 1,
    "KIB": 1024,
    "MIB": 1024**2,
    "GIB": 1024**3,
    "KB": 1000,
    "MB": 1000**2,
    "GB": 1000**3,
}


def parse_size(text):
    """Parse a human-readable size like ``10KiB``, ``1MiB``, ``100MiB``, ``1GiB``, or ``512``.

    A bare number is interpreted as bytes. Binary (KiB/MiB/GiB) and decimal (KB/MB/GB) units
    are accepted, case-insensitively. Returns the size in bytes as an int.
    """
    match = re.fullmatch(r"\s*(\d+(?:\.\d+)?)\s*([a-zA-Z]*)\s*", text)
    if not match:
        raise argparse.ArgumentTypeError(f"Invalid size {text!r} (examples: 10KiB, 1MiB, 1GiB, 4096).")
    value, unit = match.group(1), match.group(2).upper()
    if unit not in _SIZE_UNITS:
        raise argparse.ArgumentTypeError(
            f"Unknown size unit in {text!r}. Use one of: B, KiB, MiB, GiB, KB, MB, GB."
        )
    return int(float(value) * _SIZE_UNITS[unit])


def format_size(num_bytes):
    """Format a byte count as a compact human-readable string (binary units)."""
    for unit, factor in (("GiB", 1024**3), ("MiB", 1024**2), ("KiB", 1024)):
        if num_bytes >= factor:
            return f"{num_bytes / factor:g} {unit}"
    return f"{num_bytes} B"


def _size_label(num_bytes):
    """A filename-safe label for a size, e.g. 10240 -> '10KiB'."""
    return format_size(num_bytes).replace(" ", "")


@contextlib.contextmanager
def native_path(enabled):
    """Force the native (enabled=True) or pure-Python (enabled=False) transfer path.

    Toggles AZURE_STORAGE_DISABLE_NATIVE_TRANSFER, which the SDK reads on every dispatch,
    and restores the previous value on exit.
    """
    previous = os.environ.get(_DISABLE_ENV_VAR)
    if enabled:
        os.environ.pop(_DISABLE_ENV_VAR, None)
    else:
        os.environ[_DISABLE_ENV_VAR] = "1"
    try:
        yield
    finally:
        if previous is None:
            os.environ.pop(_DISABLE_ENV_VAR, None)
        else:
            os.environ[_DISABLE_ENV_VAR] = previous


class _RecordCapture(logging.Handler):
    """Captures log records emitted by the native dispatch module."""

    def __init__(self):
        super().__init__(level=logging.DEBUG)
        self.records = []

    def emit(self, record):
        self.records.append(record)

    def messages(self):
        return [r.getMessage() for r in self.records]

    def clear(self):
        self.records.clear()


def ensure_container(credential, account_url, container):
    """Create the test container if it does not already exist."""
    client = ContainerClient(account_url, container, credential=credential)
    try:
        client.create_container()
        print(f"  Created container '{container}'")
    except Exception:  # pylint: disable=broad-except
        print(f"  Container '{container}' already exists (or create failed benignly)")


def create_user_delegation_sas(credential, account_name, account_url, container, expiry_hours):
    """Create a container-scoped user delegation SAS token, signed client-side.

    Requests a user delegation key from the service using the AAD *credential*, then signs the
    SAS locally with :func:`generate_container_sas` (no extra service round trip per blob). The
    returned query string grants read/write/create/delete/list on blobs in *container* and can
    be passed directly as the ``credential`` of a :class:`BlobClient`.

    Using a SAS makes the native transfer path authenticate via the URL instead of a token
    callback into Python, which removes the per-operation ``get_token`` overhead.
    """
    service = BlobServiceClient(account_url, credential=credential)
    start = datetime.now(timezone.utc) - timedelta(minutes=5)
    expiry = datetime.now(timezone.utc) + timedelta(hours=expiry_hours)
    delegation_key = service.get_user_delegation_key(key_start_time=start, key_expiry_time=expiry)
    return generate_container_sas(
        account_name=account_name,
        container_name=container,
        user_delegation_key=delegation_key,
        permission=ContainerSasPermissions(
            read=True, write=True, create=True, delete=True, list=True
        ),
        start=start,
        expiry=expiry,
    )


def verify_paths(auth, account_url, container):
    """Sanity-check that the native path is used when enabled and Python when disabled.

    Raises if the observed behavior doesn't match, so that a benchmark isn't silently
    comparing the Python path against itself. *auth* is the blob-client credential: either an
    AAD credential object or a SAS token string.
    """
    print("\n=== Verifying path selection ===")
    if not is_available():
        raise RuntimeError("Native extension not available — build it with `maturin develop`.")

    blob_name = f"verify-{uuid.uuid4().hex}.bin"
    blob_client = BlobClient(account_url, container, blob_name, credential=auth)
    payload = os.urandom(4 * _MIB)

    capture = _RecordCapture()
    dispatch_logger = logging.getLogger(_DISPATCH_LOGGER)
    dispatch_logger.setLevel(logging.DEBUG)
    dispatch_logger.addHandler(capture)
    try:
        # Native enabled: download must return the native downloader.
        with native_path(True):
            blob_client.upload_blob(payload, overwrite=True)
            capture.clear()
            downloader = blob_client.download_blob()
            data = downloader.readall()
        assert type(downloader).__name__ == "NativeStorageStreamDownloader", (
            f"Native path not taken when enabled (got {type(downloader).__name__}). "
            f"Dispatch log: {capture.messages()}"
        )
        assert data == payload, "Native round-trip mismatch during verification!"
        print("  VERIFIED: native path active when enabled")

        # Native disabled: download must return the standard Python downloader.
        with native_path(False):
            downloader = blob_client.download_blob()
            data = downloader.readall()
        assert type(downloader).__name__ != "NativeStorageStreamDownloader", (
            "Native path was taken even though it was disabled."
        )
        assert data == payload, "Python round-trip mismatch during verification!"
        print(f"  VERIFIED: python path active when disabled (got {type(downloader).__name__})")
    finally:
        dispatch_logger.removeHandler(capture)
        with contextlib.suppress(Exception):
            blob_client.delete_blob()


def _summarize(times, size_bytes):
    return {
        "min": min(times),
        "mean": statistics.mean(times),
        "median": statistics.median(times),
        "throughput_mib_s": (size_bytes / _MIB) / statistics.mean(times),
    }


def bench_upload(blob_client, payload, enabled, iterations, warmups, max_concurrency):
    """Time repeated uploads of *payload* on the selected path. Returns per-iteration seconds."""
    times = []
    with native_path(enabled):
        for _ in range(warmups):
            blob_client.upload_blob(payload, overwrite=True, max_concurrency=max_concurrency)
        for _ in range(iterations):
            start = time.perf_counter()
            blob_client.upload_blob(payload, overwrite=True, max_concurrency=max_concurrency)
            times.append(time.perf_counter() - start)
    return times


def bench_download(blob_client, expected_len, enabled, iterations, warmups, max_concurrency):
    """Time repeated full downloads (download_blob + readall) on the selected path.

    Timing spans the whole operation, including the native path's eager first-window fetch,
    so both paths are compared end-to-end. Returns per-iteration seconds.
    """
    times = []
    with native_path(enabled):
        for _ in range(warmups):
            data = blob_client.download_blob(max_concurrency=max_concurrency).readall()
            assert len(data) == expected_len, "Download length mismatch during warmup!"
        for _ in range(iterations):
            start = time.perf_counter()
            data = blob_client.download_blob(max_concurrency=max_concurrency).readall()
            times.append(time.perf_counter() - start)
            assert len(data) == expected_len, "Download length mismatch during measurement!"
    return times


def _fmt_row(label, stats):
    return (
        f"    {label:<8} "
        f"min={stats['min']:.3f}s  "
        f"mean={stats['mean']:.3f}s  "
        f"median={stats['median']:.3f}s  "
        f"throughput={stats['throughput_mib_s']:.1f} MiB/s"
    )


def _print_comparison(op, python_stats, native_stats):
    speedup = python_stats["mean"] / native_stats["mean"] if native_stats["mean"] else float("nan")
    print(f"  {op}:")
    print(_fmt_row("python", python_stats))
    print(_fmt_row("native", native_stats))
    print(f"    speedup (python_mean / native_mean): {speedup:.2f}x")


def run_benchmarks(auth, args):
    print("\n=== Benchmarks ===")
    print(
        f"sizes={[format_size(s) for s in args.sizes]}  iterations={args.iterations}  "
        f"warmups={args.warmups}  max_concurrency={args.max_concurrency}  "
        f"auth={'user-delegation-SAS' if args.sas else 'AAD'}"
    )
    summary = []
    for size_bytes in args.sizes:
        print(f"\n--- Blob size: {format_size(size_bytes)} ({size_bytes} bytes) ---")
        payload = os.urandom(size_bytes)
        blob_name = f"perf-{_size_label(size_bytes)}-{uuid.uuid4().hex}.bin"
        blob_client = BlobClient(args.account_url, args.container, blob_name, credential=auth)

        try:
            # Upload benchmark (this also leaves a blob in place for the download benchmark).
            up_python = _summarize(
                bench_upload(blob_client, payload, False, args.iterations, args.warmups, args.max_concurrency),
                size_bytes,
            )
            up_native = _summarize(
                bench_upload(blob_client, payload, True, args.iterations, args.warmups, args.max_concurrency),
                size_bytes,
            )
            _print_comparison("upload", up_python, up_native)

            # Download benchmark.
            dl_python = _summarize(
                bench_download(blob_client, size_bytes, False, args.iterations, args.warmups, args.max_concurrency),
                size_bytes,
            )
            dl_native = _summarize(
                bench_download(blob_client, size_bytes, True, args.iterations, args.warmups, args.max_concurrency),
                size_bytes,
            )
            _print_comparison("download", dl_python, dl_native)

            summary.append((size_bytes, up_python, up_native, dl_python, dl_native))
        finally:
            with contextlib.suppress(Exception):
                blob_client.delete_blob()

    _print_summary(summary)


def _print_summary(summary):
    print("\n=== Summary (mean throughput MiB/s, native speedup) ===")
    header = f"  {'size':>10} | {'up py':>8} {'up nat':>8} {'up x':>6} | {'dl py':>8} {'dl nat':>8} {'dl x':>6}"
    print(header)
    print("  " + "-" * (len(header) - 2))
    for size_bytes, up_py, up_nat, dl_py, dl_nat in summary:
        up_speed = up_py["mean"] / up_nat["mean"] if up_nat["mean"] else float("nan")
        dl_speed = dl_py["mean"] / dl_nat["mean"] if dl_nat["mean"] else float("nan")
        print(
            f"  {format_size(size_bytes):>10} | "
            f"{up_py['throughput_mib_s']:>8.1f} {up_nat['throughput_mib_s']:>8.1f} {up_speed:>5.2f}x | "
            f"{dl_py['throughput_mib_s']:>8.1f} {dl_nat['throughput_mib_s']:>8.1f} {dl_speed:>5.2f}x"
        )


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Benchmark azure-storage-blob transfers: native Rust bindings vs pure Python.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--account-name",
        default=os.environ.get("AZURE_STORAGE_ACCOUNT_NAME"),
        help="Target storage account name (falls back to AZURE_STORAGE_ACCOUNT_NAME).",
    )
    parser.add_argument(
        "--container",
        default=_DEFAULT_CONTAINER,
        help="Container to use for the benchmark blobs.",
    )
    parser.add_argument(
        "--sizes",
        default=_DEFAULT_SIZES,
        help="Comma-separated blob sizes, e.g. '10KiB,1MiB,100MiB,1GiB'.",
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=_DEFAULT_ITERATIONS,
        help="Measured iterations per case.",
    )
    parser.add_argument(
        "--warmups",
        type=int,
        default=_DEFAULT_WARMUPS,
        help="Warmup iterations discarded before measuring.",
    )
    parser.add_argument(
        "--max-concurrency",
        type=int,
        default=_DEFAULT_MAX_CONCURRENCY,
        help="max_concurrency passed to upload/download.",
    )
    parser.add_argument(
        "--sas",
        action="store_true",
        help="Authenticate blob clients with a client-side user delegation SAS instead of the "
        "AAD credential. This avoids the per-operation token callback into Python.",
    )
    parser.add_argument(
        "--sas-expiry-hours",
        type=float,
        default=_DEFAULT_SAS_EXPIRY_HOURS,
        help="Lifetime of the generated user delegation SAS, in hours (only used with --sas).",
    )
    args = parser.parse_args(argv)

    if not args.account_name:
        parser.error("--account-name is required (or set AZURE_STORAGE_ACCOUNT_NAME).")
    if args.iterations < 1:
        parser.error("--iterations must be at least 1.")
    if args.warmups < 0:
        parser.error("--warmups must be non-negative.")
    if args.max_concurrency < 1:
        parser.error("--max-concurrency must be at least 1.")
    if args.sas and args.sas_expiry_hours <= 0:
        parser.error("--sas-expiry-hours must be greater than 0.")

    args.sizes = [parse_size(s) for s in args.sizes.split(",") if s.strip()]
    if not args.sizes:
        parser.error("--sizes must contain at least one size.")
    args.account_url = f"https://{args.account_name}.blob.core.windows.net"
    return args


def main(argv=None):
    args = parse_args(argv)
    credential = DefaultAzureCredential()
    print(f"Account: {args.account_name}")
    print("Ensuring container exists...")
    ensure_container(credential, args.account_url, args.container)

    if args.sas:
        print("Generating client-side user delegation SAS...")
        auth = create_user_delegation_sas(
            credential, args.account_name, args.account_url, args.container, args.sas_expiry_hours
        )
        print("  Blob clients will authenticate via SAS (no token callback into Python).")
    else:
        auth = credential
        print("  Blob clients will authenticate via AAD credential.")

    verify_paths(auth, args.account_url, args.container)
    run_benchmarks(auth, args)

    print("\nAll benchmarks complete.")


if __name__ == "__main__":
    main()
