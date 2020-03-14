# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from re import findall
from ._helpers import get_receipt_field_value


def get_elements(field, ocr_result):
    elements = []
    try:
        for item in field.elements:
            extracted_word = None
            nums = [int(s) for s in findall(r'\d+', item)]
            read = nums[0]
            line = nums[1]
            if len(nums) == 3:
                word = nums[2]
                ocr_word = ocr_result[read].lines[line].words[word]
                extracted_word = ExtractedWord._from_generated(ocr_word, page=read+1)
            ocr_line = ocr_result[read].lines[line]
            extracted_line = ExtractedLine._from_generated(ocr_line, page=read+1)

            if extracted_word:
                elements.append(extracted_word)
            else:
                elements.append(extracted_line)
        return elements
    except TypeError:
        return None


class DictMixin(object):

    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __repr__(self):
        return str(self)

    def __len__(self):
        return len(self.keys())

    def __delitem__(self, key):
        self.__dict__[key] = None

    def __eq__(self, other):
        """Compare objects by comparing all attributes."""
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def __ne__(self, other):
        """Compare objects by comparing all attributes."""
        return not self.__eq__(other)

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if not k.startswith('_')})

    def has_key(self, k):
        return k in self.__dict__

    def update(self, *args, **kwargs):
        return self.__dict__.update(*args, **kwargs)

    def keys(self):
        return [k for k in self.__dict__ if not k.startswith('_')]

    def values(self):
        return [v for k, v in self.__dict__.items() if not k.startswith('_')]

    def items(self):
        return [(k, v) for k, v in self.__dict__.items() if not k.startswith('_')]

    def get(self, key, default=None):
        if key in self.__dict__:
            return self.__dict__[key]
        return default


class ExtractedReceipt(DictMixin):

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
        self.page_range = kwargs.get("page_range", None)
        self.page_metadata = kwargs.get("page_metadata", None)


class FieldValue(object):

    def __init__(self, **kwargs):
        self.value = kwargs.get("value", None)
        self.text = kwargs.get("text", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.confidence = kwargs.get("confidence", None)
        self.page_number = kwargs.get("page_number", None)
        self.elements = kwargs.get("elements", None)

    @classmethod
    def _from_generated(cls, field, read_result, include_raw):
        if field is None:
            return field
        return cls(
            value=get_receipt_field_value(field),
            text=field.text,
            bounding_box=field.bounding_box,
            confidence=field.confidence,
            page_number=field.page,
            elements=get_elements(field, read_result) if include_raw else None
        )


class ReceiptItem(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.quantity = kwargs.get("quantity", None)
        self.item_price = kwargs.get('item_price', None)
        self.total_price = kwargs.get("total_price", None)

    @classmethod
    def _from_generated(cls, items, read_result, include_raw):
        try:
            receipt_item = items.value_array
            return [cls(
                name=FieldValue._from_generated(item.value_object.get("Name"), read_result, include_raw),
                quantity=FieldValue._from_generated(item.value_object.get("Quantity"), read_result, include_raw),
                item_price=FieldValue._from_generated(item.value_object.get("Price"), read_result, include_raw),
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
        self.page_number = kwargs.get("page_number", None)

    @classmethod
    def _from_generated(cls, line, page):
        return cls(
            text=line.text,
            bounding_box=line.bounding_box,
            language=line.language,
            page_number=page,
            words=[ExtractedWord._from_generated(word, page) for word in line.words]
        )


class ExtractedWord(object):
    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.confidence = kwargs.get("confidence", None)
        self.page_number = kwargs.get("page_number", None)

    @classmethod
    def _from_generated(cls, word, page):
        return cls(
            text=word.text,
            bounding_box=word.bounding_box,
            confidence=word.confidence,
            page_number=page
        )


class ExtractedLayoutPage(object):
    def __init__(self, **kwargs):
        self.tables = kwargs.get("tables", None)
        self.page_number = kwargs.get("page_number", None)
        self.page_metadata = kwargs.get("page_metadata", None)


class ExtractedTable(object):
    def __init__(self, **kwargs):
        self.cells = kwargs.get("cells", None)
        self.row_count = kwargs.get("row_count", None)
        self.column_count = kwargs.get("column_count", None)


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
        self.elements = kwargs.get('elements', None)

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
            is_header=cell.is_header or False,
            is_footer=cell.is_footer or False,
            elements=get_elements(cell, read_result) if include_raw else None
        )


class CustomModel(object):
    def __init__(self, **kwargs):
        self.model_id = kwargs.get('model_id', None)
        self.status = kwargs.get('status', None)
        self.created_on = kwargs.get('created_on', None)
        self.last_updated_on = kwargs.get('last_updated_on', None)
        self.train_result = kwargs.get('train_result', None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            model_id=model.model_info.model_id,
            status=model.model_info.status,
            created_on=model.model_info.created_date_time,
            last_updated_on=model.model_info.last_updated_date_time,
            train_result=TrainResult._from_generated(model.train_result, model.keys)
        )


class TrainResult(object):
    def __init__(self, **kwargs):
        self.extracted_fields = kwargs.get("extracted_fields", None)
        self.documents = kwargs.get('documents', None)
        self.training_errors = kwargs.get('training_errors', None)

    @classmethod
    def _from_generated(cls, train, keys):
        return cls(
            extracted_fields=FormTypeFields._from_generated(keys),
            documents=[TrainingDocumentInfo._from_generated(doc) for doc in train.training_documents],
            training_errors=FormRecognizerError._from_generated(train.errors)
        )


class FormTypeFields(object):
    def __init__(self, **kwargs):
        self.form_type_id = kwargs.get("form_type_id", None)
        self.fields = kwargs.get("fields", None)

    @classmethod
    def _from_generated(cls, keys):
        try:
            clusters = keys.clusters
            return [cls(
                form_type_id=cluster_id,
                fields=fields
            ) for cluster_id, fields in clusters.items()]
        except AttributeError:
            return None


class TrainingDocumentInfo(object):

    def __init__(self, **kwargs):
        self.document_name = kwargs.get('document_name', None)
        self.status = kwargs.get('status', None)
        self.page_count = kwargs.get('page_count', None)
        self.errors = kwargs.get('errors', None)

    @classmethod
    def _from_generated(cls, doc):
        return cls(
            document_name=doc.document_name,
            status=doc.status,
            page_count=doc.pages,
            errors=FormRecognizerError._from_generated(doc.errors)
        )


class FormRecognizerError(object):
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


class CustomLabeledModel(object):
    def __init__(self, **kwargs):
        self.model_id = kwargs.get('model_id', None)
        self.status = kwargs.get('status', None)
        self.created_on = kwargs.get('created_on', None)
        self.last_updated_on = kwargs.get('last_updated_on', None)
        self.train_result = kwargs.get('train_result', None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            model_id=model.model_info.model_id,
            status=model.model_info.status,
            created_on=model.model_info.created_date_time,
            last_updated_on=model.model_info.last_updated_date_time,
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
            training_errors=FormRecognizerError._from_generated(train.errors)
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
        self.name = kwargs.get('name', None)
        self.value = kwargs.get('value', None)
        self.confidence = kwargs.get('confidence', None)

    @classmethod
    def _from_generated(cls, field, read_result, include_raw):
        return cls(
            name=ExtractedText._from_generated(field.key, read_result, include_raw),
            value=ExtractedText._from_generated(field.value, read_result, include_raw),
            confidence=field.confidence
        )


class ExtractedText:
    def __init__(self, **kwargs):
        self.text = kwargs.get('model_id', None)
        self.bounding_box = kwargs.get('model_id', None)
        self.elements = kwargs.get('model_id', None)

    @classmethod
    def _from_generated(cls, field, read_result, include_raw):
        return cls(
            text=field.text,
            bounding_box=field.bounding_box,
            elements=get_elements(field.elements, read_result) if include_raw else None
        )


class LabelValue(object):
    def __init__(self, **kwargs):
        self.text = kwargs.get('text', None)
        self.value = kwargs.get('text', None)
        self.bounding_box = kwargs.get('bounding_box', None)
        self.confidence = kwargs.get('confidence', None)
        self.page_number = kwargs.get('page_number', None)
        self.elements = kwargs.get('raw_field', None)

    @classmethod
    def _from_generated(cls, label, read_result, include_raw):
        return cls(
            text=label.text,
            value=label.value,
            bounding_box=label.bounding_box,
            confidence=label.confidence,
            page_number=label.page,
            elements=get_elements(label, read_result) if include_raw else None
        )


class ModelInfo(object):
    def __init__(self, **kwargs):
        self.model_id = kwargs.get('model_id', None)
        self.status = kwargs.get('status', None)
        self.created_on = kwargs.get('created_on', None)
        self.last_updated_on = kwargs.get('last_updated_on', None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            model_id=model.model_id,
            status=model.status,
            created_on=model.created_date_time,
            last_updated_on=model.last_updated_date_time
        )


class ModelsSummary(object):
    def __init__(self, **kwargs):
        self.count = kwargs.get('count', None)
        self.limit = kwargs.get('limit', None)
        self.last_updated_on = kwargs.get('last_updated_on', None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            count=model.count,
            limit=model.limit,
            last_updated_on=model.last_updated_date_time
        )


class PageMetadata(object):
    def __init__(self, **kwargs):
        self.page_number = kwargs.get('page_number', None)
        self.angle = kwargs.get('angle', None)
        self.width = kwargs.get('width', None)
        self.height = kwargs.get('height', None)
        self.unit = kwargs.get('unit', None)
        self.language = kwargs.get('language', None)
        self.lines = kwargs.get("lines", None)

    @classmethod
    def _from_generated_page_index(cls, read_result, page_index):
        return cls(
            page_number=read_result[page_index].page,
            angle=read_result[page_index].angle,
            width=read_result[page_index].width,
            height=read_result[page_index].height,
            unit=read_result[page_index].unit,
            language=read_result[page_index].language,
            lines=[ExtractedLine._from_generated(line, page_index+1) for line in read_result[page_index].lines]
        )

    @classmethod
    def _all_pages(cls, read_result):
        return [cls(
            page_number=page.page,
            angle=page.angle,
            width=page.width,
            height=page.height,
            unit=page.unit,
            language=page.language,
            lines=[ExtractedLine._from_generated(line, page.page) for line in read_result.lines]
        ) for page in read_result]


class ExtractedForm(object):
    def __init__(self, **kwargs):
        self.fields = kwargs.get('fields', None)
        self.tables = kwargs.get('tables', None)
        self.page_metadata = kwargs.get('page_metadata', None)
        self.page_range = kwargs.get('page_range', None)
