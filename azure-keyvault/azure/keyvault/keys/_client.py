import functools
from typing import Any, List, Mapping, Optional
import uuid

from ._models import (
    DeletedKey,
    DeletedKeyItem,
    DeletedKeyItemPaged,
    JsonWebKey,
    Key,
    KeyAttributes,
    KeyCreateParameters,
    KeyItem,
    KeyItemPaged,
    KeyUpdateParameters,
)
from azure.core.configuration import Configuration
from azure.core.exceptions import ClientRequestError
from azure.core.pipeline import Pipeline
from azure.core.pipeline.policies import (
    HTTPPolicy,
    UserAgentPolicy,
    HeadersPolicy,
    RetryPolicy,
    RedirectPolicy,
    ContentDecodePolicy,
)
from azure.core.pipeline.transport import (
    RequestsTransport,
    HttpRequest,
    HttpResponse,
    HttpTransport,
)
from msrest import Serializer, Deserializer


class BearerTokenCredentialPolicy(HTTPPolicy):
    def __init__(self, credentials):
        self._credentials = credentials

    def send(self, request, **kwargs):
        # type: (HttpRequest, Any) -> HttpResponse
        auth_header = "Bearer " + self._credentials.token["access_token"]
        request.http_request.headers["Authorization"] = auth_header

        return self.next.send(request, **kwargs)


