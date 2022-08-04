# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.ai.formrecognizer import _models
from testcase import FormRecognizerTest


class TestToDict(FormRecognizerTest):
    def test_bounding_region_to_dict(self):
        model = _models.BoundingRegion(
            polygon=[_models.Point(1, 2), _models.Point(3, 4)], page_number=1
        )
        # d = [p.to_dict() for p in model]
        d = model.to_dict()
        final = {
            "page_number": 1,
            "polygon": [
                {"x": 1, "y": 2},
                {
                    "x": 3,
                    "y": 4,
                },
            ],
        }
        assert d == final

    def test_document_span_to_dict(self):
        model = _models.DocumentSpan(
            offset=5,
            length=2,
        )

        d = model.to_dict()
        final = {
            "offset": 5,
            "length": 2,
        }
        assert d == final

    def test_address_value_to_dict(self):
        model = _models.AddressValue(
            house_number="123",
            po_box="4567",
            road="Contoso Ave",
            city="Redmond",
            state="WA",
            postal_code="98052",
            country_region="USA",
            street_address="123 Contoso Ave",
        )

        d = model.to_dict()
        final = {
            "house_number": "123",
            "po_box": "4567",
            "road": "Contoso Ave",
            "city": "Redmond",
            "state": "WA",
            "postal_code": "98052",
            "country_region": "USA",
            "street_address": "123 Contoso Ave",
        }
        assert d == final

    def test_currency_value_to_dict(self):
        model = _models.CurrencyValue(
            amount=5.01,
            symbol="$",
        )

        d = model.to_dict()
        final = {
            "amount": 5.01,
            "symbol": "$",
        }
        assert d == final

    def test_document_content_element_to_dict(self):
        model = _models.DocumentContentElement(
            content="sample",
            polygon=[
                _models.Point(1427.0, 1669.0),
                _models.Point(1527.0, 1669.0),
                _models.Point(1527.0, 1698.0),
                _models.Point(1427.0, 1698.0),
            ],
            span=_models.DocumentSpan(
                offset=5,
                length=2,
            ),
            kind="word",
            confidence=0.99,
        )

        d = model.to_dict()
        final = {
            "content": "sample",
            "polygon": [
                {"x": 1427.0, "y": 1669.0},
                {"x": 1527.0, "y": 1669.0},
                {"x": 1527.0, "y": 1698.0},
                {"x": 1427.0, "y": 1698.0},
            ],
            "span": {
                "offset": 5,
                "length": 2,
            },
            "confidence": 0.99,
            "kind": "word",
        }
        assert d == final

    def test_analyzed_document_to_dict(self):
        model = _models.AnalyzedDocument(
            doc_type="test:doc",
            bounding_regions=[
                _models.BoundingRegion(
                    polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                    page_number=1,
                ),
                _models.BoundingRegion(
                    polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                    page_number=1,
                ),
            ],
            spans=[
                _models.DocumentSpan(
                    offset=5,
                    length=2,
                ),
                _models.DocumentSpan(
                    offset=5,
                    length=2,
                ),
            ],
            fields={
                "sample": _models.DocumentField(
                    value_type="number",
                    value=0.1,
                    content="0.1",
                    bounding_regions=[
                        _models.BoundingRegion(
                            polygon=[
                                _models.Point(1, 2),
                                _models.Point(3, 4),
                            ],
                            page_number=1,
                        ),
                        _models.BoundingRegion(
                            polygon=[
                                _models.Point(1, 2),
                                _models.Point(3, 4),
                            ],
                            page_number=1,
                        ),
                    ],
                    spans=[
                        _models.DocumentSpan(
                            offset=5,
                            length=2,
                        ),
                        _models.DocumentSpan(
                            offset=5,
                            length=2,
                        ),
                    ],
                    confidence=0.99,
                ),
            },
            confidence=0.99,
        )

        d = model.to_dict()

        final = {
            "doc_type": "test:doc",
            "bounding_regions": [
                {
                    "page_number": 1,
                    "polygon": [
                        {"x": 1, "y": 2},
                        {
                            "x": 3,
                            "y": 4,
                        },
                    ],
                },
                {
                    "page_number": 1,
                    "polygon": [
                        {"x": 1, "y": 2},
                        {
                            "x": 3,
                            "y": 4,
                        },
                    ],
                },
            ],
            "spans": [
                {
                    "offset": 5,
                    "length": 2,
                },
                {
                    "offset": 5,
                    "length": 2,
                },
            ],
            "fields": {
                "sample": {
                    "value_type": "number",
                    "value": 0.1,
                    "content": "0.1",
                    "bounding_regions": [
                        {
                            "page_number": 1,
                            "polygon": [
                                {"x": 1, "y": 2},
                                {
                                    "x": 3,
                                    "y": 4,
                                },
                            ],
                        },
                        {
                            "page_number": 1,
                            "polygon": [
                                {"x": 1, "y": 2},
                                {
                                    "x": 3,
                                    "y": 4,
                                },
                            ],
                        },
                    ],
                    "spans": [
                        {
                            "offset": 5,
                            "length": 2,
                        },
                        {
                            "offset": 5,
                            "length": 2,
                        },
                    ],
                    "confidence": 0.99,
                },
            },
            "confidence": 0.99,
        }

        assert d == final

    def test_document_field_to_dict(self):
        model = _models.DocumentField(
            value_type="number",
            value=0.1,
            content="0.1",
            bounding_regions=[
                _models.BoundingRegion(
                    polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                    page_number=1,
                ),
                _models.BoundingRegion(
                    polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                    page_number=1,
                ),
            ],
            spans=[
                _models.DocumentSpan(
                    offset=5,
                    length=2,
                ),
                _models.DocumentSpan(
                    offset=5,
                    length=2,
                ),
            ],
            confidence=0.99,
        )

        d = model.to_dict()

        final = {
            "value_type": "number",
            "value": 0.1,
            "content": "0.1",
            "bounding_regions": [
                {
                    "page_number": 1,
                    "polygon": [
                        {"x": 1, "y": 2},
                        {
                            "x": 3,
                            "y": 4,
                        },
                    ],
                },
                {
                    "page_number": 1,
                    "polygon": [
                        {"x": 1, "y": 2},
                        {
                            "x": 3,
                            "y": 4,
                        },
                    ],
                },
            ],
            "spans": [
                {
                    "offset": 5,
                    "length": 2,
                },
                {
                    "offset": 5,
                    "length": 2,
                },
            ],
            "confidence": 0.99,
        }
        assert d == final

    def test_document_key_value_element_to_dict(self):
        model = _models.DocumentKeyValueElement(
            content="content",
            bounding_regions=[
                _models.BoundingRegion(
                    polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                    page_number=1,
                ),
                _models.BoundingRegion(
                    polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                    page_number=1,
                ),
            ],
            spans=[
                _models.DocumentSpan(
                    offset=5,
                    length=2,
                ),
                _models.DocumentSpan(
                    offset=5,
                    length=2,
                ),
            ],
        )

        d = model.to_dict()

        final = {
            "content": "content",
            "bounding_regions": [
                {
                    "page_number": 1,
                    "polygon": [
                        {"x": 1, "y": 2},
                        {
                            "x": 3,
                            "y": 4,
                        },
                    ],
                },
                {
                    "page_number": 1,
                    "polygon": [
                        {"x": 1, "y": 2},
                        {
                            "x": 3,
                            "y": 4,
                        },
                    ],
                },
            ],
            "spans": [
                {
                    "offset": 5,
                    "length": 2,
                },
                {
                    "offset": 5,
                    "length": 2,
                },
            ],
        }

        assert d == final

    def test_document_key_value_pair_to_dict(self):
        model = _models.DocumentKeyValuePair(
            key=_models.DocumentKeyValueElement(
                content="key",
                bounding_regions=[
                    _models.BoundingRegion(
                        polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                        page_number=1,
                    ),
                ],
                spans=[
                    _models.DocumentSpan(
                        offset=5,
                        length=2,
                    ),
                ],
            ),
            value=_models.DocumentKeyValueElement(
                content="value",
                bounding_regions=[
                    _models.BoundingRegion(
                        polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                        page_number=1,
                    ),
                ],
                spans=[
                    _models.DocumentSpan(
                        offset=5,
                        length=2,
                    ),
                ],
            ),
            confidence=0.89,
        )

        d = model.to_dict()

        final = {
            "key": {
                "content": "key",
                "bounding_regions": [
                    {
                        "page_number": 1,
                        "polygon": [
                            {"x": 1, "y": 2},
                            {
                                "x": 3,
                                "y": 4,
                            },
                        ],
                    },
                ],
                "spans": [
                    {
                        "offset": 5,
                        "length": 2,
                    },
                ],
            },
            "value": {
                "content": "value",
                "bounding_regions": [
                    {
                        "page_number": 1,
                        "polygon": [
                            {"x": 1, "y": 2},
                            {
                                "x": 3,
                                "y": 4,
                            },
                        ],
                    },
                ],
                "spans": [
                    {
                        "offset": 5,
                        "length": 2,
                    },
                ],
            },
            "confidence": 0.89,
        }

        assert d == final

    def test_document_line_to_dict(self):
        model = _models.DocumentLine(
            content="sample line",
            polygon=[
                _models.Point(1427.0, 1669.0),
                _models.Point(1527.0, 1669.0),
                _models.Point(1527.0, 1698.0),
                _models.Point(1427.0, 1698.0),
            ],
            spans=[
                _models.DocumentSpan(
                    offset=5,
                    length=2,
                ),
            ],
        )

        d = model.to_dict()
        final = {
            "content": "sample line",
            "polygon": [
                {"x": 1427.0, "y": 1669.0},
                {"x": 1527.0, "y": 1669.0},
                {"x": 1527.0, "y": 1698.0},
                {"x": 1427.0, "y": 1698.0},
            ],
            "spans": [
                {
                    "offset": 5,
                    "length": 2,
                },
            ],
        }
        assert d == final

    def test_document_page_to_dict(self):
        model = _models.DocumentPage(
            kind="document",
            page_number=1,
            angle=180.0,
            width=8.5,
            height=11.0,
            unit="inch",
            spans=[
                _models.DocumentSpan(
                    offset=5,
                    length=2,
                ),
            ],
            words=[
                _models.DocumentWord(
                    content="example",
                    polygon=[
                        _models.Point(1427.0, 1669.0),
                        _models.Point(1527.0, 1669.0),
                        _models.Point(1527.0, 1698.0),
                        _models.Point(1427.0, 1698.0),
                    ],
                    span=_models.DocumentSpan(
                        offset=5,
                        length=2,
                    ),
                    confidence=0.62,
                ),
            ],
            selection_marks=[
                _models.DocumentSelectionMark(
                    state="unselected",
                    polygon=[
                        _models.Point(1427.0, 1669.0),
                        _models.Point(1527.0, 1669.0),
                        _models.Point(1527.0, 1698.0),
                        _models.Point(1427.0, 1698.0),
                    ],
                    span=_models.DocumentSpan(
                        offset=5,
                        length=2,
                    ),
                    confidence=1.0,
                ),
            ],
            lines=[
                _models.DocumentLine(
                    content="sample line",
                    polygon=[
                        _models.Point(1427.0, 1669.0),
                        _models.Point(1527.0, 1669.0),
                        _models.Point(1527.0, 1698.0),
                        _models.Point(1427.0, 1698.0),
                    ],
                    spans=[
                        _models.DocumentSpan(
                            offset=5,
                            length=2,
                        ),
                    ],
                ),
            ],
        )

        d = model.to_dict()

        final = {
            "kind": "document",
            "page_number": 1,
            "angle": 180.0,
            "width": 8.5,
            "height": 11.0,
            "unit": "inch",
            "spans": [
                {
                    "offset": 5,
                    "length": 2,
                },
            ],
            "words": [
                {
                    "content": "example",
                    "polygon": [
                        {"x": 1427.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1698.0},
                        {"x": 1427.0, "y": 1698.0},
                    ],
                    "span": {
                        "offset": 5,
                        "length": 2,
                    },
                    "confidence": 0.62,
                    "kind": "word",
                },
            ],
            "selection_marks": [
                {
                    "content": None,
                    "state": "unselected",
                    "polygon": [
                        {"x": 1427.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1698.0},
                        {"x": 1427.0, "y": 1698.0},
                    ],
                    "span": {
                        "offset": 5,
                        "length": 2,
                    },
                    "kind": "selectionMark",
                    "confidence": 1.0,
                },
            ],
            "lines": [
                {
                    "content": "sample line",
                    "polygon": [
                        {"x": 1427.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1698.0},
                        {"x": 1427.0, "y": 1698.0},
                    ],
                    "spans": [
                        {
                            "offset": 5,
                            "length": 2,
                        },
                    ],
                },
            ],
        }

        assert d == final

    def test_document_selection_mark_to_dict(self):
        model = _models.DocumentSelectionMark(
            state="unselected",
            polygon=[
                _models.Point(1427.0, 1669.0),
                _models.Point(1527.0, 1669.0),
                _models.Point(1527.0, 1698.0),
                _models.Point(1427.0, 1698.0),
            ],
            span=_models.DocumentSpan(
                offset=5,
                length=2,
            ),
            confidence=1.0,
        )

        d = model.to_dict()

        final = {
            "content": None,
            "state": "unselected",
            "polygon": [
                {"x": 1427.0, "y": 1669.0},
                {"x": 1527.0, "y": 1669.0},
                {"x": 1527.0, "y": 1698.0},
                {"x": 1427.0, "y": 1698.0},
            ],
            "span": {
                "offset": 5,
                "length": 2,
            },
            "kind": "selectionMark",
            "confidence": 1.0,
        }

        assert d == final

    def test_document_style_to_dict(self):
        model = _models.DocumentStyle(
            is_handwritten=True,
            spans=[
                _models.DocumentSpan(
                    offset=5,
                    length=2,
                ),
            ],
            confidence=1.0,
        )

        d = model.to_dict()

        final = {
            "is_handwritten": True,
            "spans": [
                {
                    "offset": 5,
                    "length": 2,
                }
            ],
            "confidence": 1.0,
        }

        assert d == final

    def test_document_table_to_dict(self):
        model = _models.DocumentTable(
            row_count=3,
            column_count=2,
            cells=[
                _models.DocumentTableCell(
                    kind="content",
                    row_index=2,
                    column_index=3,
                    row_span=1,
                    column_span=1,
                    content="cell content",
                    bounding_regions=[
                        _models.BoundingRegion(
                            polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                            page_number=1,
                        ),
                    ],
                    spans=[
                        _models.DocumentSpan(
                            offset=5,
                            length=2,
                        ),
                    ],
                ),
            ],
            bounding_regions=[
                _models.BoundingRegion(
                    polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                    page_number=1,
                ),
            ],
            spans=[
                _models.DocumentSpan(
                    offset=5,
                    length=2,
                ),
            ],
        )

        d = model.to_dict()

        final = {
            "row_count": 3,
            "column_count": 2,
            "cells": [
                {
                    "kind": "content",
                    "row_index": 2,
                    "column_index": 3,
                    "row_span": 1,
                    "column_span": 1,
                    "content": "cell content",
                    "bounding_regions": [
                        {
                            "page_number": 1,
                            "polygon": [
                                {"x": 1, "y": 2},
                                {
                                    "x": 3,
                                    "y": 4,
                                },
                            ],
                        },
                    ],
                    "spans": [
                        {
                            "offset": 5,
                            "length": 2,
                        },
                    ],
                },
            ],
            "bounding_regions": [
                {
                    "page_number": 1,
                    "polygon": [
                        {"x": 1, "y": 2},
                        {
                            "x": 3,
                            "y": 4,
                        },
                    ],
                },
            ],
            "spans": [
                {
                    "offset": 5,
                    "length": 2,
                },
            ],
        }

        assert d == final

    def test_document_table_cell_to_dict(self):
        model = _models.DocumentTableCell(
            kind="content",
            row_index=2,
            column_index=3,
            row_span=1,
            column_span=1,
            content="cell content",
            bounding_regions=[
                _models.BoundingRegion(
                    polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                    page_number=1,
                ),
            ],
            spans=[
                _models.DocumentSpan(
                    offset=5,
                    length=2,
                ),
            ],
        )

        d = model.to_dict()

        final = {
            "kind": "content",
            "row_index": 2,
            "column_index": 3,
            "row_span": 1,
            "column_span": 1,
            "content": "cell content",
            "bounding_regions": [
                {
                    "page_number": 1,
                    "polygon": [
                        {"x": 1, "y": 2},
                        {
                            "x": 3,
                            "y": 4,
                        },
                    ],
                },
            ],
            "spans": [
                {
                    "offset": 5,
                    "length": 2,
                },
            ],
        }

        assert d == final

    def test_document_table_cell_to_dict_use_defaults(self):
        # NOTE: kind, column_span, and row_span are not included on purpose to test that the proper defaults are set.
        model = _models.DocumentTableCell(
            row_index=2,
            column_index=3,
            content="cell content",
            bounding_regions=[
                _models.BoundingRegion(
                    polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                    page_number=1,
                ),
            ],
            spans=[
                _models.DocumentSpan(
                    offset=5,
                    length=2,
                ),
            ],
        )

        d = model.to_dict()

        final = {
            "kind": "content",
            "row_index": 2,
            "column_index": 3,
            "row_span": 1,
            "column_span": 1,
            "content": "cell content",
            "bounding_regions": [
                {
                    "page_number": 1,
                    "polygon": [
                        {"x": 1, "y": 2},
                        {
                            "x": 3,
                            "y": 4,
                        },
                    ],
                },
            ],
            "spans": [
                {
                    "offset": 5,
                    "length": 2,
                },
            ],
        }

        assert d == final

    def test_model_operation_info_to_dict(self):
        model = _models.DocumentModelOperationSummary(
            operation_id="id123",
            status="succeeded",
            percent_completed=100,
            created_on="1994-11-05T13:15:30Z",
            last_updated_on="1994-11-05T13:20:30Z",
            kind="documentModelBuild",
            resource_location="https://contoso.com/resource",
            api_version="2022-06-30-preview",
            tags={"test": "value"},
        )

        d = model.to_dict()

        final = {
            "operation_id": "id123",
            "status": "succeeded",
            "percent_completed": 100,
            "created_on": "1994-11-05T13:15:30Z",  # TODO should this field be switched to a datetime?
            "last_updated_on": "1994-11-05T13:20:30Z",
            "kind": "documentModelBuild",
            "resource_location": "https://contoso.com/resource",
            "api_version": "2022-06-30-preview",
            "tags": {"test": "value"},
        }

        assert d == final

    def test_document_word_to_dict(self):
        model = _models.DocumentWord(
            content="example",
            polygon=[
                _models.Point(1427.0, 1669.0),
                _models.Point(1527.0, 1669.0),
                _models.Point(1527.0, 1698.0),
                _models.Point(1427.0, 1698.0),
            ],
            span=_models.DocumentSpan(
                offset=5,
                length=2,
            ),
            confidence=0.62,
        )

        d = model.to_dict()

        final = {
            "content": "example",
            "polygon": [
                {"x": 1427.0, "y": 1669.0},
                {"x": 1527.0, "y": 1669.0},
                {"x": 1527.0, "y": 1698.0},
                {"x": 1427.0, "y": 1698.0},
            ],
            "span": {
                "offset": 5,
                "length": 2,
            },
            "confidence": 0.62,
            "kind": "word",
        }

        assert d == final

    def test_analyze_result_to_dict(self):
        model = _models.AnalyzeResult(
            api_version="2021-07-30-preview",
            model_id="modelId1",
            content="Sample\nFile content.",
            languages=[
                _models.DocumentLanguage(
                    locale="en",
                    spans=[
                        _models.DocumentSpan(offset=5, length=2),
                    ],
                    confidence=0.99,
                ),
            ],
            paragraphs=[
                _models.DocumentParagraph(
                    role="pageNumber",
                    content="a paragraph",
                    bounding_regions=[
                        _models.BoundingRegion(
                            polygon=[
                                _models.Point(1, 2),
                                _models.Point(3, 4),
                            ],
                            page_number=1,
                        ),
                    ],
                    spans=[
                        _models.DocumentSpan(offset=5, length=2),
                    ],
                )
            ],
            pages=[
                _models.DocumentPage(
                    kind="document",
                    page_number=1,
                    angle=180.0,
                    width=8.5,
                    height=11.0,
                    unit="inch",
                    spans=[
                        _models.DocumentSpan(offset=5, length=2),
                    ],
                    words=[
                        _models.DocumentWord(
                            content="example",
                            polygon=[
                                _models.Point(1427.0, 1669.0),
                                _models.Point(1527.0, 1669.0),
                                _models.Point(1527.0, 1698.0),
                                _models.Point(1427.0, 1698.0),
                            ],
                            span=_models.DocumentSpan(offset=5, length=2),
                            confidence=0.62,
                        ),
                    ],
                    selection_marks=[
                        _models.DocumentSelectionMark(
                            state="unselected",
                            polygon=[
                                _models.Point(1427.0, 1669.0),
                                _models.Point(1527.0, 1669.0),
                                _models.Point(1527.0, 1698.0),
                                _models.Point(1427.0, 1698.0),
                            ],
                            span=_models.DocumentSpan(offset=5, length=2),
                            confidence=1.0,
                        ),
                    ],
                    lines=[
                        _models.DocumentLine(
                            content="sample line",
                            polygon=[
                                _models.Point(1427.0, 1669.0),
                                _models.Point(1527.0, 1669.0),
                                _models.Point(1527.0, 1698.0),
                                _models.Point(1427.0, 1698.0),
                            ],
                            spans=[_models.DocumentSpan(offset=5, length=2)],
                        ),
                    ],
                ),
            ],
            tables=[
                _models.DocumentTable(
                    row_count=3,
                    column_count=2,
                    cells=[
                        _models.DocumentTableCell(
                            kind="content",
                            row_index=2,
                            column_index=3,
                            row_span=1,
                            column_span=1,
                            content="cell content",
                            bounding_regions=[
                                _models.BoundingRegion(
                                    polygon=[
                                        _models.Point(1, 2),
                                        _models.Point(3, 4),
                                    ],
                                    page_number=1,
                                ),
                            ],
                            spans=[_models.DocumentSpan(offset=5, length=2)],
                        ),
                    ],
                    bounding_regions=[
                        _models.BoundingRegion(
                            polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                            page_number=1,
                        ),
                    ],
                    spans=[_models.DocumentSpan(offset=5, length=2)],
                ),
            ],
            key_value_pairs=[
                _models.DocumentKeyValuePair(
                    key=_models.DocumentKeyValueElement(
                        content="key",
                        bounding_regions=[
                            _models.BoundingRegion(
                                polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                                page_number=1,
                            ),
                        ],
                        spans=[
                            _models.DocumentSpan(
                                offset=5,
                                length=2,
                            ),
                        ],
                    ),
                    value=_models.DocumentKeyValueElement(
                        content="value",
                        bounding_regions=[
                            _models.BoundingRegion(
                                polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                                page_number=1,
                            ),
                        ],
                        spans=[
                            _models.DocumentSpan(
                                offset=5,
                                length=2,
                            ),
                        ],
                    ),
                    confidence=0.89,
                ),
            ],
            styles=[
                _models.DocumentStyle(
                    is_handwritten=True,
                    spans=[
                        _models.DocumentSpan(
                            offset=5,
                            length=2,
                        ),
                    ],
                    confidence=1.0,
                ),
            ],
            documents=[
                _models.AnalyzedDocument(
                    doc_type="test:doc",
                    bounding_regions=[
                        _models.BoundingRegion(
                            polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                            page_number=1,
                        ),
                        _models.BoundingRegion(
                            polygon=[_models.Point(1, 2), _models.Point(3, 4)],
                            page_number=1,
                        ),
                    ],
                    spans=[
                        _models.DocumentSpan(
                            offset=5,
                            length=2,
                        ),
                        _models.DocumentSpan(
                            offset=5,
                            length=2,
                        ),
                    ],
                    fields={
                        "sample": _models.DocumentField(
                            value_type="number",
                            value=0.1,
                            content="0.1",
                            bounding_regions=[
                                _models.BoundingRegion(
                                    polygon=[
                                        _models.Point(1, 2),
                                        _models.Point(3, 4),
                                    ],
                                    page_number=1,
                                ),
                                _models.BoundingRegion(
                                    polygon=[
                                        _models.Point(1, 2),
                                        _models.Point(3, 4),
                                    ],
                                    page_number=1,
                                ),
                            ],
                            spans=[
                                _models.DocumentSpan(
                                    offset=5,
                                    length=2,
                                ),
                                _models.DocumentSpan(
                                    offset=5,
                                    length=2,
                                ),
                            ],
                            confidence=0.99,
                        ),
                    },
                    confidence=0.99,
                ),
            ],
        )

        d = model.to_dict()

        final = {
            "api_version": "2021-07-30-preview",
            "model_id": "modelId1",
            "content": "Sample\nFile content.",
            "languages": [
                {
                    "locale": "en",
                    "spans": [
                        {
                            "offset": 5,
                            "length": 2,
                        },
                    ],
                    "confidence": 0.99,
                }
            ],
            "pages": [
                {
                    "kind": "document",
                    "page_number": 1,
                    "angle": 180.0,
                    "width": 8.5,
                    "height": 11.0,
                    "unit": "inch",
                    "spans": [
                        {
                            "offset": 5,
                            "length": 2,
                        },
                    ],
                    "words": [
                        {
                            "content": "example",
                            "polygon": [
                                {"x": 1427.0, "y": 1669.0},
                                {"x": 1527.0, "y": 1669.0},
                                {"x": 1527.0, "y": 1698.0},
                                {"x": 1427.0, "y": 1698.0},
                            ],
                            "span": {
                                "offset": 5,
                                "length": 2,
                            },
                            "confidence": 0.62,
                            "kind": "word",
                        },
                    ],
                    "selection_marks": [
                        {
                            "content": None,
                            "state": "unselected",
                            "polygon": [
                                {"x": 1427.0, "y": 1669.0},
                                {"x": 1527.0, "y": 1669.0},
                                {"x": 1527.0, "y": 1698.0},
                                {"x": 1427.0, "y": 1698.0},
                            ],
                            "span": {
                                "offset": 5,
                                "length": 2,
                            },
                            "kind": "selectionMark",
                            "confidence": 1.0,
                        },
                    ],
                    "lines": [
                        {
                            "content": "sample line",
                            "polygon": [
                                {"x": 1427.0, "y": 1669.0},
                                {"x": 1527.0, "y": 1669.0},
                                {"x": 1527.0, "y": 1698.0},
                                {"x": 1427.0, "y": 1698.0},
                            ],
                            "spans": [
                                {
                                    "offset": 5,
                                    "length": 2,
                                },
                            ],
                        },
                    ],
                },
            ],
            "paragraphs": [
                {
                    "role": "pageNumber",
                    "content": "a paragraph",
                    "bounding_regions": [
                        {
                            "page_number": 1,
                            "polygon": [
                                {"x": 1, "y": 2},
                                {
                                    "x": 3,
                                    "y": 4,
                                },
                            ],
                        },
                    ],
                    "spans": [
                        {
                            "offset": 5,
                            "length": 2,
                        },
                    ],
                }
            ],
            "tables": [
                {
                    "row_count": 3,
                    "column_count": 2,
                    "cells": [
                        {
                            "kind": "content",
                            "row_index": 2,
                            "column_index": 3,
                            "row_span": 1,
                            "column_span": 1,
                            "content": "cell content",
                            "bounding_regions": [
                                {
                                    "page_number": 1,
                                    "polygon": [
                                        {"x": 1, "y": 2},
                                        {
                                            "x": 3,
                                            "y": 4,
                                        },
                                    ],
                                },
                            ],
                            "spans": [
                                {
                                    "offset": 5,
                                    "length": 2,
                                },
                            ],
                        },
                    ],
                    "bounding_regions": [
                        {
                            "page_number": 1,
                            "polygon": [
                                {"x": 1, "y": 2},
                                {
                                    "x": 3,
                                    "y": 4,
                                },
                            ],
                        },
                    ],
                    "spans": [
                        {
                            "offset": 5,
                            "length": 2,
                        },
                    ],
                },
            ],
            "key_value_pairs": [
                {
                    "key": {
                        "content": "key",
                        "bounding_regions": [
                            {
                                "page_number": 1,
                                "polygon": [
                                    {"x": 1, "y": 2},
                                    {
                                        "x": 3,
                                        "y": 4,
                                    },
                                ],
                            },
                        ],
                        "spans": [
                            {
                                "offset": 5,
                                "length": 2,
                            },
                        ],
                    },
                    "value": {
                        "content": "value",
                        "bounding_regions": [
                            {
                                "page_number": 1,
                                "polygon": [
                                    {"x": 1, "y": 2},
                                    {
                                        "x": 3,
                                        "y": 4,
                                    },
                                ],
                            },
                        ],
                        "spans": [
                            {
                                "offset": 5,
                                "length": 2,
                            },
                        ],
                    },
                    "confidence": 0.89,
                },
            ],
            "styles": [
                {
                    "is_handwritten": True,
                    "spans": [
                        {
                            "offset": 5,
                            "length": 2,
                        }
                    ],
                    "confidence": 1.0,
                },
            ],
            "documents": [
                {
                    "doc_type": "test:doc",
                    "bounding_regions": [
                        {
                            "page_number": 1,
                            "polygon": [
                                {"x": 1, "y": 2},
                                {
                                    "x": 3,
                                    "y": 4,
                                },
                            ],
                        },
                        {
                            "page_number": 1,
                            "polygon": [
                                {"x": 1, "y": 2},
                                {
                                    "x": 3,
                                    "y": 4,
                                },
                            ],
                        },
                    ],
                    "spans": [
                        {
                            "offset": 5,
                            "length": 2,
                        },
                        {
                            "offset": 5,
                            "length": 2,
                        },
                    ],
                    "fields": {
                        "sample": {
                            "value_type": "number",
                            "value": 0.1,
                            "content": "0.1",
                            "bounding_regions": [
                                {
                                    "page_number": 1,
                                    "polygon": [
                                        {"x": 1, "y": 2},
                                        {
                                            "x": 3,
                                            "y": 4,
                                        },
                                    ],
                                },
                                {
                                    "page_number": 1,
                                    "polygon": [
                                        {"x": 1, "y": 2},
                                        {
                                            "x": 3,
                                            "y": 4,
                                        },
                                    ],
                                },
                            ],
                            "spans": [
                                {
                                    "offset": 5,
                                    "length": 2,
                                },
                                {
                                    "offset": 5,
                                    "length": 2,
                                },
                            ],
                            "confidence": 0.99,
                        },
                    },
                    "confidence": 0.99,
                },
            ],
        }

        assert d == final

    def test_model_operation_to_dict(self):
        model = _models.DocumentModelOperationDetails(
            api_version="2022-06-30-preview",
            tags={},
            operation_id="id123",
            status="succeeded",
            percent_completed=100,
            created_on="1994-11-05T13:15:30Z",
            last_updated_on="1994-11-05T13:20:30Z",
            kind="documentModelBuild",
            resource_location="https://contoso.com/resource",
            result=_models.DocumentModelDetails(
                api_version="2022-06-30-preview",
                tags={},
                description="my description",
                created_on="1994-11-05T13:15:30Z",
                model_id="prebuilt-invoice",
                doc_types={
                    "prebuilt-invoice": _models.DocTypeDetails(
                        build_mode="template",
                        description="my description",
                        field_confidence={"CustomerName": 95},
                        field_schema={
                            "prebuilt-invoice": {
                                "CustomerName": {"type": "string"},
                                "CustomerId": {"type": "string"},
                                "PurchaseOrder": {"type": "string"},
                                "InvoiceId": {"type": "string"},
                                "InvoiceDate": {"type": "date"},
                                "DueDate": {"type": "date"},
                                "VendorName": {"type": "string"},
                                "VendorAddress": {"type": "string"},
                                "VendorAddressRecipient": {"type": "string"},
                                "CustomerAddress": {"type": "string"},
                                "CustomerAddressRecipient": {"type": "string"},
                                "BillingAddress": {"type": "string"},
                                "BillingAddressRecipient": {"type": "string"},
                                "ShippingAddress": {"type": "string"},
                                "ShippingAddressRecipient": {"type": "string"},
                                "SubTotal": {"type": "number"},
                                "TotalTax": {"type": "number"},
                                "InvoiceTotal": {"type": "number"},
                                "AmountDue": {"type": "number"},
                                "PreviousUnpaidBalance": {"type": "number"},
                                "RemittanceAddress": {"type": "string"},
                                "RemittanceAddressRecipient": {"type": "string"},
                                "ServiceAddress": {"type": "string"},
                                "ServiceAddressRecipient": {"type": "string"},
                                "ServiceStartDate": {"type": "date"},
                                "ServiceEndDate": {"type": "date"},
                                "Items": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "Amount": {"type": "number"},
                                            "Date": {"type": "date"},
                                            "Description": {"type": "string"},
                                            "Quantity": {"type": "number"},
                                            "ProductCode": {"type": "string"},
                                            "Tax": {"type": "number"},
                                            "Unit": {"type": "string"},
                                            "UnitPrice": {"type": "number"},
                                        },
                                    },
                                },
                            }
                        },
                    )
                },
            ),
            error=_models.DocumentAnalysisError(
                code="ResourceNotFound",
                message="Resource was not found",
                target="resource",
                details=[
                    _models.DocumentAnalysisError(
                        code="ResourceNotFound", message="Resource was not found"
                    )
                ],
                innererror=_models.DocumentAnalysisInnerError(
                    code="ResourceNotFound",
                    message="Resource was not found",
                    innererror=_models.DocumentAnalysisInnerError(
                        code="ResourceNotFound",
                        message="Resource was not found",
                    ),
                ),
            ),
        )

        d = model.to_dict()

        final = {
            "api_version": "2022-06-30-preview",
            "tags": {},
            "operation_id": "id123",
            "status": "succeeded",
            "percent_completed": 100,
            "created_on": "1994-11-05T13:15:30Z",
            "last_updated_on": "1994-11-05T13:20:30Z",
            "kind": "documentModelBuild",
            "resource_location": "https://contoso.com/resource",
            "result": {
                "api_version": "2022-06-30-preview",
                "tags": {},
                "description": "my description",
                "created_on": "1994-11-05T13:15:30Z",
                "model_id": "prebuilt-invoice",
                "doc_types": {
                    "prebuilt-invoice": {
                        "build_mode": "template",
                        "description": "my description",
                        "field_confidence": {"CustomerName": 95},
                        "field_schema": {
                            "prebuilt-invoice": {
                                "CustomerName": {"type": "string"},
                                "CustomerId": {"type": "string"},
                                "PurchaseOrder": {"type": "string"},
                                "InvoiceId": {"type": "string"},
                                "InvoiceDate": {"type": "date"},
                                "DueDate": {"type": "date"},
                                "VendorName": {"type": "string"},
                                "VendorAddress": {"type": "string"},
                                "VendorAddressRecipient": {"type": "string"},
                                "CustomerAddress": {"type": "string"},
                                "CustomerAddressRecipient": {"type": "string"},
                                "BillingAddress": {"type": "string"},
                                "BillingAddressRecipient": {"type": "string"},
                                "ShippingAddress": {"type": "string"},
                                "ShippingAddressRecipient": {"type": "string"},
                                "SubTotal": {"type": "number"},
                                "TotalTax": {"type": "number"},
                                "InvoiceTotal": {"type": "number"},
                                "AmountDue": {"type": "number"},
                                "PreviousUnpaidBalance": {"type": "number"},
                                "RemittanceAddress": {"type": "string"},
                                "RemittanceAddressRecipient": {"type": "string"},
                                "ServiceAddress": {"type": "string"},
                                "ServiceAddressRecipient": {"type": "string"},
                                "ServiceStartDate": {"type": "date"},
                                "ServiceEndDate": {"type": "date"},
                                "Items": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "Amount": {"type": "number"},
                                            "Date": {"type": "date"},
                                            "Description": {"type": "string"},
                                            "Quantity": {"type": "number"},
                                            "ProductCode": {"type": "string"},
                                            "Tax": {"type": "number"},
                                            "Unit": {"type": "string"},
                                            "UnitPrice": {"type": "number"},
                                        },
                                    },
                                },
                            }
                        },
                    }
                },
            },
            "error": {
                "code": "ResourceNotFound",
                "message": "Resource was not found",
                "target": "resource",
                "details": [
                    {
                        "code": "ResourceNotFound",
                        "message": "Resource was not found",
                        "target": None,
                        "details": [],
                        "innererror": None,
                    }
                ],
                "innererror": {
                    "code": "ResourceNotFound",
                    "message": "Resource was not found",
                    "innererror": {
                        "code": "ResourceNotFound",
                        "message": "Resource was not found",
                        "innererror": None,
                    },
                },
            },
        }

        assert d == final

    def test_doc_type_info_to_dict(self):
        model = _models.DocTypeDetails(
            description="my description",
            build_mode="neural",
            field_confidence={"CustomerName": 95},
            field_schema={
                "prebuilt-invoice": {
                    "CustomerName": {"type": "string"},
                    "CustomerId": {"type": "string"},
                    "PurchaseOrder": {"type": "string"},
                    "InvoiceId": {"type": "string"},
                    "InvoiceDate": {"type": "date"},
                    "DueDate": {"type": "date"},
                    "VendorName": {"type": "string"},
                    "VendorAddress": {"type": "string"},
                    "VendorAddressRecipient": {"type": "string"},
                    "CustomerAddress": {"type": "string"},
                    "CustomerAddressRecipient": {"type": "string"},
                    "BillingAddress": {"type": "string"},
                    "BillingAddressRecipient": {"type": "string"},
                    "ShippingAddress": {"type": "string"},
                    "ShippingAddressRecipient": {"type": "string"},
                    "SubTotal": {"type": "number"},
                    "TotalTax": {"type": "number"},
                    "InvoiceTotal": {"type": "number"},
                    "AmountDue": {"type": "number"},
                    "PreviousUnpaidBalance": {"type": "number"},
                    "RemittanceAddress": {"type": "string"},
                    "RemittanceAddressRecipient": {"type": "string"},
                    "ServiceAddress": {"type": "string"},
                    "ServiceAddressRecipient": {"type": "string"},
                    "ServiceStartDate": {"type": "date"},
                    "ServiceEndDate": {"type": "date"},
                    "Items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "Amount": {"type": "number"},
                                "Date": {"type": "date"},
                                "Description": {"type": "string"},
                                "Quantity": {"type": "number"},
                                "ProductCode": {"type": "string"},
                                "Tax": {"type": "number"},
                                "Unit": {"type": "string"},
                                "UnitPrice": {"type": "number"},
                            },
                        },
                    },
                }
            },
        )

        d = model.to_dict()

        final = {
            "description": "my description",
            "build_mode": "neural",
            "field_confidence": {"CustomerName": 95},
            "field_schema": {
                "prebuilt-invoice": {
                    "CustomerName": {"type": "string"},
                    "CustomerId": {"type": "string"},
                    "PurchaseOrder": {"type": "string"},
                    "InvoiceId": {"type": "string"},
                    "InvoiceDate": {"type": "date"},
                    "DueDate": {"type": "date"},
                    "VendorName": {"type": "string"},
                    "VendorAddress": {"type": "string"},
                    "VendorAddressRecipient": {"type": "string"},
                    "CustomerAddress": {"type": "string"},
                    "CustomerAddressRecipient": {"type": "string"},
                    "BillingAddress": {"type": "string"},
                    "BillingAddressRecipient": {"type": "string"},
                    "ShippingAddress": {"type": "string"},
                    "ShippingAddressRecipient": {"type": "string"},
                    "SubTotal": {"type": "number"},
                    "TotalTax": {"type": "number"},
                    "InvoiceTotal": {"type": "number"},
                    "AmountDue": {"type": "number"},
                    "PreviousUnpaidBalance": {"type": "number"},
                    "RemittanceAddress": {"type": "string"},
                    "RemittanceAddressRecipient": {"type": "string"},
                    "ServiceAddress": {"type": "string"},
                    "ServiceAddressRecipient": {"type": "string"},
                    "ServiceStartDate": {"type": "date"},
                    "ServiceEndDate": {"type": "date"},
                    "Items": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "Amount": {"type": "number"},
                                "Date": {"type": "date"},
                                "Description": {"type": "string"},
                                "Quantity": {"type": "number"},
                                "ProductCode": {"type": "string"},
                                "Tax": {"type": "number"},
                                "Unit": {"type": "string"},
                                "UnitPrice": {"type": "number"},
                            },
                        },
                    },
                }
            },
        }

        assert d == final

    def test_document_model_to_dict(self):
        model = _models.DocumentModelDetails(
            description="my description",
            created_on="1994-11-05T13:15:30Z",
            model_id="prebuilt-invoice",
            api_version="2022-06-30-preview",
            tags={"test": "value"},
            doc_types={
                "prebuilt-invoice": _models.DocTypeDetails(
                    build_mode="template",
                    description="my description",
                    field_confidence={"CustomerName": 95},
                    field_schema={
                        "prebuilt-invoice": {
                            "CustomerName": {"type": "string"},
                            "CustomerId": {"type": "string"},
                            "PurchaseOrder": {"type": "string"},
                            "InvoiceId": {"type": "string"},
                            "InvoiceDate": {"type": "date"},
                            "DueDate": {"type": "date"},
                            "VendorName": {"type": "string"},
                            "VendorAddress": {"type": "string"},
                            "VendorAddressRecipient": {"type": "string"},
                            "CustomerAddress": {"type": "string"},
                            "CustomerAddressRecipient": {"type": "string"},
                            "BillingAddress": {"type": "string"},
                            "BillingAddressRecipient": {"type": "string"},
                            "ShippingAddress": {"type": "string"},
                            "ShippingAddressRecipient": {"type": "string"},
                            "SubTotal": {"type": "number"},
                            "TotalTax": {"type": "number"},
                            "InvoiceTotal": {"type": "number"},
                            "AmountDue": {"type": "number"},
                            "PreviousUnpaidBalance": {"type": "number"},
                            "RemittanceAddress": {"type": "string"},
                            "RemittanceAddressRecipient": {"type": "string"},
                            "ServiceAddress": {"type": "string"},
                            "ServiceAddressRecipient": {"type": "string"},
                            "ServiceStartDate": {"type": "date"},
                            "ServiceEndDate": {"type": "date"},
                            "Items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "Amount": {"type": "number"},
                                        "Date": {"type": "date"},
                                        "Description": {"type": "string"},
                                        "Quantity": {"type": "number"},
                                        "ProductCode": {"type": "string"},
                                        "Tax": {"type": "number"},
                                        "Unit": {"type": "string"},
                                        "UnitPrice": {"type": "number"},
                                    },
                                },
                            },
                        }
                    },
                ),
            },
        )

        d = model.to_dict()

        final = {
            "description": "my description",
            "created_on": "1994-11-05T13:15:30Z",
            "model_id": "prebuilt-invoice",
            "api_version": "2022-06-30-preview",
            "tags": {"test": "value"},
            "doc_types": {
                "prebuilt-invoice": {
                    "build_mode": "template",
                    "description": "my description",
                    "field_confidence": {"CustomerName": 95},
                    "field_schema": {
                        "prebuilt-invoice": {
                            "CustomerName": {"type": "string"},
                            "CustomerId": {"type": "string"},
                            "PurchaseOrder": {"type": "string"},
                            "InvoiceId": {"type": "string"},
                            "InvoiceDate": {"type": "date"},
                            "DueDate": {"type": "date"},
                            "VendorName": {"type": "string"},
                            "VendorAddress": {"type": "string"},
                            "VendorAddressRecipient": {"type": "string"},
                            "CustomerAddress": {"type": "string"},
                            "CustomerAddressRecipient": {"type": "string"},
                            "BillingAddress": {"type": "string"},
                            "BillingAddressRecipient": {"type": "string"},
                            "ShippingAddress": {"type": "string"},
                            "ShippingAddressRecipient": {"type": "string"},
                            "SubTotal": {"type": "number"},
                            "TotalTax": {"type": "number"},
                            "InvoiceTotal": {"type": "number"},
                            "AmountDue": {"type": "number"},
                            "PreviousUnpaidBalance": {"type": "number"},
                            "RemittanceAddress": {"type": "string"},
                            "RemittanceAddressRecipient": {"type": "string"},
                            "ServiceAddress": {"type": "string"},
                            "ServiceAddressRecipient": {"type": "string"},
                            "ServiceStartDate": {"type": "date"},
                            "ServiceEndDate": {"type": "date"},
                            "Items": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "Amount": {"type": "number"},
                                        "Date": {"type": "date"},
                                        "Description": {"type": "string"},
                                        "Quantity": {"type": "number"},
                                        "ProductCode": {"type": "string"},
                                        "Tax": {"type": "number"},
                                        "Unit": {"type": "string"},
                                        "UnitPrice": {"type": "number"},
                                    },
                                },
                            },
                        }
                    },
                },
            },
        }

        assert d == final

    def test_document_model_info_to_dict(self):
        model = _models.DocumentModelSummary(
            description="my description",
            created_on="1994-11-05T13:15:30Z",
            model_id="prebuilt-invoice",
            api_version="2022-06-30-preview",
            tags={"test": "value"},
        )

        d = model.to_dict()

        final = {
            "description": "my description",
            "created_on": "1994-11-05T13:15:30Z",
            "model_id": "prebuilt-invoice",
            "api_version": "2022-06-30-preview",
            "tags": {"test": "value"},
        }

        assert d == final

    def test_account_info_to_dict(self):
        model = _models.ResourceDetails(document_model_limit=5000, document_model_count=10)

        d = model.to_dict()

        final = {"document_model_limit": 5000, "document_model_count": 10}
        assert d == final

    def test_document_analysis_inner_error_to_dict(self):
        model = _models.DocumentAnalysisInnerError(
            code="ResourceNotFound",
            message="Resource was not found",
            innererror=_models.DocumentAnalysisInnerError(
                code="ResourceNotFound",
                message="Resource was not found",
            ),
        )

        d = model.to_dict()

        final = {
            "code": "ResourceNotFound",
            "message": "Resource was not found",
            "innererror": {
                "code": "ResourceNotFound",
                "message": "Resource was not found",
                "innererror": None,
            },
        }
        assert d == final

    def test_document_analysis_error_to_dict(self):
        model = _models.DocumentAnalysisError(
            code="ResourceNotFound",
            message="Resource was not found",
            target="resource",
            details=[
                _models.DocumentAnalysisError(
                    code="ResourceNotFound", message="Resource was not found"
                )
            ],
            innererror=_models.DocumentAnalysisInnerError(
                code="ResourceNotFound",
                message="Resource was not found",
                innererror=_models.DocumentAnalysisInnerError(
                    code="ResourceNotFound",
                    message="Resource was not found",
                ),
            ),
        )

        d = model.to_dict()

        final = {
            "code": "ResourceNotFound",
            "message": "Resource was not found",
            "target": "resource",
            "details": [
                {
                    "code": "ResourceNotFound",
                    "message": "Resource was not found",
                    "target": None,
                    "details": [],
                    "innererror": None,
                }
            ],
            "innererror": {
                "code": "ResourceNotFound",
                "message": "Resource was not found",
                "innererror": {
                    "code": "ResourceNotFound",
                    "message": "Resource was not found",
                    "innererror": None,
                },
            },
        }
        assert d == final
