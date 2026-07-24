# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""Quick manual test for the native transfer extension.

This is NOT part of any automated test infrastructure. Run it manually:

    python manual_test.py

Prerequisites:
  - The native extension is built and installed (maturin develop / pip install -e .)
  - You are logged in so DefaultAzureCredential can authenticate
    (e.g. `az login` or appropriate environment variables).
  - Set AZURE_STORAGE_ACCOUNT_NAME to the target storage account (required),
    and ensure your identity has 'Storage Blob Data Contributor' on it.

How native usage is verified:
  - Direct API: is_available() must be True and the round-trip must succeed.
  - Through the SDK: the dispatch module (azure.storage.blob._transfer_native)
    logs an INFO record "Used native Rust extension for ..." when the native
    path is taken, and a WARNING if it fails and falls back. This script
    installs a handler on that logger and asserts those records appear.
    Additionally, download returns a 'NativeStorageStreamDownloader' object
    only when native acceleration was used.
"""

import logging
import os
import uuid

from azure.identity import DefaultAzureCredential

from azure.storage.extensions.transfer import (
    download_blob,
    is_available,
    upload_blob,
)

ACCOUNT_NAME = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME")
if not ACCOUNT_NAME:
    raise SystemExit("AZURE_STORAGE_ACCOUNT_NAME environment variable must be set.")
ACCOUNT_URL = f"https://{ACCOUNT_NAME}.blob.core.windows.net"
CONTAINER = "transfer-ext-test"
STORAGE_SCOPE = "https://storage.azure.com/.default"

_DISPATCH_LOGGER = "azure.storage.blob._transfer_native"


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


def _get_token(credential):
    return credential.get_token(STORAGE_SCOPE).token


def ensure_container(credential):
    """Create the test container if it does not already exist (uses the Python SDK)."""
    from azure.storage.blob import ContainerClient

    container = ContainerClient(ACCOUNT_URL, CONTAINER, credential=credential)
    try:
        container.create_container()
        print(f"  Created container '{CONTAINER}'")
    except Exception:  # pylint: disable=broad-except
        print(f"  Container '{CONTAINER}' already exists (or create failed benignly)")


def test_direct_extension(credential):
    """Exercise upload_blob / download_blob from the extension directly."""
    print("\n=== Direct extension API ===")
    print(f"is_available(): {is_available()}")
    if not is_available():
        raise RuntimeError("Native extension not available — build it with `maturin develop`.")

    token = _get_token(credential)
    blob_name = f"direct-{uuid.uuid4().hex}.bin"

    # A payload big enough to exercise the chunked / parallel path (16 MiB).
    payload = os.urandom(16 * 1024 * 1024)
    print(f"Uploading {len(payload)} bytes to '{blob_name}'...")
    result = upload_blob(
        account_url=ACCOUNT_URL,
        container=CONTAINER,
        blob=blob_name,
        data=payload,
        access_token=token,
        overwrite=True,
        content_type="application/octet-stream",
        max_concurrency=8,
    )
    print(f"  Upload result: {result}")

    print("Downloading it back...")
    downloaded = download_blob(
        account_url=ACCOUNT_URL,
        container=CONTAINER,
        blob=blob_name,
        access_token=token,
        max_concurrency=8,
        expected_size=len(payload),
    )
    print(f"  Downloaded {len(downloaded)} bytes")
    assert downloaded == payload, "Round-trip mismatch (direct extension)!"
    print("  OK: round-trip matches (native by definition — direct call)")


def test_through_blob_sdk(credential):
    """Exercise the transparent acceleration path via azure-storage-blob.

    Verifies the native path was actually taken (not a silent Python fallback)
    by inspecting the dispatch logger and the returned downloader type.
    """
    print("\n=== Through azure-storage-blob (transparent acceleration) ===")
    from azure.storage.blob import BlobClient

    capture = _RecordCapture()
    dispatch_logger = logging.getLogger(_DISPATCH_LOGGER)
    dispatch_logger.setLevel(logging.DEBUG)
    dispatch_logger.addHandler(capture)
    try:
        blob_name = f"sdk-{uuid.uuid4().hex}.bin"
        payload = os.urandom(8 * 1024 * 1024)

        blob_client = BlobClient(ACCOUNT_URL, CONTAINER, blob_name, credential=credential)

        print(f"Uploading {len(payload)} bytes via BlobClient.upload_blob...")
        capture.clear()
        blob_client.upload_blob(payload, overwrite=True)
        upload_msgs = capture.messages()
        print(f"  Dispatch log: {upload_msgs}")
        assert any("Used native Rust extension for blob upload." in m for m in upload_msgs), (
            "Upload did NOT use the native path (it fell back to Python). "
            f"Dispatch log: {upload_msgs}"
        )
        print("  VERIFIED: upload used native path")

        print("Downloading via BlobClient.download_blob().readall()...")
        capture.clear()
        downloader = blob_client.download_blob()
        download_msgs = capture.messages()
        print(f"  Dispatch log: {download_msgs}")
        print(f"  Downloader type: {type(downloader).__name__}")
        assert type(downloader).__name__ == "NativeStorageStreamDownloader", (
            "Download did NOT use the native path (returned a Python "
            f"StorageStreamDownloader). Dispatch log: {download_msgs}"
        )
        assert any("Used native Rust extension for blob download." in m for m in download_msgs), (
            f"Expected native download log record. Dispatch log: {download_msgs}"
        )
        print("  VERIFIED: download used native path")

        downloaded = downloader.readall()
        print(f"  Downloaded {len(downloaded)} bytes")
        assert downloaded == payload, "Round-trip mismatch (blob SDK)!"
        print("  OK: round-trip matches")
    finally:
        dispatch_logger.removeHandler(capture)


def main():
    credential = DefaultAzureCredential()
    print(f"Account: {ACCOUNT_NAME}")
    print("Ensuring container exists...")
    ensure_container(credential)

    test_direct_extension(credential)
    test_through_blob_sdk(credential)

    print("\nAll manual checks passed.")


if __name__ == "__main__":
    main()
