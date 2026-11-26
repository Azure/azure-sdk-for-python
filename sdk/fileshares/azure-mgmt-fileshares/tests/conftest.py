# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
import glob
import json
import os
import pytest
from dotenv import load_dotenv
from devtools_testutils import (
    is_live,
    is_live_and_not_recording,
    test_proxy,
    add_general_regex_sanitizer,
    add_body_key_sanitizer,
    add_header_regex_sanitizer,
    remove_batch_sanitizers,
)

load_dotenv()

from _fs_test_helpers import RESOURCE_GROUP  # type: ignore[import-not-found]  # pylint: disable=wrong-import-position

_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))


# For security, please avoid recording sensitive identity information in recordings
@pytest.fixture(scope="session", autouse=True)
def add_sanitizers(test_proxy):
    fileshares_subscription_id = os.environ.get("AZURE_SUBSCRIPTION_ID", "00000000-0000-0000-0000-000000000000")
    fileshares_tenant_id = os.environ.get("AZURE_TENANT_ID", "00000000-0000-0000-0000-000000000000")
    fileshares_client_id = os.environ.get("AZURE_CLIENT_ID", "00000000-0000-0000-0000-000000000000")
    fileshares_client_secret = os.environ.get("AZURE_CLIENT_SECRET", "00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=fileshares_subscription_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=fileshares_tenant_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=fileshares_client_id, value="00000000-0000-0000-0000-000000000000")
    add_general_regex_sanitizer(regex=fileshares_client_secret, value="00000000-0000-0000-0000-000000000000")

    add_header_regex_sanitizer(key="Set-Cookie", value="[set-cookie;]")
    add_header_regex_sanitizer(key="Cookie", value="cookie;")
    # ARM echoes the caller's tenant and object ID in this header.
    add_header_regex_sanitizer(key="x-ms-operation-identifier", value="Sanitized")
    add_body_key_sanitizer(json_path="$..access_token", value="access_token")

    # Preserve resource names and IDs in recorded response bodies — tests assert on them
    # and use the variables API to keep names stable across record/playback.
    #   - AZSDK3493: $..name body key sanitizer
    #   - AZSDK3430: $..id body key sanitizer
    remove_batch_sanitizers(["AZSDK3493", "AZSDK3430"])


_ASSETS_JSON = "sdk/fileshares/azure-mgmt-fileshares/assets.json"


def _recordings_dir():
    """Returns the recordings folder of this package's assets checkout, found via the test proxy breadcrumb."""
    for breadcrumb in glob.glob(os.path.join(_REPO_ROOT, ".assets", "breadcrumb", "*.breadcrumb")):
        with open(breadcrumb, encoding="utf-8-sig") as breadcrumb_file:
            for line in breadcrumb_file:
                fields = line.strip().split(";")
                if len(fields) >= 2 and fields[0].replace("\\", "/") == _ASSETS_JSON:
                    return os.path.join(
                        _REPO_ROOT,
                        ".assets",
                        fields[1],
                        "python",
                        *os.path.dirname(_ASSETS_JSON).split("/"),
                        "tests",
                        "recordings"
                    )
    return None


# Listing file shares by subscription returns every share in the shared test subscription. Keep only
# this suite's resource group in recorded list responses, so recordings don't capture unrelated
# resources' names, IDs and host names. Runs only while recording, on the test's own recording file.
@pytest.fixture(autouse=True)
def scope_recorded_share_lists(request):
    yield
    if not is_live() or is_live_and_not_recording() or request.node.cls is None:
        return
    file_name = "{}{}{}.json".format(
        os.path.basename(str(request.node.fspath)), request.node.cls.__name__, request.node.name
    )
    recordings_dir = _recordings_dir()
    path = os.path.join(recordings_dir, file_name) if recordings_dir else None
    marker = "/resourcegroups/{}/".format(RESOURCE_GROUP.lower())
    if not path or not os.path.isfile(path):
        if request.node.get_closest_marker("live_test_only") is None:
            raise RuntimeError(
                "No recording found for {} in this package's assets checkout; the recording path may have "
                "changed, which would let unrelated resources into recordings.".format(file_name)
            )
        return
    with open(path, encoding="utf-8") as recording_file:
        recording = json.load(recording_file)
    changed = False
    for entry in recording.get("Entries", []):
        body = entry.get("ResponseBody")
        items = body.get("value") if isinstance(body, dict) else None
        if (
            entry.get("RequestMethod") != "GET"
            or "/providers/Microsoft.FileShares/fileShares?" not in entry.get("RequestUri", "")
            or not isinstance(items, list)
        ):
            continue
        kept = [item for item in items if marker in str(item.get("id", "")).lower()]
        if len(kept) != len(items):
            body["value"] = kept
            entry.get("ResponseHeaders", {}).pop("Content-Length", None)
            changed = True
    if changed:
        with open(path, "w", encoding="utf-8") as recording_file:
            json.dump(recording, recording_file, indent=2)
