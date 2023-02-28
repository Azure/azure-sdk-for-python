
from enum import Enum


class DataColumnType(Enum):
    string = 1
    integer = 2
    long = 3
    float = 4
    double = 5
    binary = 6
    datetime = 7
    bool = 8