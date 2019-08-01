# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from datetime import datetime

try:
    from typing import TYPE_CHECKING
except ImportError:
    TYPE_CHECKING = False

if TYPE_CHECKING:
    from typing import Any, Dict, Generator, Mapping, Optional

from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError
from azure.core.tracing.decorator import distributed_trace

from ._shared import KeyVaultClientBase
from ._models import Secret, DeletedSecret, SecretAttributes


class SecretClient(KeyVaultClientBase):
    """SecretClient is a high-level interface for managing a vault's secrets.

    Example:
        .. literalinclude:: ../tests/test_samples_secrets.py
            :start-after: [START create_secret_client]
            :end-before: [END create_secret_client]
            :language: python
            :caption: Creates a new instance of the Secret client
            :dedent: 4
    """

    # pylint:disable=protected-access

    @distributed_trace
    def get_secret(self, name, version=None, **kwargs):
        # type: (str, str, Mapping[str, Any]) -> Secret
        """Get a specified secret from the vault.

        The GET operation is applicable to any secret stored in Azure Key
        Vault. This operation requires the secrets/get permission.

        :param str name: The name of the secret.
        :param str version: The version of the secret. If version is None or the empty string, the latest version of
            the secret is returned
        :returns: An instance of Secret
        :rtype: ~azure.keyvault.secrets._models.Secret
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the client failed to retrieve the secret

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START get_secret]
                :end-before: [END get_secret]
                :language: python
                :caption: Get secret from the key vault
                :dedent: 8
        """
        bundle = self._client.get_secret(
            self._vault_url, name, version or "", error_map={404: ResourceNotFoundError}, **kwargs
        )
        return Secret._from_secret_bundle(bundle)

    @distributed_trace
    def set_secret(
        self, name, value, content_type=None, enabled=None, not_before=None, expires=None, tags=None, **kwargs
    ):
        # type: (str, str, Optional[str], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> Secret
        """Sets a secret in the vault.

        The SET operation adds a secret to the Azure Key Vault. If the named
        secret already exists, Azure Key Vault creates a new version of that
        secret. This operation requires the secrets/set permission.

        :param str name: The name of the secret
        :param str value: The value of the secret
        :param str content_type: Type of the secret value such as a password
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param not_before: Not before date of the secret in UTC
        :type not_before: datetime.datetime
        :param expires: Expiry date of the secret  in UTC.
        :type expires: datetime.datetime
        :param tags: Application specific metadata in the form of key-value pairs.
        :type tags: dict(str, str)
        :returns: The created secret
        :rtype: ~azure.keyvault.secrets._models.Secret

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START set_secret]
                :end-before: [END set_secret]
                :language: python
                :caption: Set a secret in the key vault
                :dedent: 8

        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.SecretAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None
        bundle = self._client.set_secret(
            self.vault_url, name, value, secret_attributes=attributes, content_type=content_type, tags=tags, **kwargs
        )
        return Secret._from_secret_bundle(bundle)

    @distributed_trace
    def update_secret(
        self, name, version=None, content_type=None, enabled=None, not_before=None, expires=None, tags=None, **kwargs
    ):
        # type: (str, Optional[str], Optional[str], Optional[bool], Optional[datetime], Optional[datetime], Optional[Dict[str, str]], Mapping[str, Any]) -> SecretAttributes
        """Updates the attributes associated with a specified secret in the key vault.

        The UPDATE operation changes specified attributes of an existing stored secret.
        Attributes that are not specified in the request are left unchanged. The value
        of a secret itself cannot be changed. This operation requires the secrets/set permission.

        :param str name: The name of the secret
        :param str version: The version of the secret.
        :param str content_type: Type of the secret value such as a password
        :param enabled: Determines whether the object is enabled.
        :type enabled: bool
        :param not_before: Not before date of the secret  in UTC
        :type not_before: datetime.datetime
        :param expires: Expiry date  of the secret in UTC.
        :type expires: datetime.datetime
        :param tags: Application specific metadata in the form of key-value pairs.
        :type tags: dict(str, str)
        :returns: The created secret
        :rtype: ~azure.keyvault.secrets._models.SecretAttributes
        :raises: ~azure.core.exceptions.ResourceNotFoundError if the client failed to create the secret

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START update_secret]
                :end-before: [END update_secret]
                :language: python
                :caption: Updates the attributes associated with a specified secret in the key vault
                :dedent: 8

        """
        if enabled is not None or not_before is not None or expires is not None:
            attributes = self._client.models.SecretAttributes(enabled=enabled, not_before=not_before, expires=expires)
        else:
            attributes = None
        bundle = self._client.update_secret(
            self.vault_url,
            name,
            secret_version=version or "",
            content_type=content_type,
            tags=tags,
            secret_attributes=attributes,
            error_map={404: ResourceNotFoundError},
            **kwargs
        )
        return SecretAttributes._from_secret_bundle(bundle)  # pylint: disable=protected-access

    @distributed_trace
    def list_secrets(self, **kwargs):
        # type: (Mapping[str, Any]) -> Generator[SecretAttributes]
        """List secrets in the vault.

        The Get Secrets operation is applicable to the entire vault. However,
        only the latest secret identifier and its attributes are provided in the
        response. No secret values are returned and individual secret versions are
        not listed in the response.  This operation requires the secrets/list permission.

        :returns: An iterator like instance of Secrets
        :rtype:
         Generator[~azure.keyvault.secrets._models.SecretAttributes]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START list_secrets]
                :end-before: [END list_secrets]
                :language: python
                :caption: Lists all the secrets in the vault
                :dedent: 8

        """
        max_page_size = kwargs.get("max_page_size", None)
        return self._client.get_secrets(
            self._vault_url,
            maxresults=max_page_size,
            cls=lambda objs: [DeletedSecret._from_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_secret_versions(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> Generator[SecretAttributes]
        """List all versions of the specified secret.

        The full secret identifier and attributes are provided in the response.
        No values are returned for the secrets. This operations requires the
        secrets/list permission.

        :param str name: The name of the secret.
        :returns: An iterator like instance of Secret
        :rtype:
         Generator[~azure.keyvault.secrets._models.SecretAttributes]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START list_secret_versions]
                :end-before: [END list_secret_versions]
                :language: python
                :caption: List all versions of the specified secret
                :dedent: 8

        """
        max_page_size = kwargs.get("max_page_size", None)
        return self._client.get_secret_versions(
            self._vault_url,
            name,
            maxresults=max_page_size,
            cls=lambda objs: [DeletedSecret._from_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def backup_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> bytes
        """Backs up the specified secret.

        Requests that a backup of the specified secret be downloaded to the
        client. All versions of the secret will be downloaded. This operation
        requires the secrets/backup permission.

        :param str name: The name of the secret.
        :returns: The raw bytes of the secret backup.
        :rtype: bytes
        :raises: ~azure.core.exceptions.ResourceNotFoundError, if client failed to back up the secret

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START backup_secret]
                :end-before: [END backup_secret]
                :language: python
                :caption: Backs up the specified secret
                :dedent: 8

        """
        backup_result = self._client.backup_secret(
            self.vault_url, name, error_map={404: ResourceNotFoundError}, **kwargs
        )
        return backup_result.value

    @distributed_trace
    def restore_secret(self, backup, **kwargs):
        # type: (bytes, Mapping[str, Any]) -> SecretAttributes
        """Restore a backed up secret to the vault.

        Restores a backed up secret, and all its versions, to a vault. This
        operation requires the secrets/restore permission.

        :param bytes backup: The raw bytes of the secret backup
        :returns: The restored secret
        :rtype: ~azure.keyvault.secrets._models.SecretAttributes
        :raises: ~azure.core.exceptions.ResourceExistsError, if client failed to restore the secret

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START restore_secret]
                :end-before: [END restore_secret]
                :language: python
                :caption: Restores a backed up secret to the vault
                :dedent: 8

        """
        bundle = self._client.restore_secret(self.vault_url, backup, error_map={409: ResourceExistsError}, **kwargs)
        return SecretAttributes._from_secret_bundle(bundle)

    @distributed_trace
    def delete_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> DeletedSecret
        """Deletes a secret from the vault.

        The DELETE operation applies to any secret stored in Azure Key Vault.
        DELETE cannot be applied to an individual version of a secret. This
        operation requires the secrets/delete permission.

        :param str name: The name of the secret
        :return: The deleted secret.
        :rtype: ~azure.keyvault.secrets._models.DeletedSecret
        :raises: ~azure.core.exceptions.ResourceNotFoundError, if client failed to delete the secret

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START delete_secret]
                :end-before: [END delete_secret]
                :language: python
                :caption: Deletes a secret
                :dedent: 8

        """
        bundle = self._client.delete_secret(self.vault_url, name, error_map={404: ResourceNotFoundError}, **kwargs)
        return DeletedSecret._from_deleted_secret_bundle(bundle)

    @distributed_trace
    def get_deleted_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> DeletedSecret
        """Gets the specified deleted secret.

        The Get Deleted Secret operation returns the specified deleted secret
        along with its attributes. This operation requires the secrets/get permission.

        :param str name: The name of the secret
        :return: The deleted secret.
        :rtype: ~azure.keyvault.secrets._models.DeletedSecret
        :raises: ~azure.core.exceptions.ResourceNotFoundError, if client failed to get the deleted secret

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START get_deleted_secret]
                :end-before: [END get_deleted_secret]
                :language: python
                :caption: Gets the deleted secret
                :dedent: 8

        """
        bundle = self._client.get_deleted_secret(self.vault_url, name, error_map={404: ResourceNotFoundError}, **kwargs)
        return DeletedSecret._from_deleted_secret_bundle(bundle)

    @distributed_trace
    def list_deleted_secrets(self, **kwargs):
        # type: (Mapping[str, Any]) -> Generator[DeletedSecret]
        """Lists deleted secrets of the vault.

        The Get Deleted Secrets operation returns the secrets that have
        been deleted for a vault enabled for soft-delete. This
        operation requires the secrets/list permission.

        :returns: An iterator like instance of DeletedSecrets
        :rtype:
         Generator[~azure.keyvault.secrets._models.DeletedSecret]

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START list_deleted_secrets]
                :end-before: [END list_deleted_secrets]
                :language: python
                :caption: Lists the deleted secrets of the vault
                :dedent: 8

        """
        max_page_size = kwargs.get("max_page_size", None)
        return self._client.get_deleted_secrets(
            self._vault_url,
            maxresults=max_page_size,
            cls=lambda objs: [DeletedSecret._from_deleted_secret_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def purge_deleted_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> None
        """Permanently deletes the specified secret.

        The purge deleted secret operation removes the secret permanently, without the
        possibility of recovery. This operation can only be enabled on a soft-delete enabled
        vault. This operation requires the secrets/purge permission.

        :param str name: The name of the secret
        :returns: None
        :raises: ~azure.core.exceptions.HttpResponseError, if client failed to return the purged secret

        Example:
            .. code-block:: python

                # if the vault has soft-delete enabled, purge permanently deletes the secret
                # (with soft-delete disabled, delete itself is permanent)
                secret_client.purge_deleted_secret("secret-name")

        """
        self._client.purge_deleted_secret(self.vault_url, name, **kwargs)

    @distributed_trace
    def recover_deleted_secret(self, name, **kwargs):
        # type: (str, Mapping[str, Any]) -> SecretAttributes
        """Recovers the deleted secret to the latest version.

        Recovers the deleted secret in the specified vault.
        This operation can only be performed on a soft-delete enabled
        vault. This operation requires the secrets/recover permission.

        :param str name: The name of the secret
        :returns: The recovered deleted secret
        :rtype: ~azure.keyvault.secrets._models.SecretAttributes
        :raises: ~azure.core.exceptions.HttpResponseError, if client failed to recover the deleted secret

        Example:
            .. literalinclude:: ../tests/test_samples_secrets.py
                :start-after: [START recover_deleted_secret]
                :end-before: [END recover_deleted_secret]
                :language: python
                :caption: Restores a backed up secret to the vault
                :dedent: 8

        """
        bundle = self._client.recover_deleted_secret(self.vault_url, name, **kwargs)
        return SecretAttributes._from_secret_bundle(bundle)
