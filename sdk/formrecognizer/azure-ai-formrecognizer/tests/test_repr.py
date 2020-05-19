# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

import pytest
import datetime
from azure.ai.formrecognizer import _models

# All features return a tuple of the object and the repr of the obejct

# Adding in assert for each pytest fixture so it's easier to narrow down where the problem is

@pytest.fixture
def bounding_box():
    model = [
        _models.Point(1, 2),
        _models.Point(3, 4),
        _models.Point(5, 6),
        _models.Point(7, 8)
    ]
    model_repr = '[Point(x=1, y=2), Point(x=3, y=4), Point(x=5, y=6), Point(x=7, y=8)]'
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def form_word(bounding_box):
    model = _models.FormWord(text="Word", bounding_box=bounding_box[0], confidence=0.5, page_number=1)
    model_repr = "FormWord(text=Word, bounding_box={}, confidence=0.5, page_number=1)".format(bounding_box[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr


@pytest.fixture
def form_line(bounding_box, form_word):
    model = _models.FormLine(text="Word Word", bounding_box=bounding_box[0], words=[form_word[0], form_word[0]], page_number=1)
    model_repr = "FormLine(text=Word Word, bounding_box={}, words=[{}, {}], page_number=1)".format(bounding_box[1], form_word[1], form_word[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def form_table_cell(bounding_box, form_word):
    model = _models.FormTableCell(
        text="Cell", row_index=3, column_index=4, row_span=2, column_span=3, bounding_box=bounding_box[0],
        confidence=0.7, is_header=True, is_footer=False, page_number=3, text_content=[form_word[0]]
    )
    model_repr = "FormTableCell(text=Cell, row_index=3, column_index=4, row_span=2, column_span=3, bounding_box={}, confidence=0.7, " \
        "is_header=True, is_footer=False, page_number=3, text_content=[{}])".format(bounding_box[1], form_word[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def form_table(form_table_cell):
    model = _models.FormTable(cells=[form_table_cell[0], form_table_cell[0]], row_count=3, column_count=4)
    model_repr = "FormTable(cells=[{}, {}], row_count=3, column_count=4)".format(form_table_cell[1], form_table_cell[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def field_text(bounding_box, form_word, form_line):
    model = _models.FieldText(page_number=1, text="This is text.", bounding_box=bounding_box[0], text_content=[form_word[0], form_line[0]])
    model_repr = "FieldText(page_number=1, text=This is text., bounding_box={}, text_content=[{}, {}])".format(bounding_box[1], form_word[1], form_line[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def form_field_two(field_text):
    model = _models.FormField(label_data=field_text[0], value_data=field_text[0], name="form_field_two", value="value", confidence=0)
    model_repr = "FormField(label_data={}, value_data={}, name=form_field_two, value='value', confidence=0)".format(field_text[1], field_text[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def form_field_one(field_text, form_field_two):
    model = _models.FormField(label_data=field_text[0], value_data=field_text[0], name="form_field_one", value=form_field_two[0], confidence=1.0)
    model_repr = "FormField(label_data={}, value_data={}, name=form_field_one, value={}, confidence=1.0)".format(field_text[1], field_text[1], form_field_two[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def page_range():
    model = _models.FormPageRange(first_page=1, last_page=100)
    model_repr = "FormPageRange(first_page=1, last_page=100)"
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def form_page(form_table, form_line):
    model = _models.FormPage(page_number=1, text_angle=180, width=5, height=5.5, unit=_models.LengthUnit.pixel, tables=[form_table[0]], lines=[form_line[0]])
    model_repr = "FormPage(page_number=1, text_angle=180, width=5, height=5.5, unit=pixel, tables=[{}], lines=[{}])".format(
            form_table[1], form_line[1]
        )[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def us_receipt_type():
    model = _models.ReceiptType(type="Itemized", confidence=1.0)
    model_repr = "ReceiptType(type=Itemized, confidence=1.0)"
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def us_receipt_item(form_field_two):
    model = _models.USReceiptItem(name=form_field_two[0], quantity=form_field_two[0], price=form_field_two[0], total_price=form_field_two[0])
    model_repr = "USReceiptItem(name={}, quantity={}, price={}, total_price={})".format(form_field_two[1], form_field_two[1], form_field_two[1], form_field_two[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def custom_form_model_field():
    model = _models.CustomFormModelField(label="label", name="name", accuracy=0.99)
    model_repr = "CustomFormModelField(label=label, name=name, accuracy=0.99)"
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def custom_form_sub_model(custom_form_model_field):
    model = _models.CustomFormSubModel(accuracy=0.99, fields={"name": custom_form_model_field[0]}, form_type="Itemized")
    model_repr = "CustomFormSubModel(accuracy=0.99, fields={{'name': {}}}, form_type=Itemized)".format(custom_form_model_field[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def form_recognizer_error():
    model = _models.FormRecognizerError(code=404, message="Resource Not Found")
    model_repr = "FormRecognizerError(code=404, message=Resource Not Found)"
    assert repr(model) == model_repr
    return model, model_repr

@pytest.fixture
def training_document_info(form_recognizer_error):
    model = _models.TrainingDocumentInfo(document_name="document_name", status=_models.TrainingStatus.partially_succeeded, page_count=5, errors=[form_recognizer_error[0]])
    model_repr = "TrainingDocumentInfo(document_name=document_name, status=partiallySucceeded, page_count=5, errors=[{}])".format(form_recognizer_error[1])[:1024]
    assert repr(model) == model_repr
    return model, model_repr


class TestRepr():
    # Not inheriting form FormRecognizerTest because that doesn't allow me to define pytest fixtures in the same file
    # Not worth moving pytest fixture definitions to conftest since all I would use is assertEqual and I can just use assert
    def test_recognized_form(self, form_field_one, page_range, form_page, us_receipt_type, us_receipt_item):
        model = _models.RecognizedForm(form_type="receipt", fields={"one": form_field_one[0]}, page_range=page_range[0], pages=[form_page[0]])
        model_repr = "RecognizedForm(form_type=receipt, fields={{'one': {}}}, page_range={}, pages=[{}])".format(
            form_field_one[1], page_range[1], form_page[1]
        )[:1024]
        assert repr(model) == model_repr

    def test_recognized_receipt(self, form_field_one, page_range, form_page, us_receipt_type):
        model = _models.RecognizedReceipt(
            form_type="receipt", fields={"one": form_field_one[0]}, page_range=page_range[0], pages=[form_page[0]],
            receipt_type=us_receipt_type[0], receipt_locale="en-US")
        model_repr = "RecognizedReceipt(form_type=receipt, fields={{'one': {}}}, page_range={}, pages=[{}])".format(
            form_field_one[1], page_range[1], form_page[1], us_receipt_type[0], "en-US"
        )[:1024]
        assert repr(model) == model_repr

    def test_us_receipt(self, form_field_one, form_field_two, us_receipt_type, us_receipt_item, page_range, form_page):
        model = _models.USReceipt(
            merchant_address=form_field_one[0],
            merchant_name=form_field_two[0],
            merchant_phone_number=form_field_one[0],
            receipt_type=us_receipt_type[0],
            receipt_items=[us_receipt_item[0], us_receipt_item[0]],
            subtotal=form_field_two[0],
            tax=form_field_one[0],
            tip=form_field_two[0],
            total=form_field_one[0],
            transaction_date=form_field_two[0],
            transaction_time=form_field_one[0],
            fields={
                "one": form_field_one[0]
            },
            page_range=page_range[0],
            pages=[form_page[0]],
            form_type="test",
            receipt_locale="en-US"
        )
        model_repr="USReceipt(merchant_address={}, merchant_name={}, merchant_phone_number={}, receipt_type={}, receipt_items=[{}, {}], subtotal={}, " \
            "tax={}, tip={}, total={}, transaction_date={}, transaction_time={}, fields={{'one': {}}}, page_range={}, pages=[{}], " \
            "form_type=test, receipt_locale=en-US)".format(
                form_field_one[1],
                form_field_two[1],
                form_field_one[1],
                us_receipt_type[1],
                us_receipt_item[1],
                us_receipt_item[1],
                form_field_two[1],
                form_field_one[1],
                form_field_two[1],
                form_field_one[1],
                form_field_two[1],
                form_field_one[1],
                form_field_one[1],
                page_range[1],
                form_page[1]
            )[:1024]


        assert repr(model) == model_repr

    def test_custom_form_model(self, custom_form_sub_model, form_recognizer_error, training_document_info):
        model = _models.CustomFormModel(
            model_id=1,
            status=_models.CustomFormModelStatus.creating,
            created_on=datetime.datetime(1, 1, 1),
            last_modified=datetime.datetime(1, 1, 1),
            models=[custom_form_sub_model[0], custom_form_sub_model[0]],
            errors=[form_recognizer_error[0]],
            training_documents=[training_document_info[0], training_document_info[0]]
        )

        model_repr = "CustomFormModel(model_id=1, status=creating, created_on=0001-01-01 00:00:00, " \
            "last_modified=0001-01-01 00:00:00, models=[{}, {}], errors=[{}], training_documents=[{}, {}])".format(
                custom_form_sub_model[1], custom_form_sub_model[1], form_recognizer_error[1], training_document_info[1], training_document_info[1]
            )[:1024]

        assert repr(model) == model_repr

    def test_custom_form_model_info(self):
        model = _models.CustomFormModelInfo(
            model_id=1, status=_models.CustomFormModelStatus.ready, created_on=datetime.datetime(1, 1, 1), last_modified=datetime.datetime(1, 1, 1)
        )
        model_repr = "CustomFormModelInfo(model_id=1, status=ready, created_on=0001-01-01 00:00:00, last_modified=0001-01-01 00:00:00)"[:1024]
        assert repr(model) == model_repr

    def test_account_properties(self):
        model = _models.AccountProperties(custom_model_count=100, custom_model_limit=1000)
        model_repr = "AccountProperties(custom_model_count=100, custom_model_limit=1000)"
        assert repr(model) == model_repr
