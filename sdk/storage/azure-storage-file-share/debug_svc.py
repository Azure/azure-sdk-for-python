import sys
import azure.storage.fileshare._models as models

orig_deserialize = models.service_properties_deserialize


def debug_deserialize(generated):
    print(f"DEBUG generated type: {type(generated)}", file=sys.stderr)
    if hasattr(generated, "hour_metrics"):
        hm = generated.hour_metrics
        print(f"DEBUG hour_metrics type: {type(hm)}", file=sys.stderr)
        if hm:
            data = getattr(hm, "_data", "NO _data")
            print(f"DEBUG hm._data: {data}", file=sys.stderr)
            rp = getattr(hm, "retention_policy", "NO retention_policy")
            print(f"DEBUG retention_policy: {type(rp)} = {rp}", file=sys.stderr)
    return orig_deserialize(generated)


models.service_properties_deserialize = debug_deserialize
import azure.storage.fileshare._share_service_client as ssc

ssc.service_properties_deserialize = debug_deserialize

import pytest

pytest.main(
    [
        "-x",
        "tests/test_file_service_properties.py::TestFileServiceProperties::test_file_service_properties",
        "-q",
        "--tb=short",
        "--no-header",
        "-s",
    ]
)
