import unittest
from datetime import datetime
import dateutil.tz

from azure.communication.callingserver._shared.utils import(
    _convert_datetime_to_utc_int
)

class UtilsTest(unittest.TestCase):

    def test_convert_datetime_to_utc_int(self):
        # UTC
        utc_time_in_sec = _convert_datetime_to_utc_int(datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=dateutil.tz.tzutc()))
        assert utc_time_in_sec == 0
        # PST is UTC-8
        pst_time_in_sec = _convert_datetime_to_utc_int(datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=dateutil.tz.gettz('America/Vancouver')))
        assert pst_time_in_sec == 8 * 3600
        # EST is UTC-5
        est_time_in_sec = _convert_datetime_to_utc_int(datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=dateutil.tz.gettz('America/New_York')))
        assert est_time_in_sec == 5 * 3600
        # CST is UTC+8
        cst_time_in_sec = _convert_datetime_to_utc_int(datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=dateutil.tz.gettz('Asia/Shanghai')))
        assert cst_time_in_sec == -8 * 3600

if __name__ == "__main__":
    unittest.main()
