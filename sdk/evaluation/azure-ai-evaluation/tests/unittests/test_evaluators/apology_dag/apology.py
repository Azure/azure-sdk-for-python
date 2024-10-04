import re

from promptflow.core import tool


@tool
def apology(response):
    return len(re.findall("(sorry)|(apology)|(apologies)", response.lower()))
