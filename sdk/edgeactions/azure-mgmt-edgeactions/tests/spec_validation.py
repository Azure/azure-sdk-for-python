# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------
"""Offline response validation against the generation's pinned OpenAPI specification."""

import json
import logging
import re
from functools import lru_cache
from pathlib import Path
from urllib.parse import parse_qs, urldefrag, urljoin, urlsplit
from urllib.request import urlopen

import yaml
from jsonschema import Draft4Validator, FormatChecker

PACKAGE = Path(__file__).resolve().parents[1]
SNAPSHOT = Path(__file__).with_name("response_spec.json")
API_VERSION = "2026-10-01"
LOGGER = logging.getLogger(__name__)

# The polling endpoint is not modeled in OpenAPI. ARM requires this envelope;
# other status fields are provider-specific, not final-resource properties.
# https://learn.microsoft.com/azure/azure-resource-manager/management/async-operations#azure-asyncoperation-request-and-response
ARM_STATUS_SCHEMA = {
    "type": "object",
    "required": ["status"],
    "properties": {"status": {"type": "string", "minLength": 1}},
}


class ResponseSpec:
    def __init__(self, snapshot):
        self.snapshot = snapshot

    def operation(self, method, url):
        path = urlsplit(url).path
        version = parse_qs(urlsplit(url).query).get("api-version")
        assert version is None or version == [self.snapshot["api_version"]], "Response spec API version mismatch"
        for route, methods in self.snapshot["paths"].items():
            pattern = "/".join("[^/]+" if part.startswith("{") else re.escape(part) for part in route.split("/"))
            if re.fullmatch(pattern, path, flags=re.IGNORECASE):
                return methods.get(method.lower())
        return None

    def _validate_schema(self, value, schema, description, *, allow_null_validation_status=False):
        schema = {**schema, "definitions": self.snapshot["definitions"]}
        skipped_null_status = False
        for error in Draft4Validator(schema, format_checker=FormatChecker()).iter_errors(value):
            if (
                allow_null_validation_status
                and tuple(error.absolute_path) == ("properties", "validationStatus")
                and error.instance is None
                and error.validator in ("enum", "type")
            ):
                skipped_null_status = True
                continue
            path = ".".join(str(part) for part in error.absolute_path) or "<body>"
            # Report the violated rule without echoing potentially sensitive response values.
            raise AssertionError(f"{description}: {path} violates OpenAPI {error.validator}") from None
        if skipped_null_status:
            LOGGER.warning(
                "Skipping only null validationStatus schema errors for the known version-creation service bug."
            )

    def validate_response(
        self, operation, status, body, headers, *, body_present=None, allow_known_null_validation_status=False
    ):
        assert operation is not None, "No matching operation in the pinned response spec"
        response = operation["responses"].get(str(status))
        name = operation["operationId"]
        assert response is not None, f"{name}: HTTP {status} is not a documented response"
        if body_present is None:
            body_present = body is not None
        if "schema" in response:
            assert body_present, f"{name}: HTTP {status} requires a response body"
            self._validate_schema(
                body,
                response["schema"],
                name,
                allow_null_validation_status=(
                    allow_known_null_validation_status and name == "EdgeActionVersions_Create" and status in (200, 201)
                ),
            )
        else:
            assert not body_present, f"{name}: HTTP {status} does not declare a response body"
        actual_headers = {key.lower(): value for key, value in headers.items()}
        for key, schema in response.get("headers", {}).items():
            if key.lower() not in actual_headers:
                continue
            value = actual_headers[key.lower()]
            if schema.get("type") == "integer":
                try:
                    value = int(value)
                except (ValueError, TypeError):
                    raise AssertionError(f"{name}: {key} must be an integer") from None
            self._validate_schema(value, schema, f"{name} header {key}")

    def validate_status_response(self, status, body):
        assert status == 200, f"Azure-AsyncOperation: expected HTTP 200, received HTTP {status}"
        self._validate_schema(body, ARM_STATUS_SCHEMA, "Azure-AsyncOperation")
        return body["status"]

    def validate_location(
        self,
        method,
        request_url,
        location,
        status,
        body,
        headers,
        *,
        body_present=None,
        allow_known_swap_default_response=False,
    ):
        # Validate the logical result declared by the initiating LRO, not an
        # unrelated GET contract selected by the URL the service happens to return.
        operation = self.operation(method, request_url)
        assert operation is not None, "No initiating operation in the pinned response spec"
        assert operation.get("x-ms-long-running-operation"), "Location validation requires a long-running operation"
        assert urlsplit(location).scheme == "https" and urlsplit(location).netloc, "Location must be an HTTPS URL"
        version = parse_qs(urlsplit(location).query).get("api-version")
        assert version is None or version == [
            self.snapshot["api_version"]
        ], "Location response spec API version mismatch"
        assert status != 202, f"{operation['operationId']}: Location did not return a completed response"
        if (
            allow_known_swap_default_response
            and operation["operationId"] == "EdgeActionVersions_SwapDefault"
            and status == 200
            and (body is not None if body_present is None else body_present)
        ):
            LOGGER.warning(
                "Skipping swapDefault Location response schema validation for the known HTTP-200-with-body service bug."
            )
            return
        self.validate_response(operation, status, body, headers, body_present=body_present)


