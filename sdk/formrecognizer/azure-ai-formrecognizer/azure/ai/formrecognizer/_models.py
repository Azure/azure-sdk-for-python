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


class TrainingStatus(str, Enum):
    """Status of the training operation.
    """

    succeeded = "succeeded"
    partially_succeeded = "partiallySucceeded"
    failed = "failed"


class CustomFormModelStatus(str, Enum):
    """Status of the model.
    """

    creating = "creating"
    ready = "ready"
    invalid = "invalid"


class FormContentType(str, Enum):
    """Content type for upload
    """

    application_pdf = "application/pdf"  #: Content Type 'application/pdf'.
    image_jpeg = "image/jpeg"  #: Content Type 'image/jpeg'.
    image_png = "image/png"  #: Content Type 'image/png'.
    image_tiff = "image/tiff"  #: Content Type 'image/tiff'.


class Point(namedtuple("Point", "x y")):
    """The x, y coordinate of a point on a bounding box.

    :ivar float x: x-coordinate
    :ivar float y: y-coordinate
    """

    __slots__ = ()

    def __new__(cls, x, y):
        return super(Point, cls).__new__(cls, x, y)


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
    :ivar str receipt_locale: Defaults to "en-US".
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
        self.receipt_locale = kwargs.get("receipt_locale", "en-US")


class FormField(object):
    """Represents the recognized field and its value.

    :ivar ~azure.ai.formrecognizer.FieldText label_data:
        Contains the text, bounding box, and text content of the field label.
    :ivar ~azure.ai.formrecognizer.FieldText value_data:
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
        self.label_data = kwargs.get("label_data", None)
        self.value_data = kwargs.get("value_data", None)
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
            label_data=FieldText._from_generated(field, read_result),
            value_data=FieldText._from_generated(value, read_result),
            value=get_field_scalar_value(value),
            name=field,
            confidence=value.confidence,
            page_number=value.page,
        )

    @classmethod
    def _from_generated_unlabeled(cls, field, idx, page, read_result):
        return cls(
            label_data=FieldText._from_generated_unlabeled(field.key, page, read_result),
            value_data=FieldText._from_generated_unlabeled(field.value, page, read_result),
            value=field.value.text,
            name="field-" + str(idx),
            confidence=field.confidence,
            page_number=page,
        )


class FieldText(object):
    """Represents the properties of a field or value.

    :ivar int page_number:
        The 1-based page number in the input document.
    :ivar str text: The string representation of the field or value.
    :ivar list[~azure.ai.formrecognizer.Point] bounding_box:
        The quadrangle bounding box that outlines the text.
        Units are in pixels for images and inches for PDF.
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
            return None
        return cls(
            page_number=field.page,
            text=field.text,
            bounding_box=[
                Point(x=field.bounding_box[0], y=field.bounding_box[1]),
                Point(x=field.bounding_box[2], y=field.bounding_box[3]),
                Point(x=field.bounding_box[4], y=field.bounding_box[5]),
                Point(x=field.bounding_box[6], y=field.bounding_box[7])
            ] if field.bounding_box else None,
            text_content=get_elements(field, read_result) if field.elements else None
        )

    @classmethod
    def _from_generated_unlabeled(cls, field, page, read_result):
        return cls(
            page_number=page,
            text=field.text,
            bounding_box=[
                Point(x=field.bounding_box[0], y=field.bounding_box[1]),
                Point(x=field.bounding_box[2], y=field.bounding_box[3]),
                Point(x=field.bounding_box[4], y=field.bounding_box[5]),
                Point(x=field.bounding_box[6], y=field.bounding_box[7])
            ] if field.bounding_box else None,
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
    :ivar str or ~azure.ai.formrecognizer.LengthUnit unit:
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
    def _from_generated(cls, read_result):
        return [cls(
            page_number=page.page,
            text_angle=page.angle,
            width=page.width,
            height=page.height,
            unit=page.unit,
            lines=[FormLine._from_generated(line, page=page.page) for line in page.lines] if page.lines else None
        ) for page in read_result]


class FormLine(object):
    """An object representing an extracted text line.

    :ivar str text: The text content of the line.
    :ivar list[~azure.ai.formrecognizer.Point] bounding_box:
        The quadrangle bounding box that outlines the text.
        Units are in pixels for images and inches for PDF.
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
            bounding_box=[
                Point(x=line.bounding_box[0], y=line.bounding_box[1]),
                Point(x=line.bounding_box[2], y=line.bounding_box[3]),
                Point(x=line.bounding_box[4], y=line.bounding_box[5]),
                Point(x=line.bounding_box[6], y=line.bounding_box[7])
            ] if line.bounding_box else None,
            page_number=page,
            words=[FormWord._from_generated(word, page) for word in line.words] if line.words else None
        )


class FormWord(object):
    """An object representing a word.

    :ivar str text: The text content of the word.
    :ivar list[~azure.ai.formrecognizer.Point] bounding_box:
        The quadrangle bounding box that outlines the text.
        Units are in pixels for images and inches for PDF.
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
            bounding_box=[
                Point(x=word.bounding_box[0], y=word.bounding_box[1]),
                Point(x=word.bounding_box[2], y=word.bounding_box[3]),
                Point(x=word.bounding_box[4], y=word.bounding_box[5]),
                Point(x=word.bounding_box[6], y=word.bounding_box[7])
            ] if word.bounding_box else None,
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
    :ivar list[~azure.ai.formrecognizer.Point] bounding_box:
        The quadrangle bounding box that outlines the cell text.
        Units are in pixels for images and inches for PDF.
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
            bounding_box=[
                Point(x=cell.bounding_box[0], y=cell.bounding_box[1]),
                Point(x=cell.bounding_box[2], y=cell.bounding_box[3]),
                Point(x=cell.bounding_box[4], y=cell.bounding_box[5]),
                Point(x=cell.bounding_box[6], y=cell.bounding_box[7])
            ] if cell.bounding_box else None,
            confidence=cell.confidence,
            is_header=cell.is_header or False,
            is_footer=cell.is_footer or False,
            text_content=get_elements(cell, read_result) if cell.elements else None
        )


