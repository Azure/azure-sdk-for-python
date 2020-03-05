# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import re
from ._helpers import get_receipt_field_value


def get_raw_field(field, raw_result):
    raw_lines = []
    lines = set()
    try:
        for item in field.elements:
            nums = [int(s) for s in re.findall(r'\d+', item)]
            read = nums[0]
            line = nums[1]
            ocr_line = raw_result[read].lines[line]

            if line not in lines:
                lines.add(line)
                extracted_line = ExtractedLine._from_generated(ocr_line)
                raw_lines.append(extracted_line)
        return raw_lines
    except TypeError:
        return None


class ExtractedReceipt(object):

    def __init__(self, **kwargs):
        self.merchant_address = kwargs.get("merchant_address", None)
        self.merchant_name = kwargs.get("merchant_name", None)
        self.merchant_phone_number = kwargs.get("merchant_phone_number", None)
        self.receipt_type = kwargs.get("receipt_type", None)
        self.receipt_items = kwargs.get("receipt_items", None)
        self.subtotal = kwargs.get("subtotal", None)
        self.tax = kwargs.get("tax", None)
        self.tip = kwargs.get("tip", None)
        self.total = kwargs.get("total", None)
        self.transaction_date = kwargs.get("transaction_date", None)
        self.transaction_time = kwargs.get("transaction_time", None)
        self.fields = kwargs.get("fields", None)


class ReceiptFields(object):

    def __init__(self, **kwargs):
        self.merchant_address = kwargs.get("merchant_address", None)
        self.merchant_name = kwargs.get("merchant_name", None)
        self.merchant_phone_number = kwargs.get("merchant_phone_number", None)
        self.receipt_type = kwargs.get("receipt_type", None)
        self.receipt_items = kwargs.get("receipt_items", None)
        self.subtotal = kwargs.get("subtotal", None)
        self.tax = kwargs.get("tax", None)
        self.tip = kwargs.get("tip", None)
        self.total = kwargs.get("total", None)
        self.transaction_date = kwargs.get("transaction_date", None)
        self.transaction_time = kwargs.get("transaction_time", None)


class FieldValue(object):

    def __init__(self, **kwargs):
        self.value = kwargs.get("value", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.confidence = kwargs.get("confidence", None)
        self.raw_field = kwargs.get("raw_field", None)

    @classmethod
    def _from_generated(cls, field, read_result, include_raw):
        if field is None:
            return field
        return cls(
            value=get_receipt_field_value(field),
            bounding_box=field.bounding_box,
            confidence=field.confidence,
            raw_field=get_raw_field(field, read_result) if include_raw else None
        )


class ReceiptItem(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.quantity = kwargs.get("quantity", None)
        self.total_price = kwargs.get("total_price", None)

    @classmethod
    def _from_generated(cls, items):
        try:
            receipt_item = items.value_array
            return [cls(
                name=get_receipt_field_value(item.value_object.get("Name")),
                quantity=get_receipt_field_value(item.value_object.get("Quantity")),
                total_price=get_receipt_field_value(item.value_object.get("TotalPrice"))
            ) for item in receipt_item]
        except AttributeError:
            return None


class ReceiptItemField(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.quantity = kwargs.get("quantity", None)
        self.total_price = kwargs.get("total_price", None)

    @classmethod
    def _from_generated(cls, items, read_result, include_raw):
        try:
            receipt_item = items.value_array
            return [cls(
                name=FieldValue._from_generated(item.value_object.get("Name"), read_result, include_raw),
                quantity=FieldValue._from_generated(item.value_object.get("Quantity"), read_result, include_raw),
                total_price=FieldValue._from_generated(item.value_object.get("TotalPrice"), read_result, include_raw),
            ) for item in receipt_item]
        except AttributeError:
            return None


class ExtractedLine(object):
    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.language = kwargs.get("language", None)
        self.words = kwargs.get("words", None)

    @classmethod
    def _from_generated(cls, line):
        return cls(
            text=line.text,
            bounding_box=line.bounding_box,
            language=line.language,
            words=[ExtractedWord._from_generated(word) for word in line.words]
        )


class ExtractedWord(object):
    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, word):
        return cls(
            text=word.text,
            bounding_box=word.bounding_box,
            confidence=word.confidence
        )


class ExtractedLayoutPage(object):
    def __init__(self, **kwargs):
        self.tables = kwargs.get("tables", None)
        self.page_number = kwargs.get("page_number", None)


def Table(table):
    class ExtractedTable(type(table)):

        @property
        def row_count(self):
            return len(table)

        @property
        def column_count(self):
            return len(table[0])

    return ExtractedTable(table)


class TableCell(object):
    def __init__(self, **kwargs):
        self.text = kwargs.get('text', None)
        self.row_index = kwargs.get('row_index', None)
        self.column_index = kwargs.get('column_index', None)
        self.row_span = kwargs.get('row_span', 1)
        self.column_span = kwargs.get('column_span', 1)
        self.bounding_box = kwargs.get('bounding_box', None)
        self.confidence = kwargs.get('confidence', None)
        self.is_header = kwargs.get('is_header', False)
        self.is_footer = kwargs.get('is_footer', False)
        self.raw_field = kwargs.get('raw_field', None)

    @classmethod
    def _from_generated(cls, cell, read_result, include_raw):
        return cls(
            text=cell.text,
            row_index=cell.row_index,
            column_index=cell.column_index,
            row_span=cell.row_span or 1,
            column_span=cell.column_span or 1,
            bounding_box=cell.bounding_box,
            confidence=cell.confidence,
            is_header=cell.is_header,
            is_footer=cell.is_footer,
            raw_field=get_raw_field(cell, read_result) if include_raw else None
        )


class CustomModel(object):
    def __init__(self, **kwargs):
        self.model_id = kwargs.get('model_id', None)
        self.status = kwargs.get('status', None)
        self.created_date_time = kwargs.get('created_date_time', None)
        self.last_updated_date_time = kwargs.get('last_updated_date_time', None)
        self.form_clusters = kwargs.get('form_clusters', None)
        self.train_result = kwargs.get('train_result', None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            model_id=model.model_info.model_id,
            status=model.model_info.status,
            created_date_time=model.model_info.created_date_time,
            last_updated_date_time=model.model_info.last_updated_date_time,
            form_clusters=model.keys,
            train_result=TrainResult._from_generated(model.train_result)
        )


class TrainResult(object):
    def __init__(self, **kwargs):
        self.documents = kwargs.get('documents', None)
        self.training_errors = kwargs.get('training_errors', None)

    @classmethod
    def _from_generated(cls, train):
        return cls(
            documents=[TrainingDocumentInfo._from_generated(doc) for doc in train.training_documents],
            training_errors=ErrorInformation._from_generated(train.errors)
        )


class TrainingDocumentInfo(object):

    def __init__(self, **kwargs):
        self.document_name = kwargs.get('document_name', None)
        self.status = kwargs.get('status', None)
        self.pages = kwargs.get('pages', None)
        self.document_errors = kwargs.get('document_errors', None)

    @classmethod
    def _from_generated(cls, doc):
        return cls(
            document_name=doc.document_name,
            status=doc.status,
            pages=doc.pages,
            document_errors=ErrorInformation._from_generated(doc.errors)
        )


class ErrorInformation(object):
    def __init__(self, **kwargs):
        self.code = kwargs.get('code', None)
        self.message = kwargs.get('message', None)

    @classmethod
    def _from_generated(cls, err):
        if err:
            return [cls(
                code=error.code,
                message=error.message
            ) for error in err.errors]
        return []


class LabeledCustomModel(object):
    def __init__(self, **kwargs):
        self.model_id = kwargs.get('model_id', None)
        self.status = kwargs.get('status', None)
        self.created_date_time = kwargs.get('created_date_time', None)
        self.last_updated_date_time = kwargs.get('last_updated_date_time', None)
        self.train_result = kwargs.get('train_result', None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            model_id=model.model_info.model_id,
            status=model.model_info.status,
            created_date_time=model.model_info.created_date_time,
            last_updated_date_time=model.model_info.last_updated_date_time,
            train_result=LabeledTrainResult._from_generated(model.train_result)
        )


class LabeledTrainResult(object):
    def __init__(self, **kwargs):
        self.documents = kwargs.get('documents', None)
        self.fields = kwargs.get('fields', None)
        self.average_model_accuracy = kwargs.get('average_model_accuracy', None)
        self.training_errors = kwargs.get('training_errors', None)

    @classmethod
    def _from_generated(cls, train):
        return cls(
            documents=[TrainingDocumentInfo._from_generated(doc) for doc in train.training_documents],
            fields=FieldNames._from_generated(train.fields),
            average_model_accuracy=train.average_model_accuracy,
            training_errors=ErrorInformation._from_generated(train.errors)
        )


class FieldNames(object):
    def __init__(self, **kwargs):
        self.field_name = kwargs.get('field_name', None)
        self.accuracy = kwargs.get('accuracy', None)

    @classmethod
    def _from_generated(cls, fields):
        if fields:
            return [cls(
                field_name=field.field_name,
                accuracy=field.accuracy
            ) for field in fields]


class ExtractedPage(object):
    def __init__(self, **kwargs):
        self.fields = kwargs.get('fields', None)
        self.tables = kwargs.get('tables', None)
        self.page_number = kwargs.get('page_number', None)
        self.form_type_id = kwargs.get('form_type_id', None)


class ExtractedField(object):
    def __init__(self, **kwargs):
        self.label = kwargs.get('label', None)
        self.label_outline = kwargs.get('label_outline', None)
        self.label_raw_field = kwargs.get('label_raw_field', None)
        self.value = kwargs.get('value', None)
        self.value_outline = kwargs.get('value_outline', None)
        self.value_raw_field = kwargs.get('value_raw_field', None)
        self.confidence = kwargs.get('confidence', None)

    @classmethod
    def _from_generated(cls, field, read_result, include_raw):
        return cls(
            label=field.key.text,
            label_outline=field.key.bounding_box,
            label_raw_field=get_raw_field(field.key, read_result) if include_raw else None,
            value=field.value.text,
            value_outline=field.value.bounding_box,
            value_raw_field=get_raw_field(field.value, read_result) if include_raw else None,
            confidence=field.confidence
        )

    @classmethod
    def _from_labeled_generated(cls, label, read_result, include_raw):
        return cls(
            label=label[0],
            label_outline=None,
            label_raw_field=None,
            value=label[1].text,
            value_outline=label[1].bounding_box,
            value_raw_field=get_raw_field(label[1], read_result) if include_raw else None,
            confidence=label[1].confidence
        )


class ModelInfo(object):
    def __init__(self, **kwargs):
        self.model_id = kwargs.get('model_id', None)
        self.status = kwargs.get('status', None)
        self.created_date_time = kwargs.get('created_date_time', None)
        self.last_updated_date_time = kwargs.get('last_updated_date_time', None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            model_id=model.model_id,
            status=model.status,
            created_date_time=model.created_date_time,
            last_updated_date_time=model.last_updated_date_time
        )


class ModelsSummary(object):
    def __init__(self, **kwargs):
        self.count = kwargs.get('count', None)
        self.limit = kwargs.get('limit', None)
        self.last_updated_date_time = kwargs.get('last_updated_date_time', None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            count=model.count,
            limit=model.limit,
            last_updated_date_time=model.last_updated_date_time
        )
