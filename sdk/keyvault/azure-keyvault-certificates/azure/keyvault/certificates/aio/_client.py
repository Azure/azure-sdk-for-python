# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint:disable=too-many-lines,too-many-public-methods
import base64
from typing import Any, AsyncIterable, Optional, Iterable, List, Dict, Union
from functools import partial

from azure.core.polling import async_poller
from azure.core.tracing.decorator import distributed_trace
from azure.core.tracing.decorator_async import distributed_trace_async

from .. import (
    KeyVaultCertificate,
    CertificateOperation,
    CertificatePolicy,
    DeletedCertificate,
    CertificateProperties,
    CertificateContact,
    CertificateIssuer,
    IssuerProperties,
)
from ._polling_async import CreateCertificatePollerAsync
from .._shared import AsyncKeyVaultClientBase
from .._shared._polling_async import AsyncDeleteRecoverPollingMethod
from .._shared.exceptions import error_map as _error_map


class CertificateClient(AsyncKeyVaultClientBase):
    """A high-level asynchronous interface for managing a vault's certificates.

    :param str vault_url: URL of the vault the client will access
    :param credential: An object which can provide an access token for the vault, such as a credential from
        :mod:`azure.identity.aio`
    :keyword api_version: version of the Key Vault API to use. Defaults to the most recent.
    :paramtype api_version: ~azure.keyvault.certificates.ApiVersion
    :keyword transport: transport to use. Defaults to
     :class:`~azure.core.pipeline.transport.AioHttpTransport`.
    :paramtype transport: ~azure.core.pipeline.transport.AsyncHttpTransport

    Example:
        .. literalinclude:: ../tests/test_examples_certificates_async.py
            :start-after: [START create_certificate_client]
            :end-before: [END create_certificate_client]
            :language: python
            :dedent: 4
            :caption: Creates a new instance of the Certificate client
    """

    # pylint:disable=protected-access
    @distributed_trace_async
    async def create_certificate(
        self, certificate_name: str, policy: CertificatePolicy, **kwargs: "Any"
    ) -> Union[KeyVaultCertificate, CertificateOperation]:
        """Creates a new certificate.

        If this is the first version, the certificate resource is created. This
        operation requires the certificates/create permission. The poller requires the
        certificates/get permission, otherwise raises
        an :class:`~azure.core.exceptions.HttpResponseError`

        :param str certificate_name: The name of the certificate.
        :param policy: The management policy for the certificate.
        :type policy:
         ~azure.keyvault.certificates.CertificatePolicy
        :keyword bool enabled: Whether the certificate is enabled for use.
        :keyword tags: Application specific metadata in the form of key-value pairs.
        :paramtype tags: dict[str, str]
        :returns: A coroutine for the creation of the certificate. Awaiting the coroutine
         returns the created KeyVaultCertificate if creation is successful, the CertificateOperation if not.
        :rtype: ~azure.keyvault.certificates.KeyVaultCertificate or
         ~azure.keyvault.certificates.CertificateOperation
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START create_certificate]
                :end-before: [END create_certificate]
                :language: python
                :caption: Create a certificate
                :dedent: 8
        """
        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 5
        enabled = kwargs.pop("enabled", None)
        tags = kwargs.pop("tags", None)

        if enabled is not None:
            attributes = self._models.CertificateAttributes(enabled=enabled)
        else:
            attributes = None
        cert_bundle = await self._client.create_certificate(
            vault_base_url=self.vault_url,
            certificate_name=certificate_name,
            certificate_policy=policy._to_certificate_policy_bundle(),
            certificate_attributes=attributes,
            tags=tags,
            error_map=_error_map,
            **kwargs
        )

        create_certificate_operation = CertificateOperation._from_certificate_operation_bundle(cert_bundle)

        command = partial(self.get_certificate_operation, certificate_name=certificate_name, **kwargs)

        get_certificate_command = partial(self.get_certificate, certificate_name=certificate_name, **kwargs)

        create_certificate_polling = CreateCertificatePollerAsync(
            get_certificate_command=get_certificate_command, interval=polling_interval
        )
        return await async_poller(command, create_certificate_operation, None, create_certificate_polling)

    @distributed_trace_async
    async def get_certificate(self, certificate_name: str, **kwargs: "Any") -> KeyVaultCertificate:
        """Gets a certificate with its management policy attached. Requires certificates/get permission.

        Does not accept the version of the certificate as a parameter. To get a specific version of the
        certificate, call :func:`get_certificate_version`.

        :param str certificate_name: The name of the certificate in the given vault.
        :returns: An instance of KeyVaultCertificate
        :rtype: ~azure.keyvault.certificates.KeyVaultCertificate
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the certificate doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START get_certificate]
                :end-before: [END get_certificate]
                :language: python
                :caption: Get a certificate
                :dedent: 8
        """
        bundle = await self._client.get_certificate(
            vault_base_url=self.vault_url,
            certificate_name=certificate_name,
            certificate_version="",
            error_map=_error_map,
            **kwargs
        )
        return KeyVaultCertificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace_async
    async def get_certificate_version(
        self, certificate_name: str, version: str, **kwargs: "Any"
    ) -> KeyVaultCertificate:
        """Gets a specific version of a certificate without returning its management policy.

        Requires certificates/get permission. To get the latest version of the certificate,
        or to get the certificate's policy as well, call :func:`get_certificate`.

        :param str certificate_name: The name of the certificate in the given vault.
        :param str version: The version of the certificate.
        :returns: An instance of KeyVaultCertificate
        :rtype: ~azure.keyvault.certificates.KeyVaultCertificate
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the certificate doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START get_certificate]
                :end-before: [END get_certificate]
                :language: python
                :caption: Get a certificate
                :dedent: 8
        """
        bundle = await self._client.get_certificate(
            vault_base_url=self.vault_url,
            certificate_name=certificate_name,
            certificate_version=version,
            error_map=_error_map,
            **kwargs
        )
        return KeyVaultCertificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace_async
    async def delete_certificate(self, certificate_name: str, **kwargs: "Any") -> DeletedCertificate:
        """Delete all versions of a certificate. Requires certificates/delete permission.

        If the vault has soft-delete enabled, deletion may take several seconds to complete.

        :param str certificate_name: The name of the certificate.
        :returns: The deleted certificate
        :rtype: ~azure.keyvault.certificates.DeletedCertificate
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the certificate doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START delete_certificate]
                :end-before: [END delete_certificate]
                :language: python
                :caption: Delete a certificate
                :dedent: 8
        """
        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 2
        deleted_cert_bundle = await self._client.delete_certificate(
            vault_base_url=self.vault_url, certificate_name=certificate_name, error_map=_error_map, **kwargs
        )
        deleted_certificate = DeletedCertificate._from_deleted_certificate_bundle(deleted_cert_bundle)

        polling_method = AsyncDeleteRecoverPollingMethod(
            # no recovery ID means soft-delete is disabled, in which case we initialize the poller as finished
            finished=deleted_certificate.recovery_id is None,
            command=partial(self.get_deleted_certificate, certificate_name=certificate_name, **kwargs),
            final_resource=deleted_certificate,
            interval=polling_interval,
        )
        await polling_method.run()

        return polling_method.resource()

    @distributed_trace_async
    async def get_deleted_certificate(self, certificate_name: str, **kwargs: "Any") -> DeletedCertificate:
        """Get a deleted certificate. Possible only in a vault with soft-delete enabled.

        Requires certificates/get permission. Retrieves the deleted certificate information
        plus its attributes, such as retention interval, scheduled permanent deletion, and the
        current deletion recovery level.

        :param str certificate_name: The name of the certificate.
        :return: The deleted certificate
        :rtype: ~azure.keyvault.certificates.DeletedCertificate
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the certificate doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START get_deleted_certificate]
                :end-before: [END get_deleted_certificate]
                :language: python
                :caption: Get a deleted certificate
                :dedent: 8
        """
        bundle = await self._client.get_deleted_certificate(
            vault_base_url=self.vault_url, certificate_name=certificate_name, error_map=_error_map, **kwargs
        )
        return DeletedCertificate._from_deleted_certificate_bundle(deleted_certificate_bundle=bundle)

    @distributed_trace_async
    async def purge_deleted_certificate(self, certificate_name: str, **kwargs: "Any") -> None:
        """Permanently deletes a deleted certificate. Possible only in vaults with soft-delete enabled.

        Requires certificates/purge permission.

        Performs an irreversible deletion of the specified certificate, without
        possibility for recovery. The operation is not available if the
        :py:attr:`~azure.keyvault.certificates.CertificateProperties.recovery_level` does not specify 'Purgeable'.
        This method is only necessary for purging a certificate before its
        :py:attr:`~azure.keyvault.certificates.DeletedCertificate.scheduled_purge_date`.

        :param str certificate_name: The name of the certificate
        :return: None
        :rtype: None
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        await self._client.purge_deleted_certificate(
            vault_base_url=self.vault_url, certificate_name=certificate_name, error_map=_error_map, **kwargs
        )

    @distributed_trace_async
    async def recover_deleted_certificate(self, certificate_name: str, **kwargs: "Any") -> KeyVaultCertificate:
        """Recover a deleted certificate to its latest version. Possible only in a vault with soft-delete enabled.

        Requires certificates/recover permission. If the vault does not have soft-delete enabled,
        :func:`delete_certificate` is permanent, and this method will raise an error. Attempting to recover a
        non-deleted certificate will also raise an error.

        :param str certificate_name: The name of the deleted certificate
        :returns: The recovered certificate
        :rtype: ~azure.keyvault.certificates.KeyVaultCertificate
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START recover_deleted_certificate]
                :end-before: [END recover_deleted_certificate]
                :language: python
                :caption: Recover a deleted certificate
                :dedent: 8
        """
        polling_interval = kwargs.pop("_polling_interval", None)
        if polling_interval is None:
            polling_interval = 2
        recovered_cert_bundle = await self._client.recover_deleted_certificate(
            vault_base_url=self.vault_url, certificate_name=certificate_name, error_map=_error_map, **kwargs
        )
        recovered_certificate = KeyVaultCertificate._from_certificate_bundle(recovered_cert_bundle)

        command = partial(self.get_certificate, certificate_name=certificate_name, **kwargs)
        polling_method = AsyncDeleteRecoverPollingMethod(
            command=command, final_resource=recovered_certificate, finished=False, interval=polling_interval
        )
        await polling_method.run()

        return polling_method.resource()

    @distributed_trace_async
    async def import_certificate(
        self, certificate_name: str, certificate_bytes: bytes, **kwargs: "Any"
    ) -> KeyVaultCertificate:
        """Import a certificate created externally. Requires certificates/import permission.

        Imports an existing valid certificate, containing a private key, into
        Azure Key Vault. The certificate to be imported can be in either PFX or
        PEM format. If the certificate is in PEM format the PEM file must
        contain the key as well as x509 certificates.

        :param str certificate_name: The name of the certificate.
        :param bytes certificate_bytes: Bytes of the certificate object to import.
            This certificate needs to contain the private key.
        :keyword bool enabled: Whether the certificate is enabled for use.
        :keyword tags: Application specific metadata in the form of key-value pairs.
        :paramtype tags: dict[str, str]
        :keyword str password: If the private key in the passed in certificate is encrypted, it
         is the password used for encryption.
        :keyword policy: The management policy for the certificate
        :paramtype policy: ~azure.keyvault.certificates.CertificatePolicy
        :returns: The imported KeyVaultCertificate
        :rtype: ~azure.keyvault.certificates.KeyVaultCertificate
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """

        enabled = kwargs.pop("enabled", None)
        password = kwargs.pop("password", None)
        policy = kwargs.pop("policy", None)

        if enabled is not None:
            attributes = self._models.CertificateAttributes(enabled=enabled)
        else:
            attributes = None
        base64_encoded_certificate = base64.b64encode(certificate_bytes).decode("utf-8")
        bundle = await self._client.import_certificate(
            vault_base_url=self.vault_url,
            certificate_name=certificate_name,
            base64_encoded_certificate=base64_encoded_certificate,
            password=password,
            certificate_policy=CertificatePolicy._to_certificate_policy_bundle(policy),
            certificate_attributes=attributes,
            error_map=_error_map,
            **kwargs
        )
        return KeyVaultCertificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace_async
    async def get_certificate_policy(self, certificate_name: str, **kwargs: "Any") -> CertificatePolicy:
        """Gets the policy for a certificate. Requires certificates/get permission.

        Returns the specified certificate policy resources in the key vault.

        :param str certificate_name: The name of the certificate in a given key vault.
        :return: The certificate policy
        :rtype: ~azure.keyvault.certificates.CertificatePolicy
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        bundle = await self._client.get_certificate_policy(
            vault_base_url=self.vault_url, certificate_name=certificate_name, error_map=_error_map, **kwargs
        )
        return CertificatePolicy._from_certificate_policy_bundle(certificate_policy_bundle=bundle)

    @distributed_trace_async
    async def update_certificate_policy(
        self, certificate_name: str, policy: CertificatePolicy, **kwargs: "Any"
    ) -> CertificatePolicy:
        """Updates the policy for a certificate. Requires certificiates/update permission.

        Set specified members in the certificate policy. Leaves others as null.

        :param str certificate_name: The name of the certificate in the given vault.
        :param policy: The policy for the certificate.
        :type policy: ~azure.keyvault.certificates.CertificatePolicy
        :return: The certificate policy
        :rtype: ~azure.keyvault.certificates.CertificatePolicy
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        bundle = await self._client.update_certificate_policy(
            vault_base_url=self.vault_url,
            certificate_name=certificate_name,
            certificate_policy=policy._to_certificate_policy_bundle(),
            error_map=_error_map,
            **kwargs
        )
        return CertificatePolicy._from_certificate_policy_bundle(certificate_policy_bundle=bundle)

    @distributed_trace_async
    async def update_certificate_properties(
        self, certificate_name: str, version: Optional[str] = None, **kwargs: "Any"
    ) -> KeyVaultCertificate:
        """Change a certificate's properties. Requires certificates/update permission.

        :param str certificate_name: The name of the certificate in the given key vault.
        :param str version: The version of the certificate.
        :keyword bool enabled: Whether the certificate is enabled for use.
        :keyword tags: Application specific metadata in the form of key-value pairs.
        :paramtype tags: dict[str, str]
        :returns: The updated KeyVaultCertificate
        :rtype: ~azure.keyvault.certificates.KeyVaultCertificate
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START update_certificate]
                :end-before: [END update_certificate]
                :language: python
                :caption: Update a certificate's attributes
                :dedent: 8
        """

        enabled = kwargs.pop("enabled", None)

        if enabled is not None:
            attributes = self._models.CertificateAttributes(enabled=enabled)
        else:
            attributes = None

        bundle = await self._client.update_certificate(
            vault_base_url=self.vault_url,
            certificate_name=certificate_name,
            certificate_version=version or "",
            certificate_attributes=attributes,
            error_map=_error_map,
            **kwargs
        )
        return KeyVaultCertificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace_async
    async def backup_certificate(self, certificate_name: str, **kwargs: "Any") -> bytes:
        """Back up a certificate in a protected form useable only by Azure Key Vault.

        Requires certificates/backup permission. This is intended to allow copying a certificate
        from one vault to another. Both vaults must be owned by the same Azure subscription.
        Also, backup / restore cannot be performed across geopolitical boundaries. For example, a backup
        from a vault in a USA region cannot be restored to a vault in an EU region.

        :param str certificate_name: The name of the certificate.
        :return: The backup blob containing the backed up certificate.
        :rtype: bytes
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the certificate doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START backup_certificate]
                :end-before: [END backup_certificate]
                :language: python
                :caption: Get a certificate backup
                :dedent: 8
        """
        backup_result = await self._client.backup_certificate(
            vault_base_url=self.vault_url, certificate_name=certificate_name, error_map=_error_map, **kwargs
        )
        return backup_result.value

    @distributed_trace_async
    async def restore_certificate_backup(self, backup: bytes, **kwargs: "Any") -> KeyVaultCertificate:
        """Restore a certificate backup to the vault. Requires certificates/restore permission.

        This restores all versions of the certificate, with its name, attributes, and access control policies.
        If the certificate's name is already in use, restoring it will fail. Also, the target vault must
        be owned by the same Microsoft Azure subscription as the source vault.

        :param bytes backup: The backup blob associated with a certificate bundle.
        :return: The restored KeyVaultCertificate
        :rtype: ~azure.keyvault.certificates.KeyVaultCertificate
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START restore_certificate]
                :end-before: [END restore_certificate]
                :language: python
                :caption: Restore a certificate backup
                :dedent: 8
        """
        bundle = await self._client.restore_certificate(
            vault_base_url=self.vault_url, certificate_bundle_backup=backup, error_map=_error_map, **kwargs
        )
        return KeyVaultCertificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace
    def list_deleted_certificates(self, **kwargs: "Any") -> AsyncIterable[DeletedCertificate]:
        """Lists the currently-recoverable deleted certificates. Possible only if vault is soft-delete enabled.

        Requires certificates/get/list permission. Retrieves the certificates in the current vault which
        are in a deleted state and ready for recovery or purging. This operation includes
        deletion-specific information.

        :keyword bool include_pending: Specifies whether to include certificates which are
         not completely deleted.
        :return: An iterator like instance of DeletedCertificate
        :rtype:
         ~azure.core.paging.ItemPaged[~azure.keyvault.certificates.DeletedCertificate]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START list_deleted_certificates]
                :end-before: [END list_deleted_certificates]
                :language: python
                :caption: List all the deleted certificates
                :dedent: 8
        """
        max_page_size = kwargs.pop("max_page_size", None)

        return self._client.get_deleted_certificates(
            vault_base_url=self._vault_url,
            maxresults=max_page_size,
            cls=lambda objs: [DeletedCertificate._from_deleted_certificate_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_properties_of_certificates(self, **kwargs: "Any") -> AsyncIterable[CertificateProperties]:
        """List identifiers and properties of all certificates in the vault.

        Requires certificates/list permission.

        :keyword bool include_pending: Specifies whether to include certificates which are not
         completely provisioned.
        :returns: An iterator like instance of CertificateProperties
        :rtype:
         ~azure.core.paging.ItemPaged[~azure.keyvault.certificates.CertificateProperties]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START list_properties_of_certificates]
                :end-before: [END list_properties_of_certificates]
                :language: python
                :caption: List all certificates
                :dedent: 8
        """
        max_page_size = kwargs.pop("max_page_size", None)

        return self._client.get_certificates(
            vault_base_url=self._vault_url,
            maxresults=max_page_size,
            cls=lambda objs: [CertificateProperties._from_certificate_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace
    def list_properties_of_certificate_versions(
        self, certificate_name: str, **kwargs: "Any"
    ) -> AsyncIterable[CertificateProperties]:
        """List the identifiers and properties of a certificate's versions.

        Requires certificates/list permission.

        :param str certificate_name: The name of the certificate.
        :returns: An iterator like instance of CertificateProperties
        :rtype:
         ~azure.core.paging.ItemPaged[~azure.keyvault.certificates.CertificateProperties]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START list_properties_of_certificate_versions]
                :end-before: [END list_properties_of_certificate_versions]
                :language: python
                :caption: List all versions of a certificate
                :dedent: 8
        """
        max_page_size = kwargs.pop("max_page_size", None)
        return self._client.get_certificate_versions(
            vault_base_url=self._vault_url,
            certificate_name=certificate_name,
            maxresults=max_page_size,
            cls=lambda objs: [CertificateProperties._from_certificate_item(x) for x in objs],
            **kwargs
        )

    @distributed_trace_async
    async def set_contacts(self, contacts: Iterable[CertificateContact], **kwargs: "Any") -> List[CertificateContact]:
        # pylint:disable=unsubscriptable-object

        # disabled unsubscriptable-object because of pylint bug referenced here:
        # https://github.com/PyCQA/pylint/issues/2377
        """Sets the certificate contacts for the key vault. Requires certificates/managecontacts permission.

        :param contacts: The contact list for the vault certificates.
        :type contacts: list[~azure.keyvault.certificates.CertificateContact]
        :returns: The created list of contacts
        :rtype: list[~azure.keyvault.certificates.CertificateContact]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START set_contacts]
                :end-before: [END set_contacts]
                :language: python
                :caption: Create contacts
                :dedent: 8
        """
        contacts = await self._client.set_certificate_contacts(
            vault_base_url=self.vault_url,
            contact_list=[c._to_certificate_contacts_item() for c in contacts],
            error_map=_error_map,
            **kwargs
        )
        return [CertificateContact._from_certificate_contacts_item(contact_item=item) for item in contacts.contact_list]

    @distributed_trace_async
    async def get_contacts(self, **kwargs: "Any") -> List[CertificateContact]:
        # pylint:disable=unsubscriptable-object

        # disabled unsubscruptable-object because of pylint bug referenced here:
        # https://github.com/PyCQA/pylint/issues/2377
        """Gets the certificate contacts for the key vault. Requires the certificates/managecontacts permission.

        :return: The certificate contacts for the key vault.
        :rtype: list[azure.keyvault.certificates.CertificateContact]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START get_contacts]
                :end-before: [END get_contacts]
                :language: python
                :caption: Get contacts
                :dedent: 8
        """
        contacts = await self._client.get_certificate_contacts(
            vault_base_url=self._vault_url, error_map=_error_map, **kwargs
        )
        return [CertificateContact._from_certificate_contacts_item(contact_item=item) for item in contacts.contact_list]

    @distributed_trace_async
    async def delete_contacts(self, **kwargs: "Any") -> List[CertificateContact]:
        # pylint:disable=unsubscriptable-object

        # disabled unsubscruptable-object because of pylint bug referenced here:
        # https://github.com/PyCQA/pylint/issues/2377
        """Deletes the certificate contacts for the key vault. Requires the certificates/managecontacts permission.

        :return: The deleted contacts for the key vault.
        :rtype: list[~azure.keyvault.certificates.CertificateContact]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START delete_contacts]
                :end-before: [END delete_contacts]
                :language: python
                :caption: Delete contacts
                :dedent: 8
        """
        contacts = await self._client.delete_certificate_contacts(
            vault_base_url=self.vault_url, error_map=_error_map, **kwargs
        )
        return [CertificateContact._from_certificate_contacts_item(contact_item=item) for item in contacts.contact_list]

    @distributed_trace_async
    async def get_certificate_operation(self, certificate_name: str, **kwargs: "Any") -> CertificateOperation:
        """Gets the creation operation of a certificate. Requires the certificates/get permission.

        :param str certificate_name: The name of the certificate.
        :returns: The created CertificateOperation
        :rtype: ~azure.keyvault.certificates.CertificateOperation
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the certificate doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors
        """

        bundle = await self._client.get_certificate_operation(
            vault_base_url=self.vault_url, certificate_name=certificate_name, error_map=_error_map, **kwargs
        )
        return CertificateOperation._from_certificate_operation_bundle(certificate_operation_bundle=bundle)

    @distributed_trace_async
    async def delete_certificate_operation(self, certificate_name: str, **kwargs: "Any") -> CertificateOperation:
        """Deletes and stops the creation operation for a specific certificate.

        Requires the certificates/update permission.

        :param str certificate_name: The name of the certificate.
        :return: The deleted CertificateOperation
        :rtype: ~azure.keyvault.certificates.CertificateOperation
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the operation doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors
        """
        bundle = await self._client.delete_certificate_operation(
            vault_base_url=self.vault_url, certificate_name=certificate_name, error_map=_error_map, **kwargs
        )
        return CertificateOperation._from_certificate_operation_bundle(certificate_operation_bundle=bundle)

    @distributed_trace_async
    async def cancel_certificate_operation(self, certificate_name: str, **kwargs: "Any") -> CertificateOperation:
        """Cancels an in-progress certificate operation. Requires the certificates/update permission.

        :param str certificate_name: The name of the certificate.
        :returns: The cancelled certificate operation
        :rtype: ~azure.keyvault.certificates.CertificateOperation
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """
        bundle = await self._client.update_certificate_operation(
            vault_base_url=self.vault_url,
            certificate_name=certificate_name,
            cancellation_requested=True,
            error_map=_error_map,
            **kwargs
        )
        return CertificateOperation._from_certificate_operation_bundle(certificate_operation_bundle=bundle)

    @distributed_trace_async
    async def merge_certificate(
        self, certificate_name: str, x509_certificates: Iterable[bytes], **kwargs: "Any"
    ) -> KeyVaultCertificate:
        """Merges a certificate or a certificate chain with a key pair existing on the server.

        Requires the certificates/create permission. Performs the merging of a certificate or
        certificate chain with a key pair currently available in the service.
        Make sure when creating the certificate to merge using :func:`begin_create_certificate` that you set
        its issuer to 'Unknown'. This way Key Vault knows that the certificate will not be signed
        by an issuer known to it.

        :param str certificate_name: The name of the certificate
        :param x509_certificates: The certificate or the certificate chain to merge.
        :type x509_certificates: list[bytes]
        :keyword bool enabled: Whether the certificate is enabled for use.
        :keyword tags: Application specific metadata in the form of key-value pairs.
        :paramtype tags: dict[str, str]
        :return: The merged certificate operation
        :rtype: ~azure.keyvault.certificates.CertificateOperation
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """

        enabled = kwargs.pop("enabled", None)

        if enabled is not None:
            attributes = self._models.CertificateAttributes(enabled=enabled)
        else:
            attributes = None
        bundle = await self._client.merge_certificate(
            vault_base_url=self.vault_url,
            certificate_name=certificate_name,
            x509_certificates=x509_certificates,
            certificate_attributes=attributes,
            error_map=_error_map,
            **kwargs
        )
        return KeyVaultCertificate._from_certificate_bundle(certificate_bundle=bundle)

    @distributed_trace_async
    async def get_issuer(self, issuer_name: str, **kwargs: "Any") -> CertificateIssuer:
        """Gets the specified certificate issuer. Requires certificates/manageissuers/getissuers permission.

        :param str issuer_name: The name of the issuer.
        :return: The specified certificate issuer.
        :rtype: ~azure.keyvault.certificates.CertificateIssuer
        :raises:
            :class:`~azure.core.exceptions.ResourceNotFoundError` if the issuer doesn't exist,
            :class:`~azure.core.exceptions.HttpResponseError` for other errors

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START get_issuer]
                :end-before: [END get_issuer]
                :language: python
                :caption: Get an issuer
                :dedent: 8
        """
        issuer_bundle = await self._client.get_certificate_issuer(
            vault_base_url=self.vault_url, issuer_name=issuer_name, error_map=_error_map, **kwargs
        )
        return CertificateIssuer._from_issuer_bundle(issuer_bundle=issuer_bundle)

    @distributed_trace_async
    async def create_issuer(self, issuer_name: str, provider: str, **kwargs: "Any") -> CertificateIssuer:
        """Sets the specified certificate issuer. Requires certificates/setissuers permission.

        :param str issuer_name: The name of the issuer.
        :param str provider: The issuer provider.
        :keyword bool enabled: Whether the issuer is enabled for use.
        :keyword str account_id: The user name/account name/account id.
        :keyword str password: The password/secret/account key.
        :keyword str organization_id: Id of the organization
        :keyword admin_contacts: Contact details of the organization administrators of the
         certificate issuer.
        :paramtype admin_contacts: list[~azure.keyvault.certificates.AdministratorContact]
        :returns: The created CertificateIssuer
        :rtype: ~azure.keyvault.certificates.CertificateIssuer
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START create_issuer]
                :end-before: [END create_issuer]
                :language: python
                :caption: Create an issuer
                :dedent: 8
        """

        enabled = kwargs.pop("enabled", None)
        account_id = kwargs.pop("account_id", None)
        password = kwargs.pop("password", None)
        organization_id = kwargs.pop("organization_id", None)
        admin_contacts = kwargs.pop("admin_contacts", None)

        if account_id or password:
            issuer_credentials = self._models.IssuerCredentials(account_id=account_id, password=password)
        else:
            issuer_credentials = None
        if admin_contacts:
            admin_details = [
                self._models.AdministratorDetails(
                    first_name=contact.first_name,
                    last_name=contact.last_name,
                    email_address=contact.email,
                    phone=contact.phone,
                )
                for contact in admin_contacts
            ]
        else:
            admin_details = None
        if organization_id or admin_details:
            organization_details = self._models.OrganizationDetails(
                id=organization_id, admin_details=admin_details
            )
        else:
            organization_details = None
        if enabled is not None:
            issuer_attributes = self._models.IssuerAttributes(enabled=enabled)
        else:
            issuer_attributes = None
        issuer_bundle = await self._client.set_certificate_issuer(
            vault_base_url=self.vault_url,
            issuer_name=issuer_name,
            provider=provider,
            credentials=issuer_credentials,
            organization_details=organization_details,
            attributes=issuer_attributes,
            error_map=_error_map,
            **kwargs
        )
        return CertificateIssuer._from_issuer_bundle(issuer_bundle=issuer_bundle)

    @distributed_trace_async
    async def update_issuer(self, issuer_name: str, **kwargs: "Any") -> CertificateIssuer:
        """Updates the specified certificate issuer. Requires certificates/setissuers permission.

        :param str issuer_name: The name of the issuer.
        :keyword bool enabled: Whether the issuer is enabled for use.
        :keyword str provider: The issuer provider
        :keyword str account_id: The user name/account name/account id.
        :keyword str password: The password/secret/account key.
        :keyword str organization_id: Id of the organization
        :keyword admin_contacts: Contact details of the organization administrators of
         the certificate issuer
        :paramtype admin_contacts: list[~azure.keyvault.certificates.AdministratorContact]
        :return: The updated issuer
        :rtype: ~azure.keyvault.certificates.CertificateIssuer
        :raises: :class:`~azure.core.exceptions.HttpResponseError`
        """

        enabled = kwargs.pop("enabled", None)
        provider = kwargs.pop("provider", None)
        account_id = kwargs.pop("account_id", None)
        password = kwargs.pop("password", None)
        organization_id = kwargs.pop("organization_id", None)
        admin_contacts = kwargs.pop("admin_contacts", None)

        if account_id or password:
            issuer_credentials = self._models.IssuerCredentials(account_id=account_id, password=password)
        else:
            issuer_credentials = None
        if admin_contacts:
            admin_details = list(
                self._models.AdministratorDetails(
                    first_name=contact.first_name,
                    last_name=contact.last_name,
                    email_address=contact.email,
                    phone=contact.phone,
                )
                for contact in admin_contacts
            )
        else:
            admin_details = None
        if organization_id or admin_details:
            organization_details = self._models.OrganizationDetails(
                id=organization_id, admin_details=admin_details
            )
        else:
            organization_details = None
        if enabled is not None:
            issuer_attributes = self._models.IssuerAttributes(enabled=enabled)
        else:
            issuer_attributes = None
        issuer_bundle = await self._client.update_certificate_issuer(
            vault_base_url=self.vault_url,
            issuer_name=issuer_name,
            provider=provider,
            credentials=issuer_credentials,
            organization_details=organization_details,
            attributes=issuer_attributes,
            error_map=_error_map,
            **kwargs
        )
        return CertificateIssuer._from_issuer_bundle(issuer_bundle=issuer_bundle)

    @distributed_trace_async
    async def delete_issuer(self, issuer_name: str, **kwargs: "Any") -> CertificateIssuer:
        """Deletes the specified certificate issuer.

        Requires certificates/manageissuers/deleteissuers permission.

        :param str issuer_name: The name of the issuer.
        :return: CertificateIssuer
        :rtype: ~azure.keyvault.certificates.CertificateIssuer
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START delete_issuer]
                :end-before: [END delete_issuer]
                :language: python
                :caption: Delete an issuer
                :dedent: 8
        """
        issuer_bundle = await self._client.delete_certificate_issuer(
            vault_base_url=self.vault_url, issuer_name=issuer_name, error_map=_error_map, **kwargs
        )
        return CertificateIssuer._from_issuer_bundle(issuer_bundle=issuer_bundle)

    @distributed_trace
    def list_properties_of_issuers(self, **kwargs: "Any") -> AsyncIterable[IssuerProperties]:
        """Lists properties of the certificate issuers for the key vault.

        Requires the certificates/manageissuers/getissuers permission.

        :return: An iterator like instance of Issuers
        :rtype: ~azure.core.paging.ItemPaged[~azure.keyvault.certificates.CertificateIssuer]
        :raises: :class:`~azure.core.exceptions.HttpResponseError`

        Example:
            .. literalinclude:: ../tests/test_examples_certificates_async.py
                :start-after: [START list_properties_of_issuers]
                :end-before: [END list_properties_of_issuers]
                :language: python
                :caption: List issuers of a vault
                :dedent: 8
        """
        max_page_size = kwargs.pop("max_page_size", None)
        return self._client.get_certificate_issuers(
            vault_base_url=self.vault_url,
            maxresults=max_page_size,
            cls=lambda objs: [IssuerProperties._from_issuer_item(x) for x in objs],
            **kwargs
        )
