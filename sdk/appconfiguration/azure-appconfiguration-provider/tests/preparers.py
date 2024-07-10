# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import functools
from devtools_testutils import EnvironmentVariableLoader
import inspect

AppConfigProviderPreparer = functools.partial(
    EnvironmentVariableLoader,
    "appconfiguration",
    keyvault_secret_url="https://fake-keyvault.vault.azure.net/secrets/fake-secret/",
    appconfiguration_keyvault_secret_url="https://fake-keyvault.vault.azure.net/secrets/fake-secret/",
    appconfiguration_connection_string="Endpoint=https://fake-endpoint.azconfig.io;Id=0-l4-s0:h5htBaY5Z1LwFz50bIQv;Secret=lamefakesecretlamefakesecretlamefakesecrett=",
    appconfiguration_endpoint_string="https://fake-endpoint.azconfig.io",
)


def app_config_decorator(func, **kwargs):
    @AppConfigProviderPreparer()
    def wrapper(*args, **kwargs):
        appconfiguration_connection_string = kwargs.pop("appconfiguration_connection_string")
        kwargs["appconfiguration_connection_string"] = appconfiguration_connection_string

        appconfiguration_keyvault_secret_url = kwargs.pop("appconfiguration_keyvault_secret_url")
        kwargs["appconfiguration_keyvault_secret_url"] = appconfiguration_keyvault_secret_url

        trimmed_kwargs = {k: v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(func, trimmed_kwargs)

        func(*args, **trimmed_kwargs)

    return wrapper


def app_config_decorator_aad(func, **kwargs):
    @AppConfigProviderPreparer()
    def wrapper(*args, **kwargs):
        appconfiguration_endpoint_string = kwargs.pop("appconfiguration_endpoint_string")
        kwargs["appconfiguration_endpoint_string"] = appconfiguration_endpoint_string

        appconfiguration_keyvault_secret_url = kwargs.pop("appconfiguration_keyvault_secret_url")
        kwargs["appconfiguration_keyvault_secret_url"] = appconfiguration_keyvault_secret_url

        trimmed_kwargs = {k: v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(func, trimmed_kwargs)

        func(*args, **trimmed_kwargs)

    return wrapper


def trim_kwargs_from_test_function(fn, kwargs):
    # the next function is the actual test function. the kwargs need to be trimmed so
    # that parameters which are not required will not be passed to it.
    if not getattr(fn, "__is_preparer", False):
        try:
            args, _, kw, _, _, _, _ = inspect.getfullargspec(fn)
        except AttributeError:
            args, _, kw, _ = inspect.getargspec(fn)  # pylint: disable=deprecated-method
        if kw is None:
            args = set(args)
            for key in [k for k in kwargs if k not in args]:
                del kwargs[key]
