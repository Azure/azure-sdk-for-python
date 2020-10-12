class ConfigurationSetting(object):
    """A configuration value.

    :param str key: The key name of the setting.
    :param str value: The value of the setting.
    :keyword str label: The setting label.
    :ivar str etag: Entity tag (etag) of the setting.
    :ivar  ~datetime.datetime last_modified: The time the setting was last modified.
    :ivar bool read_only: Whether the setting is read-only.
    :ivar str content_type: The content type of the setting value.
    :ivar dict[str, str] tags: User tags added to the setting.
    """

    def __init__(self, key, value, **kwargs):
        # type: (str, str, Any) -> None
        pass
    
    def __repr__(self):
        # type: () -> str
        pass
    
    def __getitem__(self, *args):
        # type: (Any) -> Any
        pass
    
    def __contains__(self, *args):
        # type: (Any) -> Any
        pass
    
    ...