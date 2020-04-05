# coding=utf-8
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access

from enum import Enum
from collections import namedtuple
import re
import six
from ._helpers import get_field_scalar_value


def get_elements(field, read_result):
    text_elements = []

    for item in field.elements:
        nums = [int(s) for s in re.findall(r"\d+", item)]
        read = nums[0]
        line = nums[1]
        if len(nums) == 3:
            word = nums[2]
            ocr_word = read_result[read].lines[line].words[word]
            extracted_word = FormWord._from_generated(ocr_word, page=read + 1)
            text_elements.append(extracted_word)
            continue
        ocr_line = read_result[read].lines[line]
        extracted_line = FormLine._from_generated(ocr_line, page=read + 1)
        text_elements.append(extracted_line)
    return text_elements


class LengthUnit(str, Enum):
    """The unit used by the width, height and bounding box properties. For images, the unit is "pixel".
    For PDF, the unit is "inch".
    """

    pixel = "pixel"
    inch = "inch"


class TrainStatus(str, Enum):
    """Status of the training operation.
    """

    succeeded = "succeeded"
    partially_succeeded = "partiallySucceeded"
    failed = "failed"


class ModelStatus(str, Enum):
    """Status of the model.
    """

    creating = "creating"
    ready = "ready"
    invalid = "invalid"


class Point(namedtuple("Point", "x y")):
    """The x, y coordinate of a point of on a bounding box.

    :ivar float x: x-coordinate
    :ivar float y: y-coordinate
    """

    __slots__ = ()

    def __new__(cls, x, y):
        return super(Point, cls).__new__(cls, x, y)


class BoundingBox(namedtuple("BoundingBox", ["top_left", "top_right", "bottom_right", "bottom_left"])):
    """The quadrangle bounding box that outlines the text.
    Units are in pixels for images and inches for PDF.

    :ivar ~azure.ai.formrecognizer.Point top_left:
        The x, y coordinates of the upper left point of the bounding box.
    :ivar ~azure.ai.formrecognizer.Point top_right:
        The x, y coordinates of the upper right point of the bounding box.
    :ivar ~azure.ai.formrecognizer.Point bottom_right:
        The x, y coordinates of the lower right point of the bounding box.
    :ivar ~azure.ai.formrecognizer.Point bottom_left:
        The x, y coordinates of the lower left point of the bounding box.
    """

    __slots__ = ()

    def __new__(cls, top_left, top_right, bottom_right, bottom_left):
        return super(BoundingBox, cls).__new__(
            cls, top_left, top_right, bottom_right, bottom_left
        )


class PageRange(namedtuple("PageRange", "first_page last_page")):
    """The 1 based page range of the document.

    :ivar int first_page: The first page of the document.
    :ivar int last_page: The last page of the document.

    """

    __slots__ = ()

    def __new__(cls, first_page, last_page):
        return super(PageRange, cls).__new__(cls, first_page, last_page)


class RecognizedForm(object):
    """Represents a recognized form.

    :ivar str form_type: The type of form.
    :ivar fields:
        A dictionary of the fields.
    :vartype fields: dict[str, ~azure.ai.formrecognizer.FormField]
    :ivar ~azure.ai.formrecognizer.PageRange page_range:
        The first and last page of the input form.
    :ivar list[~azure.ai.formrecognizer.FormPage] pages:
        Contains page metadata such as page width, length, angle, unit.
        If `include_text_content=True` is passed, contains a list
        of extracted text result for each page in the input document.
    """
    def __init__(self, **kwargs):
        self.fields = kwargs.get("fields", None)
        self.form_type = kwargs.get("form_type", None)
        self.page_range = kwargs.get("page_range", None)
        self.pages = kwargs.get("pages", None)