@lru_cache
def response_spec():
    source = yaml.safe_load((PACKAGE / "tsp-location.yaml").read_text(encoding="utf-8"))
    snapshot = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    assert (
        snapshot["source"]["commit"] == source["commit"]
    ), "Response schemas are stale; run python tests\\spec_validation.py to refresh them"
    assert snapshot["source"]["repository"] == source["repo"]
    assert snapshot["source"]["url"] == (
        f"https://raw.githubusercontent.com/{source['repo']}/{source['commit']}/"
        f"{source['directory']}/stable/{API_VERSION}/openapi.json"
    ), "Response spec source URL mismatch"
    assert snapshot["api_version"] == API_VERSION, "Response spec API version mismatch"
    return ResponseSpec(snapshot)


def refresh_snapshot():
    """Extract response contracts and referenced definitions; never run during tests."""
    source = yaml.safe_load((PACKAGE / "tsp-location.yaml").read_text(encoding="utf-8"))
    commit = source["commit"]
    assert re.fullmatch(r"[0-9a-f]{40}", commit), "Pin the specification to a full commit SHA"
    root = f"https://raw.githubusercontent.com/{source['repo']}/{commit}/"
    spec_url = f"{root}{source['directory']}/stable/{API_VERSION}/openapi.json"
    documents = {}
    definitions = {}
    references = {}

    def document(url):
        assert url.startswith(root), "All schema references must stay within the pinned specification repository"
        if url not in documents:
            with urlopen(url, timeout=30) as response:
                documents[url] = json.load(response)
        return documents[url]

    def bundle(value, document_url):
        if isinstance(value, list):
            return [bundle(item, document_url) for item in value]
        if not isinstance(value, dict):
            return value
        result = {}
        for key, item in value.items():
            if key != "$ref":
                result[key] = bundle(item, document_url)
                continue
            url, pointer = urldefrag(urljoin(document_url, item))
            reference = (url, pointer)
            if reference not in references:
                name = f"{len(references)}_{pointer.rsplit('/', 1)[-1]}"
                references[reference] = name
                definition = document(url)
                for part in pointer.lstrip("/").split("/"):
                    definition = definition[part.replace("~1", "/").replace("~0", "~")]
                definitions[name] = bundle(definition, url)
            result[key] = "#/definitions/" + references[reference]
        return result

    spec = document(spec_url)
    assert spec["swagger"] == "2.0"
    assert spec["info"]["version"] == API_VERSION
    paths = {}
    for path, methods in spec["paths"].items():
        paths[path] = {}
        for method, operation in methods.items():
            if "operationId" not in operation:
                continue
            responses = {
                code: bundle(response, spec_url)
                for code, response in operation["responses"].items()
                if code.isdigit() and 200 <= int(code) < 300
            }
            paths[path][method] = {"operationId": operation["operationId"], "responses": responses}
            for key in ("x-ms-long-running-operation", "x-ms-long-running-operation-options"):
                if key in operation:
                    paths[path][method][key] = operation[key]
    snapshot = {
        "source": {"repository": source["repo"], "commit": commit, "url": spec_url},
        "api_version": API_VERSION,
        "paths": paths,
        "definitions": definitions,
    }
    Draft4Validator.check_schema({"definitions": definitions})
    SNAPSHOT.write_text(json.dumps(snapshot, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"Updated {SNAPSHOT.name} from {commit}; {len(definitions)} referenced definitions")


if __name__ == "__main__":
    refresh_snapshot()
