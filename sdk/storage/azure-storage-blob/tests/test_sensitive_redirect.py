from azure.core.pipeline import PipelineRequest, PipelineContext
from azure.core.rest import HttpRequest
from azure.storage.blob._shared.policies import StorageSensitiveHeaderCleanupPolicy


def make_request(url, headers=None):
    http_request = HttpRequest("GET", url, headers=headers or {})
    context = PipelineContext(None)
    return PipelineRequest(http_request, context)


class TestStorageSensitiveHeaderCleanup:
    SENSITIVE_HEADERS = {
        "Authorization": "Bearer token",
        "x-ms-authorization-auxiliary": "Bearer aux-token",
        "x-ms-copy-source": "https://acct.blob.core.windows.net/c/src?sig=SECRET",
        "x-ms-copy-source-authorization": "Bearer copy-token",
        "x-ms-rename-source": "/c/old",
    }

    def test_storage_sensitive_cleanup_on_redirect(self):
        headers = dict(self.SENSITIVE_HEADERS)
        headers["x-ms-meta-keep"] = "ok"
        request = make_request(
            "https://acct.blob.core.windows.net/c/b?comp=block&sv=2026-04-06&sig=SECRET",
            headers=headers,
        )
        request.context["insecure_domain_change"] = True

        StorageSensitiveHeaderCleanupPolicy().on_request(request)

        assert "sig=" not in request.http_request.url
        assert "sv=2026-04-06" in request.http_request.url
        assert "comp=block" in request.http_request.url

        for header in self.SENSITIVE_HEADERS:
            assert header not in request.http_request.headers

        assert request.http_request.headers["x-ms-meta-keep"] == "ok"

    def test_no_cleanup_when_no_redirect(self):
        request = make_request(
            "https://acct.blob.core.windows.net/c/b?sig=SECRET",
            headers=dict(self.SENSITIVE_HEADERS),
        )
        StorageSensitiveHeaderCleanupPolicy().on_request(request)

        assert "sig=SECRET" in request.http_request.url
        for header, value in self.SENSITIVE_HEADERS.items():
            assert request.http_request.headers[header] == value

    def test_no_cleanup_when_disabled(self):
        request = make_request(
            "https://acct.blob.core.windows.net/c/b?sig=SECRET",
            headers=dict(self.SENSITIVE_HEADERS),
        )
        request.context["insecure_domain_change"] = True

        StorageSensitiveHeaderCleanupPolicy(disable_redirect_cleanup=True).on_request(request)

        assert "sig=SECRET" in request.http_request.url
        for header, value in self.SENSITIVE_HEADERS.items():
            assert request.http_request.headers[header] == value