class USReceipt(object):  # pylint: disable=too-many-instance-attributes
    """Extracted fields and values found on the input US receipt.

    :ivar ~azure.ai.formrecognizer.FormField merchant_address:
        The address of the merchant.
    :ivar ~azure.ai.formrecognizer.FormField merchant_name:
        The name of the merchant.
    :ivar ~azure.ai.formrecognizer.FormField merchant_phone_number:
        The phone number associated with the merchant.
    :ivar ~azure.ai.formrecognizer.USReceiptType receipt_type:
        The reciept type and confidence.
    :ivar list[~azure.ai.formrecognizer.USReceiptItem] receipt_items:
        The purchased items found on the receipt.
    :ivar ~azure.ai.formrecognizer.FormField subtotal:
        The subtotal found on the receipt.
    :ivar ~azure.ai.formrecognizer.FormField tax:
        The tax value found on the receipt.
    :ivar ~azure.ai.formrecognizer.FormField tip:
        The tip value found on the receipt.
    :ivar ~azure.ai.formrecognizer.FormField total:
        The total amount found on the receipt.
    :ivar ~azure.ai.formrecognizer.FormField transaction_date:
        The transaction date of the sale.
    :ivar ~azure.ai.formrecognizer.FormField transaction_time:
        The transaction time of the sale.
    :ivar fields:
        A dictionary of the fields.
    :vartype fields: dict[str, ~azure.ai.formrecognizer.FormField]
    :ivar ~azure.ai.formrecognizer.PageRange page_range:
        The first and last page of the input form.
    :ivar list[~azure.ai.formrecognizer.FormPage] pages:
        Contains page metadata such as page width, length, angle, unit.
        If `include_text_content=True` is passed, contains a list
        of extracted text result for each page in the input document.
    :ivar str form_type: The type of form.
    """

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
        self.pages = kwargs.get("pages", None)
        self.form_type = kwargs.get("form_type", None)


class FormField(object):
    """Represents the recognized field and its value.

    :ivar ~azure.ai.formrecognizer.FieldText field_label:
        Contains the text, bounding box, and text content of the field label.
    :ivar ~azure.ai.formrecognizer.FieldText field_value:
        Contains the text, bounding box, and text content of the field value.
    :ivar str name: The name of the field or label.
    :ivar value:
        The value for the recognized field. Possible types include: 'string', 'date', 'time',
        'phoneNumber', 'number', 'integer`, `~azure.ai.formrecognizer.FormField`, or
        list[`~azure.ai.formrecognizer.FormField`].
    :vartype value: str, int, float, ~datetime.date, ~datetime.time,
        `~azure.ai.formrecognizer.FormField`, or list[`~azure.ai.formrecognizer.FormField`]
    :ivar float confidence: Confidence score.
    :ivar int page_number:
        The 1-based page number in the input document.
    """

    def __init__(self, **kwargs):
        self.field_label = kwargs.get("field_label", None)
        self.field_value = kwargs.get("field_value", None)
        self.name = kwargs.get("name", None)
        self.value = kwargs.get("value", None)
        self.confidence = kwargs.get("confidence", None)
        self.page_number = kwargs.get("page_number", None)

    @classmethod
    def _from_generated(cls, field, value, read_result):
        if value is None:
            return value

        if value.type == "array":
            return [
                FormField._from_generated(field, value, read_result)
                for value in value.value_array
            ]

        if value.type == "object":
            return {
                key: FormField._from_generated(key, value, read_result)
                for key, value in value.value_object.items()
            }
        return cls(
            field_label=FieldText._from_generated(field, read_result),
            field_value=FieldText._from_generated(value, read_result),
            value=get_field_scalar_value(value),
            name=field,
            confidence=value.confidence,
            page_number=value.page,
        )


class FieldText(object):
    """Represents the properties of a field or value.

    :ivar int page_number:
        The 1-based page number in the input document.
    :ivar str text: The string representation of the field or value.
    :ivar ~azure.ai.formrecognizer.BoundingBox bounding_box:
        Bounding box of the field or value.
    :ivar text_content:
        When `include_text_content` is set to true, a list of references to the text
        elements constituting this field or value.
    :vartype text_content: list[~azure.ai.formrecognizer.FormWord, ~azure.ai.formrecognizer.FormLine]
    """

    def __init__(self, **kwargs):
        self.page_number = kwargs.get("page_number", None)
        self.text = kwargs.get("text", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.text_content = kwargs.get("text_content", None)

    @classmethod
    def _from_generated(cls, field, read_result):
        if isinstance(field, six.string_types):
            return cls(
                text=field
            )
        return cls(
            page_number=field.page,
            text=field.text,
            bounding_box=BoundingBox(
                top_left=Point(x=field.bounding_box[0], y=field.bounding_box[1]),
                top_right=Point(x=field.bounding_box[2], y=field.bounding_box[3]),
                bottom_right=Point(x=field.bounding_box[4], y=field.bounding_box[5]),
                bottom_left=Point(x=field.bounding_box[6], y=field.bounding_box[7])
            ) if field.bounding_box else None,
            text_content=get_elements(field, read_result) if field.elements else None
        )


class FormPage(object):
    """Page metadata and text lines extracted from a page in the input document.

    :ivar int page_number:
        The 1-based page number in the input document.
    :ivar float text_angle:
        The general orientation of the text in clockwise direction, measured in
        degrees between (-180, 180].
    :ivar float width:
        The width of the image/PDF in pixels/inches, respectively.
    :ivar float height:
        The height of the image/PDF in pixels/inches, respectively.
    :ivar ~azure.ai.formrecognizer.LengthUnit unit:
        The unit used by the width, height and bounding box properties. For
        images, the unit is "pixel". For PDF, the unit is "inch".
    :ivar list[~azure.ai.formrecognizer.FormTable] tables:
        A list of extracted tables contained in a page.
    :ivar list[~azure.ai.formrecognizer.FormLine] lines:
        When `include_text_content` is set to true, a list of recognized text lines. The
        maximum number of lines returned is 300 per page. The lines are sorted top to bottom, left to
        right, although in certain cases proximity is treated with higher priority. As the sorting
        order depends on the detected text, it may change across images and OCR version updates. Thus,
        business logic should be built upon the actual line location instead of order.
    """

    def __init__(self, **kwargs):
        self.page_number = kwargs.get("page_number", None)
        self.text_angle = kwargs.get("text_angle", None)
        self.width = kwargs.get("width", None)
        self.height = kwargs.get("height", None)
        self.unit = kwargs.get("unit", None)
        self.tables = kwargs.get("tables", None)
        self.lines = kwargs.get("lines", None)

    @classmethod
    def _from_generated_receipt(cls, read_result):
        return [cls(
            page_number=page.page,
            text_angle=page.angle,
            width=page.width,
            height=page.height,
            unit=page.unit,
            lines=[FormLine._from_generated(line, page=page.page) for line in page.lines] if page.lines else None
        ) for page in read_result]

    @classmethod
    def _from_generated_page_index(cls, read_result, page_index):
        return cls(
            page_number=read_result[page_index].page,
            text_angle=read_result[page_index].angle,
            width=read_result[page_index].width,
            height=read_result[page_index].height,
            unit=read_result[page_index].unit,
            lines=[FormLine._from_generated(line, page=page_index+1)
                   for line in read_result[page_index].lines] if read_result[page_index].lines else None
        )

    @classmethod
    def _from_generated_form(cls, read_result):
        return [cls(
            page_number=page.page,
            text_angle=page.angle,
            width=page.width,
            height=page.height,
            unit=page.unit,
            tables=None,  # TODO: add tables from page_result
            lines=[FormLine._from_generated(line, page=page.page) for line in page.lines] if page.lines else None
        ) for page in read_result]


class FormLine(object):
    """An object representing an extracted text line.

    :ivar str text: The text content of the line.
    :ivar ~azure.ai.formrecognizer.BoundingBox bounding_box:
        Bounding box of an extracted line.
    :ivar list[~azure.ai.formrecognizer.FormWord] words:
        List of words in the text line.
    :ivar int page_number:
        The 1-based page number in the input document.
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.words = kwargs.get("words", None)
        self.page_number = kwargs.get("page_number", None)

    @classmethod
    def _from_generated(cls, line, page):
        return cls(
            text=line.text,
            bounding_box=BoundingBox(
                top_left=Point(x=line.bounding_box[0], y=line.bounding_box[1]),
                top_right=Point(x=line.bounding_box[2], y=line.bounding_box[3]),
                bottom_right=Point(x=line.bounding_box[4], y=line.bounding_box[5]),
                bottom_left=Point(x=line.bounding_box[6], y=line.bounding_box[7])
            ) if line.bounding_box else None,
            page_number=page,
            words=[FormWord._from_generated(word, page) for word in line.words] if line.words else None
        )


class FormWord(object):
    """An object representing a word.

    :ivar str text: The text content of the word.
    :ivar ~azure.ai.formrecognizer.BoundingBox bounding_box:
        Bounding box of an extracted word.
    :ivar float confidence: Confidence value.
    :ivar int page_number:
        The 1-based page number in the input document.
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.confidence = kwargs.get("confidence", None)
        self.page_number = kwargs.get("page_number", None)

    @classmethod
    def _from_generated(cls, word, page):
        return cls(
            text=word.text,
            bounding_box=BoundingBox(
                top_left=Point(x=word.bounding_box[0], y=word.bounding_box[1]),
                top_right=Point(x=word.bounding_box[2], y=word.bounding_box[3]),
                bottom_right=Point(x=word.bounding_box[4], y=word.bounding_box[5]),
                bottom_left=Point(x=word.bounding_box[6], y=word.bounding_box[7])
            ) if word.bounding_box else None,
            confidence=word.confidence,
            page_number=page
        )


class USReceiptType(object):
    """The type of the analyzed US receipt and the confidence
    value of that type.

    :ivar str type: The type of the receipt. For example, "Itemized",
        "CreditCard", "Gas", "Parking", "Gas", "Other".
    :ivar float confidence: The confidence score of the receipt type.
    """

    def __init__(self, **kwargs):
        self.type = kwargs.get("type", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, item):
        return cls(
            type=item.value_string,
            confidence=item.confidence) if item else None


class USReceiptItem(object):
    """A receipt item on a US sales receipt.
    Contains the item name, quantity, item price, and total price.

    :ivar ~azure.ai.formrecognizer.FormField name:
        The name of the item.
    :ivar ~azure.ai.formrecognizer.FormField quantity:
        The quantity purchased of the item.
    :ivar ~azure.ai.formrecognizer.FormField price:
        The individual price of the item.
    :ivar ~azure.ai.formrecognizer.FormField total_price:
        The total price of the item(s).
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.quantity = kwargs.get("quantity", None)
        self.price = kwargs.get("price", None)
        self.total_price = kwargs.get("total_price", None)

    @classmethod
    def _from_generated(cls, items, read_result):
        try:
            receipt_item = items.value_array
            return [cls(
                name=FormField._from_generated("Name", item.value_object.get("Name"), read_result),
                quantity=FormField._from_generated("Quantity", item.value_object.get("Quantity"), read_result),
                price=FormField._from_generated("Price", item.value_object.get("Price"), read_result),
                total_price=FormField._from_generated("TotalPrice", item.value_object.get("TotalPrice"), read_result),
            ) for item in receipt_item]
        except AttributeError:
            return None


class ExtractedLine(object):
    """An object representing an extracted text line.

    :ivar str text: The text content of the line.
    :ivar ~azure.ai.formrecognizer.BoundingBox bounding_box:
        Bounding box of an extracted line.
    :ivar list[~azure.ai.formrecognizer.ExtractedWord] words:
        List of words in the text line.
    :ivar int page_number:
        The 1-based page number in the input document.
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.words = kwargs.get("words", None)
        self.page_number = kwargs.get("page_number", None)

    @classmethod
    def _from_generated(cls, line, page):
        return cls(
            text=line.text,
            bounding_box=BoundingBox(
                top_left=Point(x=line.bounding_box[0], y=line.bounding_box[1]),
                top_right=Point(x=line.bounding_box[2], y=line.bounding_box[3]),
                bottom_right=Point(x=line.bounding_box[4], y=line.bounding_box[5]),
                bottom_left=Point(x=line.bounding_box[6], y=line.bounding_box[7])
            ) if line.bounding_box else None,
            page_number=page,
            words=[ExtractedWord._from_generated(word, page) for word in line.words] if line.words else None
        )


class ExtractedWord(object):
    """An object representing a word.

    :ivar str text: The text content of the word.
    :ivar ~azure.ai.formrecognizer.BoundingBox bounding_box:
        Bounding box of an extracted word.
    :ivar float confidence: Confidence value.
    :ivar int page_number:
        The 1-based page number in the input document.
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.confidence = kwargs.get("confidence", None)
        self.page_number = kwargs.get("page_number", None)

    @classmethod
    def _from_generated(cls, word, page):
        return cls(
            text=word.text,
            bounding_box=BoundingBox(
                top_left=Point(x=word.bounding_box[0], y=word.bounding_box[1]),
                top_right=Point(x=word.bounding_box[2], y=word.bounding_box[3]),
                bottom_right=Point(x=word.bounding_box[4], y=word.bounding_box[5]),
                bottom_left=Point(x=word.bounding_box[6], y=word.bounding_box[7])
            ) if word.bounding_box else None,
            confidence=word.confidence,
            page_number=page
        )


class PageMetadata(object):
    """Page metadata and text extracted from a page in the input document.

    :ivar int page_number:
        The 1-based page number in the input document.
    :ivar float angle:
        The general orientation of the text in clockwise direction, measured in
        degrees between (-180, 180].
    :ivar float width:
        The width of the image/PDF in pixels/inches, respectively.
    :ivar float height:
        The height of the image/PDF in pixels/inches, respectively.
    :ivar ~azure.ai.formrecognizer.LengthUnit unit:
        The unit used by the width, height and bounding box properties. For
        images, the unit is "pixel". For PDF, the unit is "inch".
    :ivar list[~azure.ai.formrecognizer.ExtractedLine] lines:
        When `include_text_content` is set to true, a list of recognized text lines. The
        maximum number of lines returned is 300 per page. The lines are sorted top to bottom, left to
        right, although in certain cases proximity is treated with higher priority. As the sorting
        order depends on the detected text, it may change across images and OCR version updates. Thus,
        business logic should be built upon the actual line location instead of order.
    """

    def __init__(self, **kwargs):
        self.page_number = kwargs.get("page_number", None)
        self.angle = kwargs.get("angle", None)
        self.width = kwargs.get("width", None)
        self.height = kwargs.get("height", None)
        self.unit = kwargs.get("unit", None)
        self.lines = kwargs.get("lines", None)

    @classmethod
    def _from_generated_page_index(cls, read_result, page_index):
        return cls(
            page_number=read_result[page_index].page,
            angle=read_result[page_index].angle,
            width=read_result[page_index].width,
            height=read_result[page_index].height,
            unit=read_result[page_index].unit,
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
            unit=page.unit,
            lines=[ExtractedLine._from_generated(line, page=page.page) for line in page.lines] if page.lines else None
        ) for page in read_result]


class FormTable(object):
    """Information about the extracted table contained in a page.

    :ivar list[~azure.ai.formrecognizer.FormTableCell] cells:
        List of cells contained in the table.
    :ivar int row_count:
        Number of rows in table.
    :ivar int column_count:
        Number of columns in table.
    """

    def __init__(self, **kwargs):
        self.cells = kwargs.get("cells", None)
        self.row_count = kwargs.get("row_count", None)
        self.column_count = kwargs.get("column_count", None)


class FormTableCell(object):
    """Information about the extracted cell in a table.

    :ivar str text: Text content of the cell.
    :ivar int row_index: Row index of the cell.
    :ivar int column_index: Column index of the cell.
    :ivar int row_span: Number of rows spanned by this cell.
    :ivar int column_span: Number of columns spanned by this cell.
    :ivar ~azure.ai.formrecognizer.BoundingBox bounding_box:
        Bounding box of the cell.
    :ivar float confidence: Confidence value.
    :ivar bool is_header: Whether the current cell is a header cell.
    :ivar bool is_footer: Whether the current cell is a footer cell.
    :ivar text_content:
        When `include_text_content` is set to true, a list of references to the text
        content constituting this field.
    :vartype text_content: list[~azure.ai.formrecognizer.FormWord, ~azure.ai.formrecognizer.FormLine]
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.row_index = kwargs.get("row_index", None)
        self.column_index = kwargs.get("column_index", None)
        self.row_span = kwargs.get("row_span", 1)
        self.column_span = kwargs.get("column_span", 1)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.confidence = kwargs.get("confidence", None)
        self.is_header = kwargs.get("is_header", False)
        self.is_footer = kwargs.get("is_footer", False)
        self.text_content = kwargs.get("text_content", None)

    @classmethod
    def _from_generated(cls, cell, read_result):
        return cls(
            text=cell.text,
            row_index=cell.row_index,
            column_index=cell.column_index,
            row_span=cell.row_span or 1,
            column_span=cell.column_span or 1,
            bounding_box=BoundingBox(
                top_left=Point(x=cell.bounding_box[0], y=cell.bounding_box[1]),
                top_right=Point(x=cell.bounding_box[2], y=cell.bounding_box[3]),
                bottom_right=Point(x=cell.bounding_box[4], y=cell.bounding_box[5]),
                bottom_left=Point(x=cell.bounding_box[6], y=cell.bounding_box[7])
            ) if cell.bounding_box else None,
            confidence=cell.confidence,
            is_header=cell.is_header or False,
            is_footer=cell.is_footer or False,
            text_content=get_elements(cell, read_result) if cell.elements else None
        )


class CustomModel(object):
    """Represents a custom model which was trained without labels.

    :ivar str model_id: Model identifier.
    :ivar ~azure.ai.formrecognizer.ModelStatus status:
        Status of the model. Possible values include: 'creating', 'ready', 'invalid'.
    :ivar ~datetime.datetime created_on:
        Date and time (UTC) when the model was created.
    :ivar ~datetime.datetime last_updated_on:
        Date and time (UTC) when the status was last updated.
    :ivar list[~azure.ai.formrecognizer.FormFields] extracted_fields:
        Fields extracted by the custom model.
    :ivar ~azure.ai.formrecognizer.TrainingInfo training_info:
        Training information about the custom model.
    """

    def __init__(self, **kwargs):
        self.model_id = kwargs.get("model_id", None)
        self.status = kwargs.get("status", None)
        self.created_on = kwargs.get("created_on", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.extracted_fields = kwargs.get("extracted_fields", None)
        self.training_info = kwargs.get("training_info", None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            model_id=model.model_info.model_id,
            status=model.model_info.status,
            created_on=model.model_info.created_date_time,
            last_updated_on=model.model_info.last_updated_date_time,
            extracted_fields=FormFields._from_generated(model.keys),
            training_info=TrainingInfo._from_generated(model.train_result)
        )


class TrainingInfo(object):
    """Training information about the custom model.

    :ivar list[~azure.ai.formrecognizer.TrainingDocumentInfo] documents:
        A list of reports for the training documents.
    :ivar list[~azure.ai.formrecognizer.FormRecognizerError] training_errors:
        List of any errors that occurred while training the model.
    """

    def __init__(self, **kwargs):
        self.documents = kwargs.get("documents", None)
        self.training_errors = kwargs.get("training_errors", None)

    @classmethod
    def _from_generated(cls, train):
        return cls(
            documents=[TrainingDocumentInfo._from_generated(doc)
                       for doc in train.training_documents] if train.training_documents else None,
            training_errors=FormRecognizerError._from_generated(train.errors)
        ) if train else None


class FormFields(object):
    """Fields extracted by the custom model.

    :ivar str form_type_id:
        Identifier of the type of form.
    :ivar list[str] fields:
        List of extracted fields on the page.
    """

    def __init__(self, **kwargs):
        self.form_type_id = kwargs.get("form_type_id", None)
        self.fields = kwargs.get("fields", None)

    @classmethod
    def _from_generated(cls, keys):
        try:
            clusters = keys.clusters
            return [
                cls(form_type_id=cluster_id, fields=fields)
                for cluster_id, fields in clusters.items()
            ]
        except AttributeError:
            return None


class TrainingDocumentInfo(object):
    """Report for a custom model training document.

    :ivar str document_name:
        The name of the document.
    :ivar ~azure.ai.formrecognizer.TrainStatus status:
        Status of the training operation. Possible values include:
        'succeeded', 'partiallySucceeded', 'failed'.
    :ivar int page_count:
        Total number of pages trained.
    :ivar list[~azure.ai.formrecognizer.FormRecognizerError] errors:
        List of any errors for document.
    """

    def __init__(self, **kwargs):
        self.document_name = kwargs.get("document_name", None)
        self.status = kwargs.get("status", None)
        self.page_count = kwargs.get("page_count", None)
        self.errors = kwargs.get("errors", None)

    @classmethod
    def _from_generated(cls, doc):
        return cls(
            document_name=doc.document_name,
            status=doc.status,
            page_count=doc.pages,
            errors=FormRecognizerError._from_generated(doc.errors)
        )


class FormRecognizerError(object):
    """Represents an error that occurred while training.

    :ivar str code: Error code.
    :ivar str message: Error message.
    """

    def __init__(self, **kwargs):
        self.code = kwargs.get("code", None)
        self.message = kwargs.get("message", None)

    @classmethod
    def _from_generated(cls, err):
        return [cls(code=error.code, message=error.message) for error in err] if err else None


class CustomLabeledModel(object):
    """Represents a custom model which was trained with labels.

    :ivar str model_id: Model identifier.
    :ivar ~azure.ai.formrecognizer.ModelStatus status:
        Status of the model. Possible values include: 'creating', 'ready', 'invalid'.
    :ivar ~datetime.datetime created_on:
        Date and time (UTC) when the model was created.
    :ivar ~datetime.datetime last_updated_on:
        Date and time (UTC) when the status was last updated.
    :ivar list[~azure.ai.formrecognizer.FieldInfo] fields:
        The list of labeled fields that the model was trained on.
    :ivar float average_model_accuracy: Average accuracy.
    :ivar ~azure.ai.formrecognizer.TrainingInfo training_info:
        Training information about the custom model.
    """

    def __init__(self, **kwargs):
        self.model_id = kwargs.get("model_id", None)
        self.status = kwargs.get("status", None)
        self.created_on = kwargs.get("created_on", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.fields = kwargs.get("fields", None)
        self.average_model_accuracy = kwargs.get("average_model_accuracy", None)
        self.training_info = kwargs.get("training_info", None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            model_id=model.model_info.model_id,
            status=model.model_info.status,
            created_on=model.model_info.created_date_time,
            last_updated_on=model.model_info.last_updated_date_time,
            fields=FieldInfo._from_generated(model.train_result) if model.train_result else None,
            average_model_accuracy=model.train_result.average_model_accuracy if model.train_result else None,
            training_info=TrainingInfo._from_generated(model.train_result) if model.train_result else None
        )


class FieldInfo(object):
    """The labeled field that the model was trained on.

    :ivar str field_name: Name of the field.
    :ivar float accuracy: Estimated extraction accuracy for this field.
    """

    def __init__(self, **kwargs):
        self.field_name = kwargs.get("field_name", None)
        self.accuracy = kwargs.get("accuracy", None)

    @classmethod
    def _from_generated(cls, model):
        return [cls(
            field_name=field.field_name,
            accuracy=field.accuracy
        ) for field in model.fields] if model.fields else None


class ExtractedPage(object):
    """Extracted information from a single page.

    :ivar list[~azure.ai.formrecognizer.ExtractedField] fields:
        A list of the extracted fields from the page.
    :ivar list[~azure.ai.formrecognizer.ExtractedTable] tables:
        A list of the extracted tables from the page.
    :ivar ~azure.ai.formrecognizer.PageMetadata page_metadata:
        Contains page metadata such as page width, length, angle, unit.
        If `include_text_content=True` is passed, contains a list
        of extracted text result for each page in the input document.
    :ivar int page_number:
        The 1-based page number in the input document.
    :ivar str form_type_id:
        Identifier of the type of form.
    """

    def __init__(self, **kwargs):
        self.fields = kwargs.get("fields", None)
        self.tables = kwargs.get("tables", None)
        self.page_metadata = kwargs.get("page_metadata", None)
        self.page_number = kwargs.get("page_number", None)
        self.form_type_id = kwargs.get("form_type_id", None)


class ExtractedField(object):
    """Represents an extracted field and its value.

    :ivar ~azure.ai.formrecognizer.ExtractedText name:
        The name of the field and its text details.
    :ivar ~azure.ai.formrecognizer.ExtractedText value:
        The value of the field and its text details.
    :ivar float confidence: Confidence value.
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.value = kwargs.get("value", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, field, read_result):
        return cls(
            name=ExtractedText._from_generated(field.key, read_result),
            value=ExtractedText._from_generated(field.value, read_result),
            confidence=field.confidence
        )


class ExtractedText(object):
    """Information about the extracted field or value.

    :ivar str text: The text content of the field or value.
    :ivar ~azure.ai.formrecognizer.BoundingBox bounding_box:
        Bounding box of the field or value.
    :ivar elements:
        When `include_text_content` is set to true, a list of references to the text
        elements constituting this field.
    :vartype elements: list[~azure.ai.formrecognizer.ExtractedWord, ~azure.ai.formrecognizer.ExtractedLine]
    """

    def __init__(self, **kwargs):
        self.text = kwargs.get("text", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.elements = kwargs.get("elements", None)

    @classmethod
    def _from_generated(cls, field, read_result):
        return cls(
            text=field.text,
            bounding_box=BoundingBox(
                top_left=Point(x=field.bounding_box[0], y=field.bounding_box[1]),
                top_right=Point(x=field.bounding_box[2], y=field.bounding_box[3]),
                bottom_right=Point(x=field.bounding_box[4], y=field.bounding_box[5]),
                bottom_left=Point(x=field.bounding_box[6], y=field.bounding_box[7])
            ) if field.bounding_box else None,
            elements=get_elements(field.elements, read_result) if field.elements else None
        )


class ExtractedLabeledForm(object):
    """Represents the extracted labeled fields corresponding to the input document,
    including page and text elements information.

    :ivar fields:
        Dictionary of the labeled fields and their values.
    :vartype fields: dict[str, ~azure.ai.formrecognizer.FormField]
    :ivar ~azure.ai.formrecognizer.PageRange page_range:
        The first and last page of the input document.
    :ivar list[~azure.ai.formrecognizer.ExtractedTable] tables:
        A list of extracted tables found in the input document.
    :ivar list[~azure.ai.formrecognizer.PageMetadata] page_metadata:
        Contains a list of page metadata such as page width, length,
        angle, unit. If `include_text_content=True` is passed, contains
        a list of extracted text result for each page in the input document.
    """

    def __init__(self, **kwargs):
        self.fields = kwargs.get("fields", None)
        self.page_range = kwargs.get("page_range", None)
        self.tables = kwargs.get("tables", None)
        self.page_metadata = kwargs.get("page_metadata", None)


class ModelInfo(object):
    """Custom model information.

    :ivar str model_id: Model identifier.
    :ivar ~azure.ai.formrecognizer.ModelStatus status:
        Status of the model. Possible values include: 'creating', 'ready',
        'invalid'.
    :ivar ~datetime.datetime created_on:
        Date and time (UTC) when the model was created.
    :ivar ~datetime.datetime last_updated_on:
        Date and time (UTC) when the status was last updated.
    """

    def __init__(self, **kwargs):
        self.model_id = kwargs.get("model_id", None)
        self.status = kwargs.get("status", None)
        self.created_on = kwargs.get("created_on", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            model_id=model.model_id,
            status=model.status,
            created_on=model.created_date_time,
            last_updated_on=model.last_updated_date_time
        )


class ModelsSummary(object):
    """Summary of all the custom models on the account.

    :ivar int count: Current count of trained custom models.
    :ivar int limit: Max number of models that can be trained for this account.
    :ivar ~datetime.datetime last_updated_on:
        Date and time (UTC) when the summary was last updated.
    """

    def __init__(self, **kwargs):
        self.count = kwargs.get("count", None)
        self.limit = kwargs.get("limit", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            count=model.count,
            limit=model.limit,
            last_updated_on=model.last_updated_date_time
        )
