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

    def __init__(
        self,
        cfg: AzureArtifactsFeedConfig,
        base_url: str = "https://feeds.dev.azure.com",
        pkgs_base_url: str = "https://pkgs.dev.azure.com",
    ):
        self._cfg = cfg
        self._base_url = base_url.rstrip("/")
        self._pkgs_base_url = pkgs_base_url.rstrip("/")
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
                logging.warning(
                    "Invalid version %r for package %s (feed=%s)",
                    raw,
                    package_name,
                    self._cfg.feed,
                )

        out.sort()
        return out

    def _head_ok(self, url: str) -> bool:
        """Return True if a HEAD request to *url* resolves successfully (2xx)."""
        headers = self._auth_header()
        try:
            r = self._http.request("HEAD", url, headers=headers, redirect=True)
        except Exception as ex:  # pylint: disable=broad-except
            logging.debug("HEAD request failed for %s: %s", url, ex)
            return False
        return 200 <= r.status < 300

    def _sdist_filename_candidates(self, package_name: str, version: str) -> List[str]:
        """Candidate sdist filenames for *package_name*==*version*.

        Sdist filenames vary by build tooling: legacy hyphenated form
        (``azure-core-1.0.0.tar.gz``) vs PEP 625 underscore form
        (``azure_core-1.0.0.tar.gz``), and ``.tar.gz`` vs ``.zip``.
        """
        hyphen = re.sub(r"[-_.]+", "-", package_name)
        underscore = re.sub(r"[-_.]+", "_", package_name)
        # Preserve insertion order while de-duplicating (e.g. single-token names).
        stems = list(dict.fromkeys([hyphen, underscore, package_name]))
        return [f"{stem}-{version}{ext}" for stem in stems for ext in (".tar.gz", ".zip")]

    def get_download_uri(self, package_name: str, version: str) -> Optional[str]:
        """Resolve the sdist download URI for *package_name*==*version*.

        Builds the Azure Artifacts PyPI download URL and probes candidate sdist
        filenames with HEAD requests, returning the first that resolves.
        Requesting this URL triggers an upstream pull, so versions that are not
        yet present in the feed's stale PEP 503 Simple index are still served.
        """
        download_base = (
            f"{self._pkgs_base_url}/{self._path_prefix()}"
            f"/_packaging/{self._cfg.feed}/pypi/download/{package_name}/{version}"
        )
        for filename in self._sdist_filename_candidates(package_name, version):
            url = f"{download_base}/{filename}"
            if self._head_ok(url):
                logging.info("Resolved download URI for %s==%s: %s", package_name, version, url)
                return url
        logging.warning("Could not resolve a download URI for %s==%s", package_name, version)
        return None

    def get_latest_download_uri(
        self, package_name: str, allow_prerelease: bool = False
    ) -> "tuple[Optional[str], Optional[str]]":
        """Return ``(version_str, sdist_download_uri)`` for the latest version.

        Version discovery uses the Feed REST API, which reflects the feed's
        current view (the PEP 503 Simple index only serves stale, locally-cached
        versions). The download URI is resolved against ``pkgs.dev.azure.com``.
        """
        versions = self.get_ordered_versions(package_name)
        if not versions:
            return None, None

        if allow_prerelease:
            latest = versions[-1]
        else:
            stable = [v for v in versions if not v.is_prerelease]
            latest = stable[-1] if stable else versions[-1]

        version_str = str(latest)
        return version_str, self.get_download_uri(package_name, version_str)