class KeyClient:
    API_VERSION = "7.0"

    @staticmethod
    def create_config(**kwargs):
        # type: (Any) -> Configuration
        config = Configuration(**kwargs)
        config.user_agent = UserAgentPolicy("KeyClient", **kwargs)
        config.headers = None
        config.retry = RetryPolicy(**kwargs)
        config.redirect = RedirectPolicy(**kwargs)

        # TODO: these are requests-specific
        config.cert = config.timeout = None
        config.verify = True
        return config

    def __init__(self, vault_url, credentials, config=None, transport=None):
        # type: (str, Any, Configuration, HttpTransport) -> None
        self.vault_url = vault_url.strip("/")
        config = config or KeyClient.create_config()
        transport = RequestsTransport(config)
        policies = [
            config.user_agent,
            config.headers,
            BearerTokenCredentialPolicy(credentials),
            config.redirect,
            config.retry,
            config.logging,
        ]
        self._pipeline = Pipeline(transport, policies=policies)
        models = {
            "DeletedKey": DeletedKey,
            "DeletedKeyItem": DeletedKeyItem,
            "DeletedKeyItemPaged": DeletedKeyItemPaged,
            "JsonWebKey": JsonWebKey,
            "Key": Key,
            "KeyAttributes": KeyAttributes,
            "KeyCreateParameters": KeyCreateParameters,
            "KeyItem": KeyItem,
            "KeyItemPaged": KeyItemPaged,
        }
        self._deserialize = Deserializer(models)
        self._serialize = Serializer(models)

    def create_key(
        self,
        name,
        key_type,
        size=None,
        key_ops=None,
        attributes=None,
        tags=None,
        curve=None,
        **kwargs
    ):
        # type: (str, str, Optional[int], Optional[List[str]], Any, Any, Any, Any) -> Key
        url = "/".join([self.vault_url, "keys", name, "create"])
        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "x-ms-client-request-id": str(uuid.uuid1()),
        }
        create_params = KeyCreateParameters(
            kty=key_type,
            key_size=size,
            key_ops=key_ops,
            key_attributes=attributes,
            tags=tags,
            curve=curve,
            **kwargs
        )
        body = self._serialize.body(create_params, "KeyCreateParameters")
        request = HttpRequest("POST", url, headers, data=body)
        request.format_parameters({"api-version": self.API_VERSION})

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError(
                "Request failed with code {}: '{}'".format(
                    response.status_code, response.text()
                )
            )

        key = self._deserialize("Key", response)

        return key

    def delete_key(self, name, **kwargs):
        # type: (str, Any) -> DeletedKey
        url = "/".join([self.vault_url, "keys", name])

        request = HttpRequest("DELETE", url)
        request.format_parameters({"api-version": self.API_VERSION})
        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError(
                "Request failed with code {}: '{}'".format(
                    response.status_code, response.text()
                )
            )
        deleted_key = self._deserialize("DeletedKey", response)

        return deleted_key

    def get_key(self, name, version="", **kwargs):
        # type: (str, str, Any) -> Key
        """Gets the public part of a stored key.

        The get key operation is applicable to all key types. If the requested
        key is symmetric, then no key material is released in the response.
        This operation requires the keys/get permission.

        :param name: The name of the key to get.
        :type name: str
        :param version: Adding the version parameter retrieves a specific
         version of the key.
        :type version: str
        :return: Key
        :rtype: ~azure.keyvault.keys.Key
        """
        url = "/".join([self.vault_url, "keys", name, version])

        request = HttpRequest("GET", url)
        request.format_parameters({"api-version": self.API_VERSION})
        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError(
                "Request failed with code {}: '{}'".format(
                    response.status_code, response.text()
                )
            )
        key = self._deserialize("Key", response)

        return key

    def get_deleted_key(self, name, **kwargs):
        # type: (str, Any) -> DeletedKey

        url = "/".join([self.vault_url, "deletedkeys", name])

        request = HttpRequest("GET", url)
        request.format_parameters({"api-version": self.API_VERSION})
        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError(
                "Request failed with code {}: '{}'".format(
                    response.status_code, response.text()
                )
            )
        deleted_key = self._deserialize("DeletedKey", response)

        return deleted_key

    def get_all_deleted_keys(self, max_page_size=None, **kwargs):
        # type: (Optional[int], Any) -> DeletedKeyItemPaged
        url = "{}/{}".format(self.vault_url, "deletedkeys")
        paging = functools.partial(self._internal_paging, url, max_page_size)
        return DeletedKeyItemPaged(paging, self._deserialize.dependencies)

    def get_all_keys(self, max_page_size=None, **kwargs):
        # type: (Optional[int], Any) -> KeyItemPaged
        url = "{}/{}".format(self.vault_url, "keys")
        paging = functools.partial(self._internal_paging, url, max_page_size)
        return KeyItemPaged(paging, self._deserialize.dependencies)

    def get_key_versions(self, name, max_page_size=None, **kwargs):
        # type: (Optional[int], Any) -> KeyItemPaged
        url = "/".join([self.vault_url, "keys", name, "versions"])
        paging = functools.partial(self._internal_paging, url, max_page_size)
        return KeyItemPaged(paging, self._deserialize.dependencies)

    def purge_deleted_key(self, name, **kwargs):
        # type: (str, Any) -> None
        url = "/".join([self.vault_url, "deletedkeys", name])

        request = HttpRequest("DELETE", url)
        request.format_parameters({"api-version": self.API_VERSION})

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 204:
            raise ClientRequestError(
                "Request failed with code {}: '{}'".format(
                    response.status_code, response.text()
                )
            )

        return

    def recover_deleted_key(self, name, **kwargs):
        # type: (str, Any) -> Key
        url = "/".join([self.vault_url, "deletedkeys", name, "recover"])

        request = HttpRequest("POST", url)
        request.format_parameters({"api-version": self.API_VERSION})

        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError(
                "Request failed with code {}: '{}'".format(
                    response.status_code, response.text()
                )
            )

        key = self._deserialize("Key", response)

        return key

    def update_key(
        self, name, version, key_ops=None, attributes=None, tags=None, **kwargs
    ):
        # type: (str, str, Optional[List[str]], Mapping[str, str], Mapping[str, str], Any) -> Key
        url = "/".join([self.vault_url, "keys", name, version])

        headers = {
            "Content-Type": "application/json; charset=utf-8",
            "x-ms-client-request-id": str(uuid.uuid1()),
        }

        update_params = KeyUpdateParameters(
            key_ops=key_ops, key_attributes=attributes, tags=tags
        )
        body = self._serialize.body(update_params, "KeyUpdateParameters")
        request = HttpRequest("PATCH", url, headers=headers, data=body)
        request.format_parameters({"api-version": self.API_VERSION})
        response = self._pipeline.run(request, **kwargs).http_response
        if response.status_code != 200:
            raise ClientRequestError(
                "Request failed with code {}: '{}'".format(
                    response.status_code, response.text()
                )
            )
        key = self._deserialize("Key", response)

        return key

    def _internal_paging(self, url, max_page_size, next_link=None, raw=False, **kwargs):
        # type: (str, int, Optional[str], Optional[bool], Any) -> HttpResponse
        if next_link:
            url = next_link
            query_parameters = {}
        else:
            query_parameters = {"api-version": self.API_VERSION}
            if max_page_size is not None:
                query_parameters["maxresults"] = str(max_page_size)

        headers = {"x-ms-client-request-id": str(uuid.uuid1())}

        request = HttpRequest("GET", url, headers)
        request.format_parameters(query_parameters)

        response = self._pipeline.run(request, **kwargs).http_response

        if response.status_code != 200:
            raise ClientRequestError(
                "Request failed with code {}: '{}'".format(
                    response.status_code, response.text()
                )
            )

        return response

    # TODO:
    # def import_key(self, name, key, hsm=None, attributes=None, tags=None, **kwargs):
    #     pass

    # def backup_key(self, name, **kwargs):
    #     pass

    # def restore_key(self, key_bundle_backup, **kwargs):
    #     pass

    # def wrap_key(self, name, version, algorithm, value, **kwargs):
    #     pass

    # def unwrap_key(self, name, version, algorithm, value, **kwargs):
    #     pass
