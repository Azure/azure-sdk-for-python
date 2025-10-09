from datetime import datetime
from enum import Enum
import os


class ServiceVersion(str, Enum):

    V2019_02_02 = "2019-02-02"
    V2019_07_07 = "2019-07-07"
    V2019_10_10 = "2019-10-10"
    V2019_12_12 = "2019-12-12"
    V2020_02_10 = "2020-02-10"
    V2020_04_08 = "2020-04-08"
    V2020_06_12 = "2020-06-12"
    V2020_08_04 = "2020-08-04"


service_version_map = {
    "V2019_02_02": ServiceVersion.V2019_02_02,
    "V2019_07_07": ServiceVersion.V2019_07_07,
    "V2019_10_10": ServiceVersion.V2019_10_10,
    "V2019_12_12": ServiceVersion.V2019_12_12,
    "V2020_02_10": ServiceVersion.V2020_02_10,
    "V2020_04_08": ServiceVersion.V2020_04_08,
    "V2020_06_12": ServiceVersion.V2020_06_12,
    "V2020_08_04": ServiceVersion.V2020_08_04,
    "LATEST": ServiceVersion.V2020_08_04,
    "LATEST_PLUS_1": ServiceVersion.V2020_06_12,
}


def is_version_before(test_version):
    """Return True if the current version is after a given one or if the
    service version is not set.
    """
    current_version = service_version_map.get(os.environ.get("AZURE_LIVE_TEST_SERVICE_VERSION"))
    if not current_version:
        return True
    current_version_data = datetime.strptime(current_version, "%Y-%m-%d")
    test_version_minimum = datetime.strptime(test_version, "%Y-%m-%d")
    ret = current_version_data < test_version_minimum
    return ret
