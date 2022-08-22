# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from collections import OrderedDict
from datetime import datetime, timedelta

import six

if six.PY3:
    from html import escape
else:
    from cgi import escape

SUPPORTED_VALUE_TYPE_TUPLE = (int, float, str, datetime, timedelta)
TABLE_FMT = '<table style="width:100%">{0}</table>'
ROW_FMT = "<tr>{0}</tr>"
HEADER_FMT = "<th>{0}</th>"
DATA_FMT = "<td>{0}</td>"
# target="_blank" opens in new tab, rel="noopener" is for perf + security
LINK_FMT = '<a href="{0}" target="_blank" rel="noopener">{1}</a>'


def convert_dict_to_table(object_to_convert):
    # Case 1: All non-collection values -> table of 1 row
    # Case 2: All collection values, lens eq N -> assert lengths eq, table of N rows
    # Case 3: collection and non-collection values -> table of 1 row, collections nest
    # Case 4: All collection values, lens unequal -> table of 1 row, each is nested collection?

    if not isinstance(object_to_convert, dict):
        raise AssertionError("Expected a dict or subclass, got {0}".format(type(object_to_convert)))

    if len(object_to_convert) == 0:
        return ""

    ordered_obj = OrderedDict(object_to_convert)

    def is_collection_type(val):
        return hasattr(val, "__len__") and not isinstance(val, str)

    is_collection = [is_collection_type(value) for value in ordered_obj.values()]

    all_rows = [get_header_row_string(ordered_obj.keys())]

    def values_to_data_row(values):
        cells = [to_html(value) for value in values]
        return get_data_row_string(cells)

    if all(is_collection):
        # Cases 2 and 4
        length = len(ordered_obj.values[0])
        if any([len(v) != length for v in ordered_obj.values()]):
            # Case 4
            logging.warn("Uneven column lengths in table conversion")
            all_rows.append(values_to_data_row(ordered_obj.values()))

        else:
            # Case 2 - sad transpose
            for i in range(length):
                value_list = [val[i] for val in ordered_obj.values()]
                all_rows.append(values_to_data_row(value_list))

    else:
        # Cases 1 and 3
        # Table of 1 row of values or mixed types, table of 1 row
        all_rows.append(values_to_data_row(ordered_obj.values()))

    return table_from_html_rows(all_rows)


def convert_list_to_table(object_to_convert):
    if not isinstance(object_to_convert, list):
        raise AssertionError("Expected a list or subclass, got {0}".format(type(object_to_convert)))

    if len(object_to_convert) == 0:
        return ""

    all_values = [to_html(element) for element in object_to_convert]
    all_rows = [get_data_row_string([element]) for element in all_values]
    return table_from_html_rows(all_rows)


# Mapping from complex type to HTML converters
# Unspecified types default to convert_value
_type_to_converter = {list: convert_list_to_table, dict: convert_dict_to_table}


def to_html(object_to_convert):
    candidate_converters = [k for k in _type_to_converter.keys() if isinstance(object_to_convert, k)]

    if len(candidate_converters) == 0:
        converter = convert_value
    elif len(candidate_converters) == 1:
        converter = _type_to_converter[candidate_converters[0]]
    else:
        logging.warn("Multiple candidate converters found for type {0}".format(type(object_to_convert)))
        converter = convert_value

    converted_value = converter(object_to_convert)
    return converted_value


def is_string_link(string):
    # type: (str) -> bool
    return isinstance(string, six.text_type) and string.strip().lower().startswith("http")


def make_link(link_string, link_text=None):
    # type: (str) -> str
    if not link_text:  # Actually want truthy string
        link_text = "Link"
    return LINK_FMT.format(escape(link_string), link_text)


def convert_value(value):
    # type: (...) -> str
    if value is None:
        return ""
    if is_string_link(value):
        return make_link(value)
    if not isinstance(value, SUPPORTED_VALUE_TYPE_TUPLE):
        logging.warn("Unsupported type %s for html, converting", type(value))

    # TODO: Figure out a good escaping story here right now it breaks existing tags
    return str(value)


def get_header_row_string(column_headers):
    headers = [HEADER_FMT.format(header) for header in column_headers]
    return ROW_FMT.format("".join(headers))


def get_data_row_string(data_values):
    data = [DATA_FMT.format(datum) for datum in data_values]
    return ROW_FMT.format("".join(data))


def table_from_html_rows(list_of_rows):
    # type/: (List[str]) -> str
    return TABLE_FMT.format("".join(list_of_rows))


def to_formatted_html_table(rows, header):
    html = ["""<table style="width:100%; border:2px solid black" >"""]
    if header is not None:
        html_row = "</td><td>".join(column for column in header)
        html.append(
            """<tr style="font-weight:bold; border-bottom:1pt solid black; border-right: 1pt solid black;
                    text-align: center"><td>{}</td></tr>""".format(
                html_row
            )
        )

    for row in rows:
        html_row = "</td><td>".join(str(value) for value in row)
        html.append(
            """<tr style="width:100%; word-wrap: break-word; border-bottom:1pt solid black;
                    text-align: center"><td>{}</td></tr>""".format(
                html_row
            )
        )
    html.append("</table>")
    return "".join(html)
