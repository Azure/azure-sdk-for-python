
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from devtools_testutils import PowerShellPreparer
from azure.appconfiguration import (
    AzureAppConfigurationClient,
    ConfigurationSetting,
)
from azure.core.exceptions import AzureError
from consts import (
    KEY,
    LABEL,
    TEST_VALUE,
    TEST_CONTENT_TYPE,
    LABEL_RESERVED_CHARS,
    PAGE_SIZE,
    KEY_UUID,
)
import functools
import inspect

AppConfigPreparer = functools.partial(
    PowerShellPreparer,
    'appconfiguration',
    appconfiguration_connection_string="Endpoint=https://fake_app_config.azconfig-test.io;Id=0-l4-s0:h5htBaY5Z1LwFz50bIQv;Secret=lamefakesecretlamefakesecretlamefakesecrett=",
    appconfiguration_endpoint_string="https://fake_app_config.azconfig-test.io")

def _add_for_test(client, kv):
    exist = bool(
        list(
            client.list_configuration_settings(
                key_filter=kv.key, label_filter=kv.label
            )
        )
    )
    if exist:
        _delete_from_test(client, kv.key, kv.label)
    return client.add_configuration_setting(kv)

def _delete_from_test(client, key, label):
    try:
        client.delete_configuration_setting(key=key, label=label)
    except AzureError:
        logging.debug(
            "Error occurred removing configuration setting %s %s during unit test"
            % (key, label)
        )

def trim_kwargs_from_test_function(fn, kwargs):
    # the next function is the actual test function. the kwargs need to be trimmed so
    # that parameters which are not required will not be passed to it.
    if not getattr(fn, '__is_preparer', False):
        try:
            args, _, kw, _, _, _, _ = inspect.getfullargspec(fn)
        except AttributeError:
            args, _, kw, _ = inspect.getargspec(fn) # pylint: disable=deprecated-method
        if kw is None:
            args = set(args)
            for key in [k for k in kwargs if k not in args]:
                del kwargs[key]

def app_config_decorator(func, **kwargs):

    @AppConfigPreparer()
    def wrapper(*args, **kwargs):
        appconfiguration_connection_string = kwargs.pop("appconfiguration_connection_string")
        client = AzureAppConfigurationClient.from_connection_string(appconfiguration_connection_string)

        kwargs['client'] = client
        kwargs['appconfiguration_connection_string'] = appconfiguration_connection_string

        # Do setUp on client
        test_config_setting = _add_for_test(
            client,
            ConfigurationSetting(
                key=KEY,
                label=LABEL,
                value=TEST_VALUE,
                content_type=TEST_CONTENT_TYPE,
                tags={"tag1": "tag1", "tag2": "tag2"},
            )
        )
        test_config_setting_no_label = _add_for_test(
            client,
            ConfigurationSetting(
                key=KEY,
                label=None,
                value=TEST_VALUE,
                content_type=TEST_CONTENT_TYPE,
                tags={"tag1": "tag1", "tag2": "tag2"},
            )
        )
        to_delete = [test_config_setting, test_config_setting_no_label]

        kwargs['test_config_setting'] = test_config_setting
        kwargs['test_config_setting_no_label'] = test_config_setting_no_label

        trimmed_kwargs = {k:v for k, v in kwargs.items()}
        trim_kwargs_from_test_function(func, trimmed_kwargs)

        func(*args, **trimmed_kwargs)

        for item in to_delete:
            try:
                client.delete_configuration_setting(
                    key=item.key, label=item.label
                )
            except:
                print("Issue deleting config with key {} and label {}".format(item.key, item.label))

    return wrapper
