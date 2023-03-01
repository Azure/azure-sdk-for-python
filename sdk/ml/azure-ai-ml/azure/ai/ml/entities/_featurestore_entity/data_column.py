from .data_column_type import DataColumnType

from azure.ai.ml._utils._experimental import experimental


@experimental
class DataColumn(object):
    """A dataframe column
    :param name: The column name
    :type name: str, required
    :param type: Column data type
    :type type: str, one of [string, integer, long, float, double, binary, datetime], optional"""

    def __init__(self, *, name: str, type: DataColumnType = None, **kwargs):
        self.name = name
        self.type = type
