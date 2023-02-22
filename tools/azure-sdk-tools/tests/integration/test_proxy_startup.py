from devtools_testutils import test_proxy
from urllib3 import PoolManager, Retry


# if os.getenv("REQUESTS_CA_BUNDLE"):
#     http_client = PoolManager(
#         retries=Retry(total=3, raise_on_status=False),
#         cert_reqs="CERT_REQUIRED",
#         ca_certs=os.getenv("REQUESTS_CA_BUNDLE"),
#     )
# else:
http_client = PoolManager(retries=Retry(total=1, raise_on_status=False))

class TestProxyIntegration:
    # These tests are checking spinup of the proxy, not automatic redirect.
    # Therefor we are not using recorded_by_proxy decorator or recorded_test fixture
    def test_tool_spinup_http():
        result = http_client.request("GET", "http://localhost:5000/Info/Available")

        breakpoint()
