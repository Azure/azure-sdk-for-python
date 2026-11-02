# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# pylint: disable=protected-access

import logging
import posixpath
from typing import TYPE_CHECKING, Any, Dict, Optional, Set, Tuple
from urllib.parse import quote, unquote, urlsplit
from uuid import UUID

import yaml

from azure.ai.ml._azure_environments import _get_storage_endpoint_from_metadata
from azure.ai.ml._utils._storage_utils import AzureMLDatastorePathUri
from azure.ai.ml.entities._credentials import AadCredentialConfiguration, NoneCredentialConfiguration
from azure.ai.ml.entities._data.resolved_data_path import ResolvedDataPath
from azure.ai.ml.entities._datastore.azure_storage import AzureBlobDatastore, AzureDataLakeGen2Datastore
from azure.ai.ml.entities._datastore.datastore import Datastore
from azure.ai.ml.entities._datastore.one_lake import OneLakeDatastore
from azure.ai.ml.exceptions import ErrorTarget, ValidationErrorType, ValidationException
from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import BlobClient

if TYPE_CHECKING:
    from azure.ai.ml.operations._datastore_operations import DatastoreOperations

module_logger = logging.getLogger(__name__)
_MAX_DEFINITION_BYTES = 1024 * 1024
_MAX_DEPTH = 8


def _invalid(message: str) -> ValidationException:
    return ValidationException(
        message=message,
        no_personal_data_message=message,
        target=ErrorTarget.DATA,
        error_type=ValidationErrorType.INVALID_VALUE,
    )


def _is_guid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except ValueError:
        return False


def _relative_path(path: str) -> str:
    path = unquote(path)
    if path.startswith("/") or "\\" in path:
        raise _invalid("Data paths must be relative to the datastore root and use forward slashes.")
    normalized = posixpath.normpath(path)
    if normalized == ".." or normalized.startswith("../"):
        raise _invalid("Data path escapes the datastore root.")
    return "" if normalized == "." else normalized


def _storage_uri(store: Datastore, path: str) -> str:
    encoded_path = quote(path, safe="/*")
    if isinstance(store, OneLakeDatastore):
        endpoint = store.endpoint or "https://onelake.dfs.fabric.microsoft.com"
        parsed = urlsplit(endpoint if "://" in endpoint else "https://" + endpoint)
        if parsed.scheme != "https" or not parsed.hostname or parsed.path not in ("", "/"):
            raise _invalid("OneLake datastore endpoint must be an HTTPS host without credentials or a path.")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise _invalid("OneLake datastore endpoint must be an HTTPS host without credentials or a path.")
        workspace = store.one_lake_workspace_name
        artifact = store.artifact.name.strip("/")
        item, separator, subpath = artifact.partition("/")
        if not workspace or not item or any(character.isspace() for character in workspace):
            raise _invalid("OneLake requires a workspace and lakehouse; use GUIDs for workspaces with spaces.")
        if _is_guid(workspace) != _is_guid(item):
            raise _invalid("OneLake workspace and lakehouse must both be GUIDs or both be names.")
        if not _is_guid(item) and not item.lower().endswith(".lakehouse"):
            item += ".lakehouse"
        artifact_path = _relative_path(item + ("/" + subpath if separator else ""))
        base = "abfss://{}@{}/{}".format(quote(workspace, safe=""), parsed.netloc, quote(artifact_path, safe="/"))
    elif isinstance(store, (AzureBlobDatastore, AzureDataLakeGen2Datastore)):
        endpoint = store.endpoint or _get_storage_endpoint_from_metadata()
        if not endpoint:
            raise _invalid("Storage endpoint suffix is missing from datastore and cloud metadata.")
        if isinstance(store, AzureBlobDatastore):
            base = "https://{}.blob.{}/{}".format(store.account_name, endpoint, store.container_name)
        else:
            base = "abfss://{}@{}.dfs.{}".format(store.filesystem, store.account_name, endpoint)
    else:
        raise _invalid("Path resolution supports Azure Blob, ADLS Gen2, and OneLake datastores only.")
    return base.rstrip("/") + "/" + encoded_path


