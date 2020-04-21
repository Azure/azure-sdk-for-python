# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import pytest
from azure.ai.formrecognizer._helpers import get_content_type
from testcase import FormRecognizerTest


class TestContentType(FormRecognizerTest):

    def test_pdf(self):
        with open(self.invoice_pdf, "rb") as fd:
            content_type = get_content_type(fd)
        self.assertEqual(content_type, "application/pdf")

    def test_pdf_bytes(self):
        with open(self.invoice_pdf, "rb") as fd:
            myfile = fd.read()
        content_type = get_content_type(myfile)
        self.assertEqual(content_type, "application/pdf")

    def test_jpg(self):
        with open(self.form_jpg, "rb") as fd:
            content_type = get_content_type(fd)
        self.assertEqual(content_type, "image/jpeg")

    def test_jpg_bytes(self):
        with open(self.form_jpg, "rb") as fd:
            myfile = fd.read()
        content_type = get_content_type(myfile)
        self.assertEqual(content_type, "image/jpeg")

    def test_png(self):
        with open(self.receipt_png, "rb") as fd:
            content_type = get_content_type(fd)
        self.assertEqual(content_type, "image/png")

    def test_png_bytes(self):
        with open(self.receipt_png, "rb") as fd:
            myfile = fd.read()
        content_type = get_content_type(myfile)
        self.assertEqual(content_type, "image/png")

    def test_tiff(self):
        with open(self.invoice_tiff, "rb") as fd:
            content_type = get_content_type(fd)
        self.assertEqual(content_type, "image/tiff")

    def test_tiff_bytes(self):
        with open(self.invoice_tiff, "rb") as fd:
            myfile = fd.read()
        content_type = get_content_type(myfile)
        self.assertEqual(content_type, "image/tiff")
