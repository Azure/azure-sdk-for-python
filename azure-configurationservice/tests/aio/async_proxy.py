from asyncio import *
from azure.configuration.aio import AzureConfigurationClient


def _to_list(ait):
    async def lst():
        result = []
        async for item in ait:
            result.append(item)
        return result
    return get_event_loop().run_until_complete(lst())


class AzureConfigurationClientProxy(object):
    def __init__(self, connection_str):
        self.obj = AzureConfigurationClient(connection_str)

    def get_configuration_setting(
        self, key, label=None, accept_date_time=None, **kwargs
    ):
        return get_event_loop().run_until_complete(
            self.obj.get_configuration_setting(
                key, label=label, accept_date_time=accept_date_time, **kwargs
            )
        )

    def add_configuration_setting(self, configuration_setting, **kwargs):
        return get_event_loop().run_until_complete(
            self.obj.add_configuration_setting(
                configuration_setting, **kwargs
            )
        )

    def delete_configuration_setting(self, key, label=None, etag=None, **kwargs):
        return get_event_loop().run_until_complete(
            self.obj.delete_configuration_setting(
                key, label=label, etag=etag, **kwargs
            )
        )

    def list_configuration_settings(
            self, labels=None, keys=None, accept_date_time=None, fields=None, **kwargs
    ):
        paged = self.obj.list_configuration_settings(
            labels=labels, keys=keys, accept_date_time=accept_date_time, fields=fields, **kwargs
        )
        return _to_list(paged)

    def list_revisions(
            self, labels=None, keys=None, accept_date_time=None, fields=None, **kwargs
    ):
        paged = self.obj.list_revisions(
            labels=labels, keys=keys, accept_date_time=accept_date_time, fields=fields, **kwargs
        )
        return _to_list(paged)

    def update_configuration_setting(
        self,
        key,
        value=None,
        content_type=None,
        tags=None,
        label=None,
        etag=None,
        **kwargs
    ):
        return get_event_loop().run_until_complete(
            self.obj.update_configuration_setting(
                key, value=value, content_type=content_type, tags=tags, label=label, etag=etag, **kwargs
            )
        )

    def set_configuration_setting(self, configuration_setting, **kwargs):
        return get_event_loop().run_until_complete(
            self.obj.set_configuration_setting(
                configuration_setting, **kwargs
            )
        )

    def lock_configuration_setting(self, key, label=None, **kwargs):
        return get_event_loop().run_until_complete(
            self.obj.lock_configuration_setting(
                key, label=label, **kwargs
            )
        )

    def unlock_configuration_setting(self, key, label=None, **kwargs):
        return get_event_loop().run_until_complete(
            self.obj.unlock_configuration_setting(
                key, label=label, **kwargs
            )
        )
