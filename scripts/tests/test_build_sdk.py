import os.path
import sys

sys.path += [os.path.dirname(__file__)]

from build_sdk import *

def test_guess_autorest_options():
    assert guess_service_info_from_path("specification/compute/resource-manager/readme.md") == {"rp_name": "compute", "is_arm": True}
    assert guess_service_info_from_path("specification/servicefabric/data-plane/readme.md") == {"rp_name": "servicefabric", "is_arm": False}