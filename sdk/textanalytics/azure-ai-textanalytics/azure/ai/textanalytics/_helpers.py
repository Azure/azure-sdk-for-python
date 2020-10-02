
def _get_deserialize():
    from ._generated.v3_2_preview_1 import TextAnalyticsClient
    return TextAnalyticsClient("dummy", "dummy")._deserialize  # pylint: disable=protected-access