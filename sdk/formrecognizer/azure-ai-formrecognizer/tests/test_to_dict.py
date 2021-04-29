# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import datetime
from azure.ai.formrecognizer import _models


class TestToDict:
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
        form_word = _models.FormLine(
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
                style=_models.TextStyle(name="other", confidence=0.90)
            ),
        )

        d = form_word.to_dict()
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
            "appearance": {"style": {"name": "other", "confidence": 0.90}},
        }
        assert d == final

    def test_form_selection_mark_to_dict(self):
        form_word = _models.FormSelectionMark(
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

        d = form_word.to_dict()
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
        form_word = _models.FormElement(
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

        d = form_word.to_dict()
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
            style=_models.TextStyle(name="other", confidence=0.98)
        )

        d = model.to_dict()
        final = {"style": {"name": "other", "confidence": 0.98}}
        assert d == final

    def test_text_style_to_dict(self):
        model = _models.TextStyle(name="other", confidence=0.98)

        d = model.to_dict()
        final = {"name": "other", "confidence": 0.98}
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
            fields=[
                _models.FormField(
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
            ],
        )

        d = form.to_dict()
        final = {
            "form_type": "test_form",
            "form_type_confidence": "0.84",
            "model_id": "examplemodel123",
            "page_range": {"first_page_number": 1, "last_page_number": 1},
            "fields": [
                {
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
                    },
                    "name": "phone",
                    "value": "55554444",
                    "confidence": 0.99,
                }
            ],
        }
        assert d == final
