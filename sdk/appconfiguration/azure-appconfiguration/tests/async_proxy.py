from asyncio import get_event_loop
from azure.appconfiguration.aio import AzureAppConfigurationClient


def _to_list(ait):
    async def lst():
        result = []
        async for item in ait:
            result.append(item)
        return result

    return get_event_loop().run_until_complete(lst())


class AzureAppConfigurationClientProxy(object):
    @classmethod
    def from_connection_string(
        cls,
        connection_string,  # type: str
        **kwargs
    ):
        return cls(
            AzureAppConfigurationClient.from_connection_string(
                connection_string, **kwargs
            )
        )

    def __init__(self, obj):
        self.obj = obj

    def get_configuration_setting(
        self, key, label=None, accept_datetime=None, **kwargs
    ):
        return get_event_loop().run_until_complete(
            self.obj.get_configuration_setting(
                key, label=label, accept_datetime=accept_datetime, **kwargs
            )
        )

    def add_configuration_setting(self, configuration_setting, **kwargs):
        return get_event_loop().run_until_complete(
            self.obj.add_configuration_setting(configuration_setting, **kwargs)
        )

    def delete_configuration_setting(self, key, label=None, etag=None, **kwargs):
        return get_event_loop().run_until_complete(
            self.obj.delete_configuration_setting(key, label=label, etag=etag, **kwargs)
        )

    def list_configuration_settings(
        self, label_filter=None, key_filter=None, accept_datetime=None, fields=None, **kwargs
    ):
        paged = self.obj.list_configuration_settings(
            label_filter=label_filter,
            key_filter=key_filter,
            accept_datetime=accept_datetime,
            fields=fields,
            **kwargs
        )
        return _to_list(paged)

    def list_revisions(
        self, label_filter=None, key_filter=None, accept_datetime=None, fields=None, **kwargs
    ):
        paged = self.obj.list_revisions(
            label_filter=label_filter,
            key_filter=key_filter,
            accept_datetime=accept_datetime,
            fields=fields,
            **kwargs
        )
        return _to_list(paged)

    def set_configuration_setting(self, configuration_setting, **kwargs):
        return get_event_loop().run_until_complete(
            self.obj.set_configuration_setting(configuration_setting, **kwargs)
        )

    def set_read_only(self, configuration_setting, read_only=True, **kwargs):
        return get_event_loop().run_until_complete(
            self.obj.set_read_only(configuration_setting, read_only, **kwargs)
        )
