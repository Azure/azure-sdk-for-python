# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import base64
import hashlib
import re
import time
import json
from typing import List, Dict, IO, Optional
from io import BytesIO
from urllib.parse import urlparse

from azure.core.exceptions import ServiceRequestError
from azure.core.pipeline import PipelineRequest
from ._generated.models import OCIManifest

BEARER = "Bearer"
AUTHENTICATION_CHALLENGE_PARAMS_PATTERN = re.compile('(?:(\\w+)="([^""]*)")+')
SUPPORTED_API_VERSIONS = [
    "2019-08-15-preview",
    "2021-07-01"
]
OCI_MANIFEST_MEDIA_TYPE = "application/vnd.oci.image.manifest.v1+json"
DEFAULT_CHUNK_SIZE = 4 * 1024 * 1024 # 4MB

# Public cloud audience
AZURE_RESOURCE_MANAGER_PUBLIC_CLOUD = "https://management.azure.com"
# The default audience used for all clouds when audience is not set
DEFAULT_AUDIENCE = "https://containerregistry.azure.net"


def _is_tag(tag_or_digest: str) -> bool:
    tag = tag_or_digest.split(":")
    return not (len(tag) == 2 and tag[0].startswith("sha"))

def _clean(matches: List[str]) -> None:
    """This method removes empty strings and commas from the regex matching of the Challenge header"""
    while True:
        try:
            matches.remove("")
        except ValueError:
            break

    while True:
        try:
            matches.remove(",")
        except ValueError:
            return

def _parse_challenge(header: str) -> Dict[str, str]:
    """Parse challenge header into service and scope"""
    ret: Dict[str, str] = {}
    if header.startswith(BEARER):
        challenge_params = header[len(BEARER) + 1 :]

        matches = re.split(AUTHENTICATION_CHALLENGE_PARAMS_PATTERN, challenge_params)
        _clean(matches)
        for i in range(0, len(matches), 2):
            ret[matches[i]] = matches[i + 1]

    return ret

def _parse_next_link(link_string: str) -> Optional[str]:
    """Parses the next link in the list operations response URL

    Per the Docker v2 HTTP API spec, the Link header is an RFC5988
    compliant rel='next' with URL to next result set, if available.
    See: https://docs.docker.com/registry/spec/api/

    The URI reference can be obtained from link-value as follows:
    Link       = "Link" ":" #link-value
    link-value = "<" URI-Reference ">" * (";" link-param )
    See: https://tools.ietf.org/html/rfc5988#section-5
    """
    if not link_string:
        return None
    return link_string[1 : link_string.find(">")]

def _enforce_https(request: PipelineRequest) -> None:
    """Raise ServiceRequestError if the request URL is non-HTTPS and the sender did not specify enforce_https=False"""

    # move 'enforce_https' from options to context so it persists
    # across retries but isn't passed to a transport implementation
    option = request.context.options.pop("enforce_https", None)

    # True is the default setting; we needn't preserve an explicit opt in to the default behavior
    if option is False:
        request.context["enforce_https"] = option

    enforce_https = request.context.get("enforce_https", True)
    if enforce_https and not request.http_request.url.lower().startswith("https"):
        raise ServiceRequestError(
            "Bearer token authentication is not permitted for non-TLS protected (non-https) URLs."
        )

def _host_only(url: str) -> str:
    return urlparse(url).netloc

def _strip_alg(digest):
    if len(digest.split(":")) == 2:
        return digest.split(":")[1]
    return digest

def _parse_exp_time(raw_token):
    # type: (str) -> float
    raw_token_list = raw_token.split(".")
    if len(raw_token_list) > 2:
        value = raw_token_list[1]
        padding = len(value) % 4
        if padding > 0:
            value += "=" * padding
        byte_value = base64.b64decode(value).decode("utf-8")
        web_token = json.loads(byte_value)
        return web_token.get("exp", time.time())

    return time.time()

def _serialize_manifest(manifest: OCIManifest) -> IO:
    data = json.dumps(manifest.serialize()).encode('utf-8')
    return BytesIO(data)

def _deserialize_manifest(data: IO) -> OCIManifest:
    data.seek(0)
    value = data.read()
    data.seek(0)
    return OCIManifest.deserialize(json.loads(value.decode()))

def _compute_digest(data: IO) -> str:
    data.seek(0)
    value = data.read()
    data.seek(0)
    return "sha256:" + hashlib.sha256(value).hexdigest()

def _validate_digest(data: IO, digest: str) -> bool:
    data_digest = _compute_digest(data)
    return data_digest == digest