class _DataPathResolver:
    def __init__(self, datastore_operations: "DatastoreOperations", follow_mltable: bool):
        self._operations = datastore_operations
        self._follow_mltable = follow_mltable
        self._stores: Dict[str, Datastore] = {}

    def resolve(
        self,
        path: str,
        *,
        path_type: Optional[str] = None,
        ancestors: Optional[Set[Tuple[str, str]]] = None,
    ) -> ResolvedDataPath:
        if not isinstance(path, str) or not path:
            raise _invalid("Path must be a nonempty AML datastore URI.")
        if urlsplit(path).query or urlsplit(path).fragment:
            raise _invalid("AML datastore paths must not contain a query or fragment; encode literal characters.")
        uri = AzureMLDatastorePathUri(path)
        if uri.uri_type != "Datastore":
            raise _invalid("Only AML datastore path URIs are supported.")
        self._validate_scope(uri)
        relative = _relative_path(uri.path)
        key = (uri.datastore.casefold(), relative)
        ancestors = ancestors or set()
        if key in ancestors or len(ancestors) >= _MAX_DEPTH:
            raise _invalid("MLTable reference cycle or maximum nesting depth reached.")
        if key[0] not in self._stores:
            module_logger.info("Retrieving AML datastore metadata.")
            self._stores[key[0]] = self._operations.get(uri.datastore)
        store = self._stores[key[0]]
        result = ResolvedDataPath(uri=_storage_uri(store, relative), path_type=path_type)
        module_logger.info("Resolved datastore path using %s metadata.", type(store).__name__)

        # Discovery is intentionally limited to Blob-backed MLTable definitions.
        if not self._follow_mltable or path_type in ("file", "pattern") or not isinstance(store, AzureBlobDatastore):
            return result
        definition = self._read_definition(store, relative, folder=path_type == "folder" or uri.path.endswith("/"))
        if definition is None:
            return result
        entries = definition.get("paths")
        transformations = definition.get("transformations", [])
        if (
            not isinstance(entries, list)
            or not entries
            or not isinstance(transformations, list)
            or any(not isinstance(step, dict) for step in transformations)
        ):
            raise _invalid("MLTable requires a nonempty paths list and a list of transformation mappings.")
        result.transformations = transformations
        parent = posixpath.dirname(relative) if posixpath.basename(relative) == "MLTable" else relative
        for entry in entries:
            if not isinstance(entry, dict) or len(entry) != 1:
                raise _invalid("Each MLTable path must contain exactly one file, folder, or pattern.")
            kind, target = next(iter(entry.items()))
            if kind not in ("file", "folder", "pattern") or not isinstance(target, str) or not target:
                raise _invalid("MLTable paths must be nonempty file, folder, or pattern strings.")
            target_scheme = urlsplit(target).scheme
            if not target_scheme:
                target_relative = _relative_path(posixpath.join(quote(parent, safe="/"), target))
                target = "azureml://datastores/{}/paths/{}".format(uri.datastore, quote(target_relative, safe="/*"))
            elif target_scheme != "azureml":
                if target_scheme not in ("https", "abfss", "wasbs", "adl"):
                    raise _invalid("Unsupported storage URI scheme in MLTable source.")
                target_parts = urlsplit(target)
                if not target_parts.hostname:
                    raise _invalid("MLTable storage source must include a host.")
                if (
                    target_parts.query
                    or target_parts.fragment
                    or target_parts.password
                    or (target_parts.scheme == "https" and target_parts.username)
                ):
                    raise _invalid("MLTable source URIs must not contain credentials, queries, or fragments.")
                result.sources.append(ResolvedDataPath(uri=target, path_type=kind))
                continue
            result.sources.append(self.resolve(target, path_type=kind, ancestors=ancestors | {key}))
        return result

    def _validate_scope(self, uri: AzureMLDatastorePathUri) -> None:
        scope = self._operations._operation_scope
        if not scope.workspace_name or scope.registry_name:
            raise _invalid("Path resolution requires a workspace-scoped MLClient.")
        for supplied, expected in (
            (uri.subscription_id, scope.subscription_id),
            (uri.resource_group, scope.resource_group_name),
            (uri.workspace_name, scope.workspace_name),
        ):
            if supplied and supplied.casefold() != expected.casefold():
                raise _invalid("URI scope differs from MLClient. Use a client configured for that workspace.")

    def _read_definition(self, store: AzureBlobDatastore, path: str, *, folder: bool) -> Optional[Dict[str, Any]]:
        explicit = posixpath.basename(path) == "MLTable"
        read_credential = self._operations._credential
        if store.credentials and not isinstance(
            store.credentials, (NoneCredentialConfiguration, AadCredentialConfiguration)
        ):
            secrets = self._operations._list_secrets(name=store.name, expirable_secret=True)
            read_credential = getattr(secrets, "sas_token", None) or getattr(secrets, "key", None)
            if not read_credential:
                raise _invalid("Datastore does not provide a supported Blob credential.")
        account_url = "https://{}.blob.{}".format(
            store.account_name, store.endpoint or _get_storage_endpoint_from_metadata()
        )
        if not folder and not explicit and path:
            with BlobClient(account_url, store.container_name, path, credential=read_credential) as blob:
                try:
                    blob.get_blob_properties()
                    module_logger.info("Source is a Blob file; MLTable discovery is not required.")
                    return None
                except ResourceNotFoundError as error:
                    if getattr(error, "error_code", None) != "BlobNotFound":
                        raise
        definition_path = path if explicit else path.rstrip("/") + "/MLTable" if path else "MLTable"
        module_logger.info("Reading MLTable definition from Blob Storage.")
        with BlobClient(account_url, store.container_name, definition_path, credential=read_credential) as blob:
            try:
                content = blob.download_blob(offset=0, length=_MAX_DEFINITION_BYTES + 1).readall()
            except ResourceNotFoundError as error:
                if explicit or getattr(error, "error_code", None) != "BlobNotFound":
                    raise
                module_logger.info("No MLTable definition found; returning the Blob location.")
                return None
        if len(content) > _MAX_DEFINITION_BYTES:
            raise _invalid("MLTable definition exceeds the 1 MiB resolution limit.")
        try:
            definition = yaml.safe_load(content.decode("utf-8-sig"))
        except (yaml.YAMLError, UnicodeDecodeError) as error:
            raise _invalid("MLTable definition must contain valid UTF-8 YAML.") from error
        if not isinstance(definition, dict):
            raise _invalid("MLTable definition must be a YAML mapping.")
        return definition
