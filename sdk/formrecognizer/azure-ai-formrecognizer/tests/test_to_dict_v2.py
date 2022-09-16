# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime
from azure.ai.formrecognizer import _models
from testcase import FormRecognizerTest


class TestToDict(FormRecognizerTest):
    def test_point_to_dict(self):
        model = [_models.Point(1, 2), _models.Point(3, 4)]
        d = [p.to_dict() for p in model]
        final = [
            {"x": 1, "y": 2},
            {
                "x": 3,
                "y": 4,
            },
        ]
        assert d == final

    def test_form_word_to_dict(self):
        form_word = _models.FormWord(
            text="word",
            confidence=0.92,
            page_number=1,
            bounding_box=[
                _models.Point(1427.0, 1669.0),
                _models.Point(1527.0, 1669.0),
                _models.Point(1527.0, 1698.0),
                _models.Point(1427.0, 1698.0),
            ],
        )

        d = form_word.to_dict()
        final = {
            "text": "word",
            "bounding_box": [
                {"x": 1427.0, "y": 1669.0},
                {"x": 1527.0, "y": 1669.0},
                {"x": 1527.0, "y": 1698.0},
                {"x": 1427.0, "y": 1698.0},
            ],
            "confidence": 0.92,
            "page_number": 1,
            "kind": "word",
        }
        assert d == final

    def test_form_line_to_dict(self):
        form_line = _models.FormLine(
            text="sample line",
            bounding_box=[
                _models.Point(1427.0, 1669.0),
                _models.Point(1527.0, 1669.0),
                _models.Point(1527.0, 1698.0),
                _models.Point(1427.0, 1698.0),
            ],
            words=[
                _models.FormWord(
                    text="sample",
                    confidence=0.92,
                    page_number=1,
                    bounding_box=[
                        _models.Point(1427.0, 1669.0),
                        _models.Point(1527.0, 1669.0),
                        _models.Point(1527.0, 1698.0),
                        _models.Point(1427.0, 1698.0),
                    ],
                ),
                _models.FormWord(
                    text="line",
                    confidence=0.92,
                    page_number=1,
                    bounding_box=[
                        _models.Point(1427.0, 1669.0),
                        _models.Point(1527.0, 1669.0),
                        _models.Point(1527.0, 1698.0),
                        _models.Point(1427.0, 1698.0),
                    ],
                ),
            ],
            page_number=2,
            appearance=_models.TextAppearance(
                style_name="other", style_confidence=0.90
            ),
        )

        d = form_line.to_dict()
        final = {
            "text": "sample line",
            "bounding_box": [
                {"x": 1427.0, "y": 1669.0},
                {"x": 1527.0, "y": 1669.0},
                {"x": 1527.0, "y": 1698.0},
                {"x": 1427.0, "y": 1698.0},
            ],
            "words": [
                {
                    "text": "sample",
                    "bounding_box": [
                        {"x": 1427.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1698.0},
                        {"x": 1427.0, "y": 1698.0},
                    ],
                    "confidence": 0.92,
                    "page_number": 1,
                    "kind": "word",
                },
                {
                    "text": "line",
                    "bounding_box": [
                        {"x": 1427.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1698.0},
                        {"x": 1427.0, "y": 1698.0},
                    ],
                    "confidence": 0.92,
                    "page_number": 1,
                    "kind": "word",
                },
            ],
            "page_number": 2,
            "kind": "line",
            "appearance": {"style_name": "other", "style_confidence": 0.90},
        }
        assert d == final

    def test_form_selection_mark_to_dict(self):
        form_selection_mark = _models.FormSelectionMark(
            text="checkbox",
            state="selected",
            confidence=0.92,
            page_number=1,
            bounding_box=[
                _models.Point(1427.0, 1669.0),
                _models.Point(1527.0, 1669.0),
                _models.Point(1527.0, 1698.0),
                _models.Point(1427.0, 1698.0),
            ],
        )

        d = form_selection_mark.to_dict()
        final = {
            "text": "checkbox",
            "state": "selected",
            "bounding_box": [
                {"x": 1427.0, "y": 1669.0},
                {"x": 1527.0, "y": 1669.0},
                {"x": 1527.0, "y": 1698.0},
                {"x": 1427.0, "y": 1698.0},
            ],
            "confidence": 0.92,
            "page_number": 1,
            "kind": "selectionMark",
        }
        assert d == final

    def test_form_element_to_dict(self):
        form_element = _models.FormElement(
            kind="selectionMark",
            text="element",
            page_number=1,
            bounding_box=[
                _models.Point(1427.0, 1669.0),
                _models.Point(1527.0, 1669.0),
                _models.Point(1527.0, 1698.0),
                _models.Point(1427.0, 1698.0),
            ],
        )

        d = form_element.to_dict()
        final = {
            "text": "element",
            "bounding_box": [
                {"x": 1427.0, "y": 1669.0},
                {"x": 1527.0, "y": 1669.0},
                {"x": 1527.0, "y": 1698.0},
                {"x": 1427.0, "y": 1698.0},
            ],
            "page_number": 1,
            "kind": "selectionMark",
        }
        assert d == final

    def test_text_appearance_to_dict(self):
        model = _models.TextAppearance(
            style_name="other", style_confidence=0.98
        )

        d = model.to_dict()
        final = {"style_name": "other", "style_confidence": 0.98}
        assert d == final

    def test_field_data_to_dict(self):
        model = _models.FieldData(
            text="element",
            page_number=1,
            bounding_box=[
                _models.Point(1427.0, 1669.0),
                _models.Point(1527.0, 1669.0),
                _models.Point(1527.0, 1698.0),
                _models.Point(1427.0, 1698.0),
            ],
            field_elements=[
                _models.FormWord(
                    text="word",
                    confidence=0.92,
                    page_number=1,
                    bounding_box=[
                        _models.Point(1427.0, 1669.0),
                        _models.Point(1527.0, 1669.0),
                        _models.Point(1527.0, 1698.0),
                        _models.Point(1427.0, 1698.0),
                    ],
                ),
            ],
        )

        d = model.to_dict()
        final = {
            "text": "element",
            "bounding_box": [
                {"x": 1427.0, "y": 1669.0},
                {"x": 1527.0, "y": 1669.0},
                {"x": 1527.0, "y": 1698.0},
                {"x": 1427.0, "y": 1698.0},
            ],
            "page_number": 1,
            "field_elements": [
                {
                    "text": "word",
                    "bounding_box": [
                        {"x": 1427.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1698.0},
                        {"x": 1427.0, "y": 1698.0},
                    ],
                    "confidence": 0.92,
                    "page_number": 1,
                    "kind": "word",
                }
            ],
        }
        assert d == final

    def test_form_field_to_dict(self):
        form_field = _models.FormField(
            value_type="phoneNumber",
            label_data=_models.FieldData(
                text="phone",
                page_number=1,
                bounding_box=[
                    _models.Point(1427.0, 1669.0),
                    _models.Point(1527.0, 1669.0),
                    _models.Point(1527.0, 1698.0),
                    _models.Point(1427.0, 1698.0),
                ],
            ),
            value_data=_models.FieldData(
                text="55554444",
                page_number=1,
                bounding_box=[
                    _models.Point(1427.0, 1669.0),
                    _models.Point(1527.0, 1669.0),
                    _models.Point(1527.0, 1698.0),
                    _models.Point(1427.0, 1698.0),
                ],
            ),
            name="phone",
            value="55554444",
            confidence=0.99,
        )

        d = form_field.to_dict()
        final = {
            "value_type": "phoneNumber",
            "label_data": {
                "text": "phone",
                "bounding_box": [
                    {"x": 1427.0, "y": 1669.0},
                    {"x": 1527.0, "y": 1669.0},
                    {"x": 1527.0, "y": 1698.0},
                    {"x": 1427.0, "y": 1698.0},
                ],
                "page_number": 1,
                "field_elements": []
            },
            "value_data": {
                "text": "55554444",
                "bounding_box": [
                    {"x": 1427.0, "y": 1669.0},
                    {"x": 1527.0, "y": 1669.0},
                    {"x": 1527.0, "y": 1698.0},
                    {"x": 1427.0, "y": 1698.0},
                ],
                "page_number": 1,
                "field_elements": []
            },
            "name": "phone",
            "value": "55554444",
            "confidence": 0.99,
        }
        assert d == final

    def test_recognized_form_to_dict(self):
        form = _models.RecognizedForm(
            form_type="test_form",
            form_type_confidence="0.84",
            model_id="examplemodel123",
            page_range=_models.FormPageRange(1, 1),
            fields={
                "example": _models.FormField(
                    value_type="phoneNumber",
                    label_data=_models.FieldData(
                        text="phone",
                        page_number=1,
                        bounding_box=[
                            _models.Point(1427.0, 1669.0),
                            _models.Point(1527.0, 1669.0),
                            _models.Point(1527.0, 1698.0),
                            _models.Point(1427.0, 1698.0),
                        ],
                    ),
                    value_data=_models.FieldData(
                        text="55554444",
                        page_number=1,
                        bounding_box=[
                            _models.Point(1427.0, 1669.0),
                            _models.Point(1527.0, 1669.0),
                            _models.Point(1527.0, 1698.0),
                            _models.Point(1427.0, 1698.0),
                        ],
                    ),
                    name="phone",
                    value="55554444",
                    confidence=0.99,
                )
            },
            pages=[_models.FormPage(
                page_number=1,
                text_angle=180.0,
                width=5.5,
                height=8.0,
                unit="pixel",
                lines=[_models.FormLine(
                        text="sample line",
                        bounding_box=[
                            _models.Point(1427.0, 1669.0),
                            _models.Point(1527.0, 1669.0),
                            _models.Point(1527.0, 1698.0),
                            _models.Point(1427.0, 1698.0),
                        ],
                        words=[
                            _models.FormWord(
                                text="sample",
                                confidence=0.92,
                                page_number=1,
                                bounding_box=[
                                    _models.Point(1427.0, 1669.0),
                                    _models.Point(1527.0, 1669.0),
                                    _models.Point(1527.0, 1698.0),
                                    _models.Point(1427.0, 1698.0),
                                ],
                            ),
                            _models.FormWord(
                                text="line",
                                confidence=0.92,
                                page_number=1,
                                bounding_box=[
                                    _models.Point(1427.0, 1669.0),
                                    _models.Point(1527.0, 1669.0),
                                    _models.Point(1527.0, 1698.0),
                                    _models.Point(1427.0, 1698.0),
                                ],
                            ),
                        ],
                        page_number=2,
                        appearance=_models.TextAppearance(
                            style_name="other", style_confidence=0.90
                        ),
                    )],
                )
            ]
        )

        d = form.to_dict()
        final = {
            "form_type": "test_form",
            "form_type_confidence": "0.84",
            "model_id": "examplemodel123",
            "page_range": {"first_page_number": 1, "last_page_number": 1},
            "fields": { 
                "example": {
                    "value_type": "phoneNumber",
                    "label_data": {
                        "text": "phone",
                        "bounding_box": [
                            {"x": 1427.0, "y": 1669.0},
                            {"x": 1527.0, "y": 1669.0},
                            {"x": 1527.0, "y": 1698.0},
                            {"x": 1427.0, "y": 1698.0},
                        ],
                        "page_number": 1,
                        "field_elements": []
                    },
                    "value_data": {
                        "text": "55554444",
                        "bounding_box": [
                            {"x": 1427.0, "y": 1669.0},
                            {"x": 1527.0, "y": 1669.0},
                            {"x": 1527.0, "y": 1698.0},
                            {"x": 1427.0, "y": 1698.0},
                        ],
                        "page_number": 1,
                        "field_elements": []
                    },
                    "name": "phone",
                    "value": "55554444",
                    "confidence": 0.99,
                }
            },
            "pages": [{
                "page_number": 1,
                "text_angle": 180.0,
                "width": 5.5,
                "height": 8.0,
                "unit": "pixel",
                "lines": [{
                    "text": "sample line",
                    "bounding_box": [
                        {"x": 1427.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1698.0},
                        {"x": 1427.0, "y": 1698.0},
                    ],
                    "words": [
                        {
                            "text": "sample",
                            "bounding_box": [
                                {"x": 1427.0, "y": 1669.0},
                                {"x": 1527.0, "y": 1669.0},
                                {"x": 1527.0, "y": 1698.0},
                                {"x": 1427.0, "y": 1698.0},
                            ],
                            "confidence": 0.92,
                            "page_number": 1,
                            "kind": "word",
                        },
                        {
                            "text": "line",
                            "bounding_box": [
                                {"x": 1427.0, "y": 1669.0},
                                {"x": 1527.0, "y": 1669.0},
                                {"x": 1527.0, "y": 1698.0},
                                {"x": 1427.0, "y": 1698.0},
                            ],
                            "confidence": 0.92,
                            "page_number": 1,
                            "kind": "word",
                        },
                    ],
                    "page_number": 2,
                    "kind": "line",
                    "appearance": {"style_name": "other", "style_confidence": 0.90},
                }],    
                "selection_marks": [],
                "tables": [],
            }],
        }
        assert d == final

    def test_form_page_to_dict(self):
        form_page = _models.FormPage(
            page_number=1,
            text_angle=180.0,
            width=5.5,
            height=8.0,
            unit="pixel",
            tables= [
                _models.FormTable(
                    page_number=2,
                    cells=[
                        _models.FormTableCell(
                            text="info",
                            row_index=1,
                            column_index=3,
                            row_span=1,
                            column_span=2,
                            bounding_box=[
                                    _models.Point(1427.0, 1669.0),
                                    _models.Point(1527.0, 1669.0),
                                    _models.Point(1527.0, 1698.0),
                                    _models.Point(1427.0, 1698.0),
                                ],
                            confidence=0.87,
                            is_header=False,
                            is_footer=True,
                            page_number=1,
                            field_elements=[
                                _models.FormWord(
                                    text="word",
                                    confidence=0.92,
                                    page_number=1,
                                    bounding_box=[
                                        _models.Point(1427.0, 1669.0),
                                        _models.Point(1527.0, 1669.0),
                                        _models.Point(1527.0, 1698.0),
                                        _models.Point(1427.0, 1698.0),
                                    ],
                                ),
                            ]
                        )
                    ],
                    row_count=10,
                    column_count=5,
                    bounding_box=[
                        _models.Point(1427.0, 1669.0),
                        _models.Point(1527.0, 1669.0),
                        _models.Point(1527.0, 1698.0),
                        _models.Point(1427.0, 1698.0),
                    ],
                ),
            ],
            lines=[_models.FormLine(
                    text="sample line",
                    bounding_box=[
                        _models.Point(1427.0, 1669.0),
                        _models.Point(1527.0, 1669.0),
                        _models.Point(1527.0, 1698.0),
                        _models.Point(1427.0, 1698.0),
                    ],
                    words=[
                        _models.FormWord(
                            text="sample",
                            confidence=0.92,
                            page_number=1,
                            bounding_box=[
                                _models.Point(1427.0, 1669.0),
                                _models.Point(1527.0, 1669.0),
                                _models.Point(1527.0, 1698.0),
                                _models.Point(1427.0, 1698.0),
                            ],
                        ),
                        _models.FormWord(
                            text="line",
                            confidence=0.92,
                            page_number=1,
                            bounding_box=[
                                _models.Point(1427.0, 1669.0),
                                _models.Point(1527.0, 1669.0),
                                _models.Point(1527.0, 1698.0),
                                _models.Point(1427.0, 1698.0),
                            ],
                        ),
                    ],
                    page_number=2,
                    appearance=_models.TextAppearance(
                        style_name="other", style_confidence=0.90
                    ),
                ),
            ],
            selection_marks=[_models.FormSelectionMark(
                    text="checkbox",
                    state="selected",
                    confidence=0.92,
                    page_number=1,
                    bounding_box=[
                        _models.Point(1427.0, 1669.0),
                        _models.Point(1527.0, 1669.0),
                        _models.Point(1527.0, 1698.0),
                        _models.Point(1427.0, 1698.0),
                    ],
                ),
            ],
            )
        d = form_page.to_dict()
        final = {
            "page_number": 1,
            "text_angle": 180.0,
            "width": 5.5,
            "height": 8.0,
            "unit": "pixel",
            "tables": [
                {"cells": [
                    {
                        "text": "info",
                        "bounding_box": [
                            {"x": 1427.0, "y": 1669.0},
                            {"x": 1527.0, "y": 1669.0},
                            {"x": 1527.0, "y": 1698.0},
                            {"x": 1427.0, "y": 1698.0},
                        ],
                        "row_index": 1,
                        "column_index": 3,
                        "row_span": 1,
                        "column_span": 2,
                        "confidence": 0.87,
                        "is_header": False,
                        "is_footer": True,
                        "page_number": 1,
                        "field_elements": [
                            {
                                "text": "word",
                                "bounding_box": [
                                    {"x": 1427.0, "y": 1669.0},
                                    {"x": 1527.0, "y": 1669.0},
                                    {"x": 1527.0, "y": 1698.0},
                                    {"x": 1427.0, "y": 1698.0},
                                ],
                                "confidence": 0.92,
                                "page_number": 1,
                                "kind": "word",
                            }
                        ],
                    },
                ],
                "page_number": 2,
                "row_count": 10,
                "column_count": 5,
                "bounding_box": [
                    {"x": 1427.0, "y": 1669.0},
                    {"x": 1527.0, "y": 1669.0},
                    {"x": 1527.0, "y": 1698.0},
                    {"x": 1427.0, "y": 1698.0},
                ],
            },
            ],
            "lines": [{
                "text": "sample line",
                "bounding_box": [
                    {"x": 1427.0, "y": 1669.0},
                    {"x": 1527.0, "y": 1669.0},
                    {"x": 1527.0, "y": 1698.0},
                    {"x": 1427.0, "y": 1698.0},
                ],
                "words": [
                    {
                        "text": "sample",
                        "bounding_box": [
                            {"x": 1427.0, "y": 1669.0},
                            {"x": 1527.0, "y": 1669.0},
                            {"x": 1527.0, "y": 1698.0},
                            {"x": 1427.0, "y": 1698.0},
                        ],
                        "confidence": 0.92,
                        "page_number": 1,
                        "kind": "word",
                    },
                    {
                        "text": "line",
                        "bounding_box": [
                            {"x": 1427.0, "y": 1669.0},
                            {"x": 1527.0, "y": 1669.0},
                            {"x": 1527.0, "y": 1698.0},
                            {"x": 1427.0, "y": 1698.0},
                        ],
                        "confidence": 0.92,
                        "page_number": 1,
                        "kind": "word",
                    },
                ],
                "page_number": 2,
                "kind": "line",
                "appearance": {"style_name": "other", "style_confidence": 0.90},
            }],
            "selection_marks": [{
                "text": "checkbox",
                "state": "selected",
                "bounding_box": [
                    {"x": 1427.0, "y": 1669.0},
                    {"x": 1527.0, "y": 1669.0},
                    {"x": 1527.0, "y": 1698.0},
                    {"x": 1427.0, "y": 1698.0},
                ],
                "confidence": 0.92,
                "page_number": 1,
                "kind": "selectionMark",
            }],
        }
        assert d == final

    def test_form_table_cell_to_dict(self):
        table_cell = _models.FormTableCell(
            text="info",
            row_index=1,
            column_index=3,
            row_span=1,
            column_span=2,
            bounding_box=[
                    _models.Point(1427.0, 1669.0),
                    _models.Point(1527.0, 1669.0),
                    _models.Point(1527.0, 1698.0),
                    _models.Point(1427.0, 1698.0),
                ],
            confidence=0.87,
            is_header=False,
            is_footer=True,
            page_number=1,
            field_elements=[
                _models.FormWord(
                    text="word",
                    confidence=0.92,
                    page_number=1,
                    bounding_box=[
                        _models.Point(1427.0, 1669.0),
                        _models.Point(1527.0, 1669.0),
                        _models.Point(1527.0, 1698.0),
                        _models.Point(1427.0, 1698.0),
                    ],
                ),
            ]
        )

        d = table_cell.to_dict()
        final = {
            "text": "info",
            "bounding_box": [
                {"x": 1427.0, "y": 1669.0},
                {"x": 1527.0, "y": 1669.0},
                {"x": 1527.0, "y": 1698.0},
                {"x": 1427.0, "y": 1698.0},
            ],
            "row_index": 1,
            "column_index": 3,
            "row_span": 1,
            "column_span": 2,
            "confidence": 0.87,
            "is_header": False,
            "is_footer": True,
            "page_number": 1,
            "field_elements": [
                {
                    "text": "word",
                    "bounding_box": [
                        {"x": 1427.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1698.0},
                        {"x": 1427.0, "y": 1698.0},
                    ],
                    "confidence": 0.92,
                    "page_number": 1,
                    "kind": "word",
                }
            ],
        }
        assert d == final

    def test_form_table_to_dict(self):
        table = _models.FormTable(
            page_number=2,
            cells=[
                _models.FormTableCell(
                    text="info",
                    row_index=1,
                    column_index=3,
                    row_span=1,
                    column_span=2,
                    bounding_box=[
                            _models.Point(1427.0, 1669.0),
                            _models.Point(1527.0, 1669.0),
                            _models.Point(1527.0, 1698.0),
                            _models.Point(1427.0, 1698.0),
                        ],
                    confidence=0.87,
                    is_header=False,
                    is_footer=True,
                    page_number=1,
                    field_elements=[
                        _models.FormWord(
                            text="word",
                            confidence=0.92,
                            page_number=1,
                            bounding_box=[
                                _models.Point(1427.0, 1669.0),
                                _models.Point(1527.0, 1669.0),
                                _models.Point(1527.0, 1698.0),
                                _models.Point(1427.0, 1698.0),
                            ],
                        ),
                    ]
                )
            ],
            row_count=10,
            column_count=5,
            bounding_box=[
                _models.Point(1427.0, 1669.0),
                _models.Point(1527.0, 1669.0),
                _models.Point(1527.0, 1698.0),
                _models.Point(1427.0, 1698.0),
            ],
        )

        d = table.to_dict()
        final = {
            "cells": [
                {
                    "text": "info",
                    "bounding_box": [
                        {"x": 1427.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1669.0},
                        {"x": 1527.0, "y": 1698.0},
                        {"x": 1427.0, "y": 1698.0},
                    ],
                    "row_index": 1,
                    "column_index": 3,
                    "row_span": 1,
                    "column_span": 2,
                    "confidence": 0.87,
                    "is_header": False,
                    "is_footer": True,
                    "page_number": 1,
                    "field_elements": [
                        {
                            "text": "word",
                            "bounding_box": [
                                {"x": 1427.0, "y": 1669.0},
                                {"x": 1527.0, "y": 1669.0},
                                {"x": 1527.0, "y": 1698.0},
                                {"x": 1427.0, "y": 1698.0},
                            ],
                            "confidence": 0.92,
                            "page_number": 1,
                            "kind": "word",
                        }
                    ],
                },
            ],
            "page_number": 2,
            "row_count": 10,
            "column_count": 5,
            "bounding_box": [
                {"x": 1427.0, "y": 1669.0},
                {"x": 1527.0, "y": 1669.0},
                {"x": 1527.0, "y": 1698.0},
                {"x": 1427.0, "y": 1698.0},
            ],
        }
        assert d == final

    def test_custom_form_model_properties_to_dict(self):
        model = _models.CustomFormModelProperties(
            is_composed_model=True,
        )
        d = model.to_dict()
        final = {
            "is_composed_model": True,
        }
        assert d == final

    def test_account_properties_to_dict(self):
        model = _models.AccountProperties(
            custom_model_count=5,
            custom_model_limit=10,
        )
        d = model.to_dict()
        final = {
            "custom_model_count": 5,
            "custom_model_limit": 10,
        }
        assert d == final

    def test_custom_form_model_info_to_dict(self):
        model = _models.CustomFormModelInfo(
            model_id="1234",
            status="creating",
            training_started_on=datetime(2021, 1, 10, 23, 55, 59, 342380),
            training_completed_on=datetime(2021, 1, 10, 23, 55, 59, 342380),
            model_name="sample_model",
            properties=_models.CustomFormModelProperties(
                is_composed_model=False,
            )
        )
        d = model.to_dict()
        final = {
            "model_id": "1234",
            "status": "creating",
            "training_started_on": datetime(2021, 1, 10, 23, 55, 59, 342380),
            "training_completed_on": datetime(2021, 1, 10, 23, 55, 59, 342380),
            "model_name": "sample_model",
            "properties": {
                "is_composed_model": False,
            }
        }
        assert d == final

    def test_form_recognizer_error_to_dict(self):
        model = _models.FormRecognizerError(
            code=404,
            message="error not found",
        )
        d = model.to_dict()
        final = {
            "code": 404,
            "message": "error not found",
        }
        assert d == final

    def test_training_document_info_to_dict(self):
        model = _models.TrainingDocumentInfo(
            name="sample doc",
            status="succeeded",
            page_count=3,
            errors=[
                _models.FormRecognizerError(
                    code=404,
                    message="error not found",
                )
            ],
            model_id="1234",
        )
        d = model.to_dict()
        final = {
            "name": "sample doc",
            "status": "succeeded",
            "page_count": 3,
            "errors": [
                {
                    "code": 404,
                    "message": "error not found",
                }
            ],
            "model_id": "1234",
        }
        assert d == final

    def test_custom_form_model_field_to_dict(self):
        model = _models.CustomFormModelField(
            label="field_label",
            name="field",
            accuracy=0.98,
        )
        d = model.to_dict()
        final = {
            "label": "field_label",
            "name": "field",
            "accuracy": 0.98,
        }
        assert d == final

    def test_custom_form_submodel_to_dict(self):
        model = _models.CustomFormSubmodel(
            model_id="1234",
            form_type="submodel",
            accuracy=0.98,
            fields={
                "example": _models.CustomFormModelField(
                    label="field_label",
                    name="field",
                    accuracy=0.98,
                )
            }
        )
        d = model.to_dict()
        final = {
            "model_id": "1234",
            "form_type": "submodel",
            "accuracy": 0.98,
            "fields": { 
                "example": {
                    "label": "field_label",
                    "name": "field",
                    "accuracy": 0.98,
                }
            }
        }
        assert d == final

    def test_custom_form_model_to_dict(self):
        model = _models.CustomFormModel(
            model_id="1234",
            status="ready",
            training_started_on=datetime(2021, 1, 10, 23, 55, 59, 342380),
            training_completed_on=datetime(2021, 1, 10, 23, 55, 59, 342380),
            submodels=[
                _models.CustomFormSubmodel(
                    model_id="1234",
                    form_type="submodel",
                    accuracy=0.98,
                    fields={ 
                        "example": _models.CustomFormModelField(
                            label="field_label",
                            name="field",
                            accuracy=0.98,
                        )
                    }
                )
            ],
            errors=[
                _models.FormRecognizerError(
                    code=404,
                    message="error not found",
                )
            ],
            training_documents=[
                _models.TrainingDocumentInfo(
                    name="sample doc",
                    status="succeeded",
                    page_count=3,
                    errors=[
                        _models.FormRecognizerError(
                            code=404,
                            message="error not found",
                        )
                    ],
                    model_id="1234",
                )
            ],
            model_name="sample model",
            properties=_models.CustomFormModelProperties(
                    is_composed_model=True,
                )
        )
        d = model.to_dict()
        final = {
            "model_id": "1234",
            "status": "ready",
            "training_started_on": datetime(2021, 1, 10, 23, 55, 59, 342380),
            "training_completed_on": datetime(2021, 1, 10, 23, 55, 59, 342380),
            "submodels": [{
                "model_id": "1234",
                "form_type": "submodel",
                "accuracy": 0.98,
                "fields": { 
                    "example": 
                    {
                        "label": "field_label",
                        "name": "field",
                        "accuracy": 0.98,
                    }
                }
            }],
            "errors": [
                {
                    "code": 404,
                    "message": "error not found",
                }
            ],
            "training_documents": [
                {
                    "name": "sample doc",
                    "status": "succeeded",
                    "page_count": 3,
                    "errors": [
                        {
                            "code": 404,
                            "message": "error not found",
                        }
                    ],
                    "model_id": "1234",
                }
            ],
            "model_name": "sample model",
            "properties": {
                "is_composed_model": True,
            }
        }
        assert d == final
