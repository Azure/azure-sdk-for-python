# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: utility.py

DESCRIPTION:
    The utils script provides the help functions to handling common scenario.

USAGE:
    These functions are rarely used alone, but are referenced by other sample code in their context.
"""
import re
from html.parser import HTMLParser


class TableParser(HTMLParser):
    """
    This class inherits from HtmlParse and provides the ability to analyze HTML table content data.
    """

    def __init__(self):
        super().__init__()
        self.in_table = False
        self.in_row = False
        self.in_cell = False
        self.current_row = []
        self.table = []

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self.in_table = True
        elif tag == "tr" and self.in_table:
            self.in_row = True
            self.current_row = []
        elif tag in ["td", "th"] and self.in_row:
            self.in_cell = True

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table = False
        elif tag == "tr" and self.in_row:
            self.in_row = False
            self.table.append(self.current_row)
        elif tag in ["td", "th"] and self.in_cell:
            self.in_cell = False

    def handle_data(self, data):
        if self.in_cell:
            self.current_row.append(data.strip())


def html_table_to_markdown(html_table_str):
    """
    Convert HTML table in string format to markdown format for output.

    Args:
        html_table_str: the string of html table.
    Return:
        the string of table in markdown format.
    """
    table_parser = TableParser()
    table_parser.feed(html_table_str)

    if not table_parser.table:
        print("No table found in the HTML.")
        return html_table_str

    markdown_table = []
    headers = table_parser.table[0]
    markdown_table.append("| " + " | ".join(headers) + " |")
    markdown_table.append("| " + " | ".join(["---"] * len(headers)) + " |")

    for row in table_parser.table[1:]:
        markdown_table.append("| " + " | ".join(row) + " |")

    table_parser.close()

    return "\n".join(markdown_table)


def correct_tables_from_html_to_markdown(content):
    """
    In mixed string, convert the HTML table characters to markdown tables, and keep other contents unchanged.

    Args:
        content: mix string about Html and Markdown.

    Return:
        The parsed markdown characters.
    """
    table_start_pattern = r"<table>"
    table_end_pattern = r"</table>"
    start_positions = [m.start() for m in re.finditer(table_start_pattern, content)]
    end_positions = [m.end() for m in re.finditer(table_end_pattern, content)]

    if len(start_positions) == len(end_positions):
        parsedContent = ""
        handled_index = 0
        for index, start_pos in enumerate(start_positions):
            end_pos = end_positions[index]
            html_table = content[start_pos:end_pos]

            markdown_table = html_table_to_markdown(html_table)
            parsedContent += content[handled_index:start_pos] + markdown_table
            handled_index = end_pos

        parsedContent += content[handled_index:]
        return parsedContent
    else:
        print("May there's layout issue about html table in result content.")
        print("Check the result content please")
        return content
