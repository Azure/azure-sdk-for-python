# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

POLLING_INTERVAL = 5
COGNITIVE_KEY_HEADER = "Ocp-Apim-Subscription-Key"


def get_content_type(form):
    """Source: https://en.wikipedia.org/wiki/Magic_number_(programming)#Magic_numbers_in_files
    """

    if hasattr(form, "read"):
        form = form.read(4)

    if len(form) > 3:
        if form[:4] == b"\x25\x50\x44\x46":
            return "application/pdf"
        if form[:2] == b"\xff\xd8":
            return "image/jpeg"
        if form[:4] == b"\x89\x50\x4E\x47":
            return "image/png"
        if form[:4] == b"\x49\x49\x2A\x00":  # little-endian
            return "image/tiff"
        if form[:4] == b"\x4D\x4D\x00\x2A":  # big-endian
            return "image/tiff"
    raise ValueError("Content type could not be auto-detected. Please pass the content_type keyword argument.")
