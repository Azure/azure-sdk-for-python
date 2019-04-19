import os
import logging
from azure.core import AzureError
from azure.configuration import AzureConfigurationClient
from azure.configuration import ConfigurationSetting

PAGE_SIZE = 100


class AzConfigTestData:
    def __init__(self):
        self.key_uuid = None
        self.label1 = None
        self.label2 = None  # contains reserved chars *,\
        self.label_uuid = None
        self.label1_data = []
        self.label2_data = []
        self.no_label_data = []


def _add_for_test(app_config_client, kv):
    exist = bool(list(app_config_client.list_configuration_settings(keys=[kv.key], labels=[kv.label])))
    if exist:
        _delete_from_test(app_config_client, key=kv.key, label=kv.label)
    return app_config_client.add_configuration_setting(kv)


def _delete_from_test(app_config_client, key, label):
    try:
        app_config_client.delete_configuration_setting(key=key, label=label)
    except AzureError:
        logging.debug("Error occurred removing configuration setting %s %s" % (key, label))


def _create_app_config_client():
    connection_str = os.environ['APP_CONFIG_CONNECTION']
    return AzureConfigurationClient(connection_str)


def setup_data():
    test_data = AzConfigTestData()
    app_config_client = _create_app_config_client()

    key_uuid = "test_key_a6af8952-54a6-11e9-b600-2816a84d0309"
    label_uuid = "1d7b2b28-549e-11e9-b51c-2816a84d0309"
    label1 = "test_label1_" + label_uuid
    label2 = "test_label2_*, \\" + label_uuid
    test_content_type = "test_content_type"
    test_value = "test_value"

    test_data.key_uuid = key_uuid
    test_data.label_uuid = label_uuid
    test_data.label1 = label1
    test_data.label2 = label2

    test_data.label1_data.append(
        _add_for_test(
            app_config_client,
            ConfigurationSetting(
                key=key_uuid + "_1",
                label=label1,
                value=test_value,
                tags={
                    "tag1": "tag1",
                    "tag2": "tag2"
                },
                content_type=test_content_type
            )
        )
    )
    test_data.label2_data.append(
        _add_for_test(
            app_config_client,
            ConfigurationSetting(
                key=key_uuid + "_2",
                label=label2,
                value=test_value,
                tags={
                    "tag1": "tag1",
                    "tag2": "tag2"
                },
                content_type=test_content_type
            )
        )
    )

    # create a configuration_setting object without label
    test_data.no_label_data.append(
        _add_for_test(
            app_config_client,
            ConfigurationSetting(
                key=key_uuid + "_3",
                label=None,
                value=test_value,
                tags={
                    "tag1": "tag1",
                    "tag2": "tag2"
                },
                content_type=test_content_type
            )
        )
    )
    return test_data


def teardown_data(test_data):
    app_config_client = _create_app_config_client()
    for kv in test_data.label1_data:
        _delete_from_test(app_config_client, kv.key, label=kv.label)
    for kv in test_data.label2_data:
        _delete_from_test(app_config_client, kv.key, label=kv.label)
    for kv in test_data.no_label_data:
        _delete_from_test(app_config_client, kv.key, label=kv.label)
