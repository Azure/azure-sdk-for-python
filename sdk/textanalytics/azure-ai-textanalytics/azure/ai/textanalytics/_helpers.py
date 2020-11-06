
def _get_deserialize():
    from ._generated.v3_1_preview_3 import TextAnalyticsClient
    return TextAnalyticsClient("dummy", "dummy")._deserialize  # pylint: disable=protected-access
    