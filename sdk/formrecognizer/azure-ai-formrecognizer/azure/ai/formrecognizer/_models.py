# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from re import findall
from collections import namedtuple
from enum import Enum
from ._helpers import get_field_scalar_value


PageRange = namedtuple("PageRange", "first_page last_page")
Point = namedtuple("Point", "x y")


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


class LengthUnit(str, Enum):
    """The unit used by the width, height and boundingBox properties. For images, the unit is "pixel".
    For PDF, the unit is "inch".
    """

    pixel = "pixel"
    inch = "inch"


class TrainStatus(str, Enum):
    succeeded = "succeeded"
    partially_succeeded = "partiallySucceeded"
    failed = "failed"


class ModelStatus(str, Enum):
    creating = "creating"
    ready = "ready"
    invalid = "invalid"


class BoundingBox:
    def __init__(self, **kwargs):
        self.top_left = kwargs.get("top_left", None)
        self.top_right = kwargs.get("top_right", None)
        self.bottom_right = kwargs.get("bottom_right", None)
        self.bottom_left = kwargs.get("bottom_left", None)

    @classmethod
    def _from_generated(cls, box):
        if box is None:
            return box
        return cls(
            top_left=Point(x=box[0], y=box[1]),
            top_right=Point(x=box[2], y=box[3]),
            bottom_right=Point(x=box[4], y=box[5]),
            bottom_left=Point(x=box[6], y=box[7]),
        )


class ExtractedReceipt(object):  # pylint: disable=too-many-instance-attributes

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
    def _from_generated(cls, field, elements):
        if field is None:
            return field

        if field.type == "array":
            return [FieldValue._from_generated(field, elements) for field in field.value_array]

        if field.type == "object":
            return {key: FieldValue._from_generated(value, elements) for key, value in field.value_object.items()}
        return cls(
            value=get_field_scalar_value(field),
            text=field.text,
            bounding_box=BoundingBox._from_generated(field.bounding_box),
            confidence=field.confidence,
            page_number=field.page,
            elements=get_elements(field, elements) if elements else None
        )


class ReceiptType(object):
    def __init__(self, **kwargs):
        self.type = kwargs.get("type", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, item):
        if item:
            return cls(
                type=get_field_scalar_value(item),
                confidence=item.confidence
            )
        return item


class ReceiptItem(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.quantity = kwargs.get("quantity", None)
        self.item_price = kwargs.get('item_price', None)
        self.total_price = kwargs.get("total_price", None)

    @classmethod
    def _from_generated(cls, items, elements):
        try:
            receipt_item = items.value_array
            return [cls(
                name=FieldValue._from_generated(item.value_object.get("Name"), elements),
                quantity=FieldValue._from_generated(item.value_object.get("Quantity"), elements),
                item_price=FieldValue._from_generated(item.value_object.get("Price"), elements),
                total_price=FieldValue._from_generated(item.value_object.get("TotalPrice"), elements),
            ) for item in receipt_item]
        except AttributeError:
            return None


class ExtractedLine(object):
    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.words = kwargs.get("words", None)
        self.page_number = kwargs.get("page_number", None)

    @classmethod
    def _from_generated(cls, line, page):
        return cls(
            text=line.text,
            bounding_box=BoundingBox._from_generated(line.bounding_box),
            page_number=page,
            words=[ExtractedWord._from_generated(word, page) for word in line.words] if line.words else None
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
            bounding_box=BoundingBox._from_generated(word.bounding_box),
            confidence=word.confidence,
            page_number=page
        )


class PageMetadata(object):
    def __init__(self, **kwargs):
        self.page_number = kwargs.get('page_number', None)
        self.angle = kwargs.get('angle', None)
        self.width = kwargs.get('width', None)
        self.height = kwargs.get('height', None)
        self.unit = kwargs.get('unit', None)
        self.lines = kwargs.get("lines", None)

    @classmethod
    def _from_generated_page_index(cls, read_result, page_index):
        return cls(
            page_number=read_result[page_index].page,
            angle=read_result[page_index].angle,
            width=read_result[page_index].width,
            height=read_result[page_index].height,
            unit=LengthUnit(read_result[page_index].unit),
            lines=[ExtractedLine._from_generated(line, page=page_index+1)
                   for line in read_result[page_index].lines] if read_result[page_index].lines else None
        )

    @classmethod
    def _from_generated(cls, read_result):
        return [cls(
            page_number=page.page,
            angle=page.angle,
            width=page.width,
            height=page.height,
            unit=LengthUnit(page.unit),
            lines=[ExtractedLine._from_generated(line, page=page.page) for line in page.lines] if page.lines else None
        ) for page in read_result]


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
        self.page_number = kwargs.get("page_number", None)


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
    def _from_generated(cls, cell, elements):
        return cls(
            text=cell.text,
            row_index=cell.row_index,
            column_index=cell.column_index,
            row_span=cell.row_span or 1,
            column_span=cell.column_span or 1,
            bounding_box=BoundingBox._from_generated(cell.bounding_box),
            confidence=cell.confidence,
            is_header=cell.is_header or False,
            is_footer=cell.is_footer or False,
            elements=get_elements(cell, elements) if elements else None
        )


class CustomModel(object):
    def __init__(self, **kwargs):
        self.model_id = kwargs.get('model_id', None)
        self.status = kwargs.get('status', None)
        self.created_on = kwargs.get('created_on', None)
        self.last_updated_on = kwargs.get('last_updated_on', None)
        self.extracted_fields = kwargs.get("extracted_fields", None)
        self.training_info = kwargs.get('training_info', None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            model_id=model.model_info.model_id,
            status=ModelStatus(model.model_info.status),
            created_on=model.model_info.created_date_time,
            last_updated_on=model.model_info.last_updated_date_time,
            extracted_fields=FormFields._from_generated(model.keys),
            training_info=TrainingInfo._from_generated(model.train_result)
        )


class TrainingInfo(object):
    def __init__(self, **kwargs):
        self.documents = kwargs.get('documents', None)
        self.training_errors = kwargs.get('training_errors', None)

    @classmethod
    def _from_generated(cls, train):
        if train:
            return cls(
                documents=[TrainingDocumentInfo._from_generated(doc)
                           for doc in train.training_documents] if train.training_documents else None,
                training_errors=FormRecognizerError._from_generated(train.errors)
            )
        return train


class FormFields(object):
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
            status=TrainStatus(doc.status),
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
            ) for error in err]
        return err