class CustomFormModel(object):
    """Represents a custom model returned from training.

    :ivar str model_id: Model identifier.
    :ivar str or ~azure.ai.formrecognizer.CustomFormModelStatus status:
        Status of the model. Possible values include: 'creating', 'ready', 'invalid'.
    :ivar ~datetime.datetime created_on:
        Date and time (UTC) when the model was created.
    :ivar ~datetime.datetime last_updated_on:
        Date and time (UTC) when the status was last updated.
    :ivar list[~azure.ai.formrecognizer.CustomFormSubModel] models:
        A list of submodels which contains the fields trained on.
    :ivar list[~azure.ai.formrecognizer.FormRecognizerError] errors:
        List of any training errors.
    :ivar ~azure.ai.formrecognizer.TrainingDocumentInfo training_documents:
        Training document information about the custom model.
    """

    def __init__(self, **kwargs):
        self.model_id = kwargs.get("model_id", None)
        self.status = kwargs.get("status", None)
        self.created_on = kwargs.get("created_on", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.models = kwargs.get("models", None)
        self.errors = kwargs.get("errors", None)
        self.training_documents = kwargs.get("training_documents", None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            model_id=model.model_info.model_id,
            status=model.model_info.status,
            created_on=model.model_info.created_date_time,
            last_updated_on=model.model_info.last_updated_date_time,
            models=CustomFormSubModel._from_generated_unlabeled(model)
            if model.keys else CustomFormSubModel._from_generated_labeled(model),
            errors=FormRecognizerError._from_generated(model.train_result.errors) if model.train_result else [],
            training_documents=TrainingDocumentInfo._from_generated(model.train_result)
            if model.train_result else None
        )


class CustomFormSubModel(object):
    """Represents the submodel with model accuracy,
    any errors while training the model, fields that were
    trained on, and the form type.

    :ivar float accuracy: The average accuracy of the model.
    :ivar fields: The fields the model was trained on.
    :vartype fields: dict[str, ~azure.ai.formrecognizer.CustomFormModelField]
    :ivar str form_type: Identifier of the type of form.
    """
    def __init__(self, **kwargs):
        self.accuracy = kwargs.get("accuracy", None)
        self.fields = kwargs.get("fields", None)
        self.form_type = kwargs.get("form_type", None)

    @classmethod
    def _from_generated_unlabeled(cls, model):
        return [cls(
            accuracy=None,
            fields={cluster_id: CustomFormModelField._from_generated_unlabeled(fields)},
            form_type="form-" + cluster_id
        ) for cluster_id, fields in model.keys.clusters.items()] if model.keys else None

    @classmethod
    def _from_generated_labeled(cls, model):
        return [cls(
            accuracy=model.train_result.average_model_accuracy,
            fields={field.field_name: CustomFormModelField._from_generated_labeled(field)
                    for field in model.train_result.fields},
            form_type="form-" + model.model_info.model_id
        )] if model.train_result else None


class CustomFormModelField(object):
    """A field that the model was trained on.

    :ivar str name: Name of the field.
    :ivar float accuracy: Estimated extraction accuracy for this field.
    """
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.accuracy = kwargs.get("accuracy", None)

    @classmethod
    def _from_generated_labeled(cls, field):
        return cls(
            name=field.field_name,
            accuracy=field.accuracy
        )

    @classmethod
    def _from_generated_unlabeled(cls, fields):
        return [cls(
            name=field_name,
            accuracy=None
        ) for field_name in fields
        ]


class TrainingDocumentInfo(object):
    """Report for a custom model training document.

    :ivar str document_name:
        The name of the document.
    :ivar str or ~azure.ai.formrecognizer.TrainingStatus status:
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
    def _from_generated(cls, train_result):
        return [cls(
            document_name=doc.document_name,
            status=doc.status,
            page_count=doc.pages,
            errors=FormRecognizerError._from_generated(doc.errors)
        ) for doc in train_result.training_documents]


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
        return [cls(code=error.code, message=error.message) for error in err] if err else []


class CustomFormModelInfo(object):
    """Custom model information.

    :ivar str model_id: Model identifier.
    :ivar str or ~azure.ai.formrecognizer.CustomFormModelStatus status:
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


class AccountProperties(object):
    """Summary of all the custom models on the account.

    :ivar int custom_model_count: Current count of trained custom models.
    :ivar int custom_model_limit: Max number of models that can be trained for this account.
    """

    def __init__(self, **kwargs):
        self.custom_model_count = kwargs.get("custom_model_count", None)
        self.custom_model_limit = kwargs.get("custom_model_limit", None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            custom_model_count=model.count,
            custom_model_limit=model.limit,
        )
