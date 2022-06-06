import unittest
from datetime import datetime
from azure.communication.chat._shared.utils import create_access_token
from azure.communication.chat._shared.utils import get_current_utc_as_int
import dateutil.tz
import base64

from azure.communication.chat._shared.utils import(
    _convert_datetime_to_utc_int
)

class UtilsTest(unittest.TestCase):

    @staticmethod
    def get_token_with_custom_expiry(expires_on):
        expiry_json = '{"exp": ' + str(expires_on) + '}'
        base64expiry = base64.b64encode(
            expiry_json.encode('utf-8')).decode('utf-8').rstrip("=")
        token_template = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9." +\
            base64expiry + ".adM-ddBZZlQ1WlN3pdPBOF5G4Wh9iZpxNP_fSvpF4cWs"
        return token_template

    def test_convert_datetime_to_utc_int(self):
        # UTC
        utc_time_in_sec = _convert_datetime_to_utc_int(datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=dateutil.tz.tzutc()))
        assert utc_time_in_sec == 0        
        # UTC naive (without a timezone specified)
        utc_naive_time_in_sec = _convert_datetime_to_utc_int(datetime(1970, 1, 1, 0, 0, 0, 0))
        assert utc_naive_time_in_sec == 0
        # PST is UTC-8
        pst_time_in_sec = _convert_datetime_to_utc_int(datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=dateutil.tz.gettz('America/Vancouver')))
        assert pst_time_in_sec == 8 * 3600
        # EST is UTC-5
        est_time_in_sec = _convert_datetime_to_utc_int(datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=dateutil.tz.gettz('America/New_York')))
        assert est_time_in_sec == 5 * 3600
        # CST is UTC+8
        cst_time_in_sec = _convert_datetime_to_utc_int(datetime(1970, 1, 1, 0, 0, 0, 0, tzinfo=dateutil.tz.gettz('Asia/Shanghai')))
        assert cst_time_in_sec == -8 * 3600

        
    def test_access_token_expiry_deserialized_correctly_from_payload(self):
        start_timestamp = get_current_utc_as_int()
        token_validity_minutes = 60
        token_expiry = start_timestamp + token_validity_minutes * 60

        token = create_access_token(
            self.get_token_with_custom_expiry(token_expiry))

        self.assertEqual(token.expires_on, token_expiry)

if __name__ == "__main__":
    unittest.main()
