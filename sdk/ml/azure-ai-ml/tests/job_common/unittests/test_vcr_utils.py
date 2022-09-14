from typing import Dict, Any, List, Tuple
from urllib.parse import urlparse


# the headers we want VCR to filter out of requests
def vcr_header_filters() -> List[Tuple[str, str]]:
    return [
        ("Authorization", "filtered-value"),
        ("x-ms-client-request-id", "filtered-value"),
        ("User-Agent", "filtered-value"),
        ("x-ms-date", "filtered-value"),
        ("x-ms-version", "filtered-value"),
        ("x-ms-range", "filtered-value"),
    ]


def before_record_cb(request: Dict[str, Any]) -> dict:
    try:
        u = urlparse(request.uri)
        empty, sub, sub_d, rg, rg_d, rest = u.path.split("/", 5)
        assert sub == "subscriptions"
        assert rg == "resourceGroups"
        u = u._replace(path="/".join([empty, sub, "00000000-0000-0000-0000-000000000000", rg, "000000000000000", rest]))
        request.uri = u.geturl()
        return request
    except Exception:
        return request