class CustomLabeledModel(object):
    def __init__(self, **kwargs):
        self.model_id = kwargs.get('model_id', None)
        self.status = kwargs.get('status', None)
        self.created_on = kwargs.get('created_on', None)
        self.last_updated_on = kwargs.get('last_updated_on', None)
        self.fields = kwargs.get('fields', None)
        self.average_model_accuracy = kwargs.get('average_model_accuracy', None)
        self.training_info = kwargs.get('training_info', None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            model_id=model.model_info.model_id,
            status=ModelStatus(model.model_info.status),
            created_on=model.model_info.created_date_time,
            last_updated_on=model.model_info.last_updated_date_time,
            fields=FieldInfo._from_generated(model.train_result) if model.train_result else None,
            average_model_accuracy=model.train_result.average_model_accuracy if model.train_result else None,
            training_info=TrainingInfo._from_generated(model.train_result) if model.train_result else None
        )


class FieldInfo(object):
    def __init__(self, **kwargs):
        self.field_name = kwargs.get('field_name', None)
        self.accuracy = kwargs.get('accuracy', None)

    @classmethod
    def _from_generated(cls, model):
        if model:
            return [cls(
              field_name=field.field_name,
              accuracy=field.accuracy
            ) for field in model.fields]
        return model


class ExtractedPage(object):
    def __init__(self, **kwargs):
        self.fields = kwargs.get('fields', None)
        self.tables = kwargs.get('tables', None)
        self.page_metadata = kwargs.get('page_metadata', None)
        self.page_number = kwargs.get('page_number', None)
        self.form_type_id = kwargs.get('form_type_id', None)


class ExtractedField(object):
    def __init__(self, **kwargs):
        self.name = kwargs.get('name', None)
        self.value = kwargs.get('value', None)
        self.confidence = kwargs.get('confidence', None)

    @classmethod
    def _from_generated(cls, field, elements):
        return cls(
            name=ExtractedText._from_generated(field.key, elements),
            value=ExtractedText._from_generated(field.value, elements),
            confidence=field.confidence
        )


class ExtractedText(object):
    def __init__(self, **kwargs):
        self.text = kwargs.get('text', None)
        self.bounding_box = kwargs.get('bounding_box', None)
        self.elements = kwargs.get('elements', None)

    @classmethod
    def _from_generated(cls, field, elements):
        return cls(
            text=field.text,
            bounding_box=BoundingBox._from_generated(field.bounding_box),
            elements=get_elements(field.elements, elements) if elements else None
        )


class ExtractedLabeledForm(object):
    def __init__(self, **kwargs):
        self.fields = kwargs.get('fields', None)
        self.page_range = kwargs.get('page_range', None)
        self.tables = kwargs.get('tables', None)
        self.page_metadata = kwargs.get("page_metadata", None)


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
            status=ModelStatus(model.status),
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
