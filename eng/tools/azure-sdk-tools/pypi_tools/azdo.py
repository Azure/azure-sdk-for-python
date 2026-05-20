import base64
import json
import logging
import os
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse

from packaging.version import Version, InvalidVersion, parse
from urllib3 import PoolManager, Retry


def pep503_normalize(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


@dataclass(frozen=True)
class AzureArtifactsFeedConfig:
    organization: str
    project: Optional[str]  # None if the feed is organization-scoped
    feed: str  # feed name or GUID
    api_version: str = "7.1"

    bearer_token: Optional[str] = None
    pat: Optional[str] = None


# Pattern: https://pkgs.dev.azure.com/{org}/{project}/_packaging/{feed}/pypi/simple/
# or org-scoped: https://pkgs.dev.azure.com/{org}/_packaging/{feed}/pypi/simple/
_AZDO_FEED_RE = re.compile(
    r"/(?P<org>[^/]+)/(?:(?P<project>[^/_][^/]*)/)?" r"_packaging/(?P<feed>[^/]+)/pypi/simple/?$"
)


def parse_pip_index_url(url: str) -> Optional[AzureArtifactsFeedConfig]:
    """If *url* points to an Azure Artifacts PyPI feed, return a config; else None."""
    parsed = urlparse(url)
    if "pkgs.dev.azure.com" not in parsed.hostname:
        return None

    m = _AZDO_FEED_RE.search(parsed.path)
    if not m:
        return None

    # Embedded credentials from PipAuthenticate@1
    pat = None
    if parsed.password:
        pat = parsed.password

    return AzureArtifactsFeedConfig(
        organization=m.group("org"),
        project=m.group("project"),
        feed=m.group("feed"),
        pat=pat or os.environ.get("AZDO_PAT"),
    )


class AzureArtifactsClient:
    """
    Minimal client to list package versions from an Azure Artifacts feed
    via Azure DevOps Artifacts REST API.
    """

    def __init__(self, cfg: AzureArtifactsFeedConfig, base_url: str = "https://feeds.dev.azure.com"):
        self._cfg = cfg
        self._base_url = base_url.rstrip("/")
        self._http = PoolManager(
            retries=Retry(total=3, raise_on_status=True),
            ca_certs=os.getenv("REQUESTS_CA_BUNDLE", None),
        )

    def _auth_header(self) -> Dict[str, str]:
        if self._cfg.bearer_token:
            return {"Authorization": f"Bearer {self._cfg.bearer_token}"}

        if self._cfg.pat:
            # Azure DevOps PATs can be used via HTTP Basic by base64-encoding ":<PAT>".
            token = base64.b64encode(f":{self._cfg.pat}".encode("utf-8")).decode("ascii")
            return {"Authorization": f"Basic {token}"}

        return {}

    def _path_prefix(self) -> str:
        # If project-scoped feed: /{org}/{project}/...
        # If org-scoped feed: /{org}/...
        if self._cfg.project:
            return f"{self._cfg.organization}/{self._cfg.project}"
        return self._cfg.organization

    def _get_json(self, url: str, params: Dict[str, Any]) -> Any:
        headers = {"Accept": "application/json", **self._auth_header()}
        r = self._http.request("GET", url, fields=params, headers=headers)
        return json.loads(r.data.decode("utf-8"))

    def list_feeds(self) -> List[Dict[str, Any]]:
        url = f"{self._base_url}/{self._path_prefix()}/_apis/packaging/feeds"
        data = self._get_json(url, {"api-version": self._cfg.api_version})
        # Many Azure DevOps APIs return {"count": n, "value": [...]}; be tolerant.
        return data["value"] if isinstance(data, dict) and "value" in data else data

    def resolve_feed_id(self) -> str:
        feed = self._cfg.feed
        if re.fullmatch(r"[0-9a-fA-F-]{36}", feed):
            return feed

        for f in self.list_feeds():
            if f.get("name") == feed:
                return f["id"]

        raise KeyError(f"Feed not found: {feed!r}")

    def get_package_record(self, package_name: str, include_deleted: bool = False) -> Dict[str, Any]:
        feed_id = self.resolve_feed_id()
        url = f"{self._base_url}/{self._path_prefix()}/_apis/packaging/Feeds/{feed_id}/packages"

        params = {
            "api-version": self._cfg.api_version,
            "protocolType": "pypi",
            "packageNameQuery": package_name,
            "includeAllVersions": "true",
            "includeDeleted": "true" if include_deleted else "false",
        }

        data = self._get_json(url, params)
        packages = data["value"] if isinstance(data, dict) and "value" in data else data

        # packageNameQuery is "contains string", so choose best match.
        target = pep503_normalize(package_name)
        for pkg in packages:
            if pep503_normalize(pkg.get("normalizedName", pkg.get("name", ""))) == target:
                return pkg
        for pkg in packages:
            if pep503_normalize(pkg.get("name", "")) == target:
                return pkg

        raise KeyError(f"Package not found in feed: {package_name!r}")

    def get_ordered_versions(self, package_name: str, include_deleted: bool = False) -> List[Version]:
        pkg = self.get_package_record(package_name, include_deleted=include_deleted)

        out: List[Version] = []
        for v in pkg.get("versions", []):
            if (not include_deleted) and v.get("isDeleted", False):
                continue

            raw = v.get("version")
            if not raw:
                continue

            try:
                out.append(parse(raw))
            except InvalidVersion:
                logging.warning("Invalid version %r for package %s (feed=%s)", raw, package_name, self._cfg.feed)

        out.sort()
        return out
