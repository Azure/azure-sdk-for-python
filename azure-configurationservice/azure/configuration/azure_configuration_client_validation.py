def validate_get_configuration_setting(key):
    if key is None:
        raise ValueError("key is mandatory to get a ConfigurationSetting object")


def validate_add_configuration_setting(configuration_setting, **kwargs):
    if configuration_setting is None:
        raise ValueError("Object configuration_setting can not be None")
    key = configuration_setting.key
    if key is None:
        raise ValueError("key is mandatory to add a new ConfigurationSetting object")
    custom_headers = kwargs.get("headers")
    if_none_match = {"If-None-Match": '"*"'}
    if custom_headers is None:
        custom_headers = if_none_match
    elif custom_headers.get("If-None-Match", '"*"') == '"*"':
        custom_headers.update(if_none_match)
    return custom_headers


def validate_update_configuration_setting(
    key,
    etag=None,
    **kwargs
):
    if key is None:
        raise ValueError("key is mandatory to update a ConfigurationSetting")
    custom_headers = kwargs.get("headers")
    if etag is not None:
        if_match = {"If-Match": '"' + etag + '"'}
    else:
        if_match = {"If-Match": '"*"'}
    if custom_headers is None:
        custom_headers = if_match
    elif custom_headers.get("If-Match", '"*"') == '"*"':
        custom_headers.update(if_match)

    return custom_headers


def validate_set_configuration_setting(configuration_setting, **kwargs):
    if configuration_setting is None:
        raise ValueError("Object configuration_setting can not be None")
    key = configuration_setting.key
    if key is None:
        raise ValueError("key is mandatory to set a new ConfigurationSetting object")
    custom_headers = kwargs.get("headers")
    etag = configuration_setting.etag
    if etag is not None:
        if_match = {"If-Match": '"' + etag + '"'}
        if custom_headers is None:
            custom_headers = if_match
        else:
            custom_headers.update(if_match)
    return custom_headers


def validate_delete_configuration_setting(key, etag=None, **kwargs):
    if key is None:
        raise ValueError("key is mandatory to delete a ConfigurationSetting object")
    custom_headers = kwargs.get("headers")
    if etag is not None:
        if_match = {"If-Match": '"' + etag + '"'}
        if custom_headers is None:
            custom_headers = if_match
        else:
            custom_headers.update(if_match)
    return custom_headers


def validate_lock_configuration_setting(key):
    if key is None:
        raise ValueError("key is mandatory to lock a ConfigurationSetting object")


def validate_unlock_configuration_setting(key):
    if key is None:
        raise ValueError("key is mandatory to unlock a ConfigurationSetting object")

