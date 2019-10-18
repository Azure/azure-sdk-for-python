# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
from azure.profiles import KnownProfiles, ProfileDefinition
from azure.profiles.multiapiclient import MultiApiClientMixin

from .v7_0.version import VERSION as V7_0_VERSION
from .v2016_10_01.version import VERSION as V2016_10_01_VERSION


class KeyVaultClient(MultiApiClientMixin):
    """The key vault client performs cryptographic key operations and vault operations against the Key Vault service.
    Implementation depends on the API version:

         * 2016-10-01: :class:`v2016_10_01.KeyVaultClient<azure.keyvault._generated.v2016_10_01.KeyVaultClient>`
         * 7.0: :class:`v7_0.KeyVaultClient<azure.keyvault._generated.v7_0.KeyVaultClient>`

    :param credentials: Credentials needed for the client to connect to Azure.
    :type credentials: :mod:`A msrestazure Credentials
     object<msrestazure.azure_active_directory>`

    :param str api_version: API version to use if no profile is provided, or if
     missing in profile.
    :param profile: A profile definition, from KnownProfiles to dict.
    :type profile: azure.profiles.KnownProfiles
    """

    DEFAULT_API_VERSION = V7_0_VERSION
    _PROFILE_TAG = "azure.keyvault.KeyVaultClient"
    LATEST_PROFILE = ProfileDefinition({_PROFILE_TAG: {None: DEFAULT_API_VERSION}}, _PROFILE_TAG + " latest")

    _init_complete = False

    def __init__(self, credentials, pipeline=None, api_version=None, aio=False, profile=KnownProfiles.default):
        self._client_impls = {}
        self._pipeline = pipeline
        self._entered = False
        self._aio = aio
        super(KeyVaultClient, self).__init__(api_version=api_version, profile=profile)

        self._credentials = credentials
        self._init_complete = True

    @staticmethod
    def get_configuration_class(api_version, aio=False):
        """
        Get the versioned configuration implementation corresponding to the current profile.
        :return: The versioned configuration implementation.
        """
        if api_version == V7_0_VERSION:
            if aio:
                from .v7_0.aio._configuration_async import KeyVaultClientConfiguration as ImplConfig
            else:
                from .v7_0._configuration import KeyVaultClientConfiguration as ImplConfig
        elif api_version == V2016_10_01_VERSION:
            if aio:
                from .v2016_10_01.aio._configuration_async import KeyVaultClientConfiguration as ImplConfig
            else:
                from .v2016_10_01._configuration import KeyVaultClientConfiguration as ImplConfig
        else:
            raise NotImplementedError("API version {} is not available".format(api_version))
        return ImplConfig

    @property
    def models(self):
        """Module depends on the API version:
            * 2016-10-01: :mod:`v2016_10_01.models<azure.keyvault._generated.v2016_10_01.models>`
            * 7.0: :mod:`v7_0.models<azure.keyvault._generated.v7_0.models>`
        """
        api_version = self._get_api_version(None)

        if api_version == V7_0_VERSION:
            from .v7_0 import models as impl_models
        elif api_version == V2016_10_01_VERSION:
            from .v2016_10_01 import models as impl_models
        else:
            raise NotImplementedError("APIVersion {} is not available".format(api_version))
        return impl_models

    def _get_client_impl(self):
        """
        Get the versioned client implementation corresponding to the current profile.
        :return:  The versioned client implementation.
        """
        api_version = self._get_api_version(None)
        if api_version not in self._client_impls:
            self._create_client_impl(api_version)
        return self._client_impls[api_version]

    def _create_client_impl(self, api_version):
        """
        Creates the client implementation corresponding to the specified api_version.
        :param api_version:
        :return:
        """
        if api_version == V7_0_VERSION:
            if self._aio:
                from .v7_0.aio import KeyVaultClient as ImplClient
            else:
                from .v7_0 import KeyVaultClient as ImplClient
        elif api_version == V2016_10_01_VERSION:
            if self._aio:
                from .v2016_10_01.aio import KeyVaultClient as ImplClient
            else:
                from .v2016_10_01 import KeyVaultClient as ImplClient
        else:
            raise NotImplementedError("API version {} is not available".format(api_version))

        impl = ImplClient(credentials=self._credentials, pipeline=self._pipeline)

        # if __enter__ has previously been called and the impl client has __enter__ defined we need to call it
        if self._entered:
            if hasattr(impl, "__enter__"):
                impl.__enter__()
            elif hasattr(impl, "__aenter__"):
                impl.__aenter__()

        self._client_impls[api_version] = impl
        return impl

    def __aenter__(self, *args, **kwargs):
        """
        Calls __aenter__ on all client implementations which support it
        :param args: positional arguments to relay to client implementations of __aenter__
        :param kwargs: keyword arguments to relay to client implementations of __aenter__
        :return: returns the current KeyVaultClient instance
        """
        for _, impl in self._client_impls.items():
            if hasattr(impl, "__aenter__"):
                impl.__aenter__(*args, **kwargs)

        # mark the current KeyVaultClient as _entered so that client implementations instantiated
        # subsequently will also have __aenter__ called on them as appropriate
        self._entered = True
        return self

    def __enter__(self, *args, **kwargs):
        """
        Calls __enter__ on all client implementations which support it
        :param args: positional arguments to relay to client implementations of __enter__
        :param kwargs: keyword arguments to relay to client implementations of __enter__
        :return: returns the current KeyVaultClient instance
        """
        for _, impl in self._client_impls.items():
            if hasattr(impl, "__enter__"):
                impl.__enter__(*args, **kwargs)

        # mark the current KeyVaultClient as _entered so that client implementations instantiated
        # subsequently will also have __enter__ called on them as appropriate
        self._entered = True
        return self

    def __aexit__(self, *args, **kwargs):
        """
        Calls __aexit__ on all client implementations which support it
        :param args: positional arguments to relay to client implementations of __aexit__
        :param kwargs: keyword arguments to relay to client implementations of __aexit__
        :return: returns the current KeyVaultClient instance
        """
        for _, impl in self._client_impls.items():
            if hasattr(impl, "__aexit__"):
                impl.__aexit__(*args, **kwargs)
        return self

    def __exit__(self, *args, **kwargs):
        """
        Calls __exit__ on all client implementations which support it
        :param args: positional arguments to relay to client implementations of __enter__
        :param kwargs: keyword arguments to relay to client implementations of __enter__
        :return: returns the current KeyVaultClient instance
        """
        for _, impl in self._client_impls.items():
            if hasattr(impl, "__exit__"):
                impl.__exit__(*args, **kwargs)
        return self

    def __getattr__(self, name):
        """
        In the case that the attribute is not defined on the custom KeyVaultClient.  Attempt to get
        the attribute from the versioned client implementation corresponding to the current profile.
        :param name: Name of the attribute retrieve from the current versioned client implementation
        :return: The value of the specified attribute on the current client implementation.
        """
        impl = self._get_client_impl()
        return getattr(impl, name)

    def __setattr__(self, name, attr):
        """
        Sets the specified attribute either on the custom KeyVaultClient or the current underlying implementation.
        :param name: Name of the attribute to set
        :param attr: Value of the attribute to set
        :return: None
        """
        if self._init_complete and not hasattr(self, name):
            impl = self._get_client_impl()
            setattr(impl, name, attr)
        else:
            super(KeyVaultClient, self).__setattr__(name, attr)
