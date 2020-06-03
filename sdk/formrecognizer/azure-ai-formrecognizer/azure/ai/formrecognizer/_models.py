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


def adjust_confidence(score):
    """Adjust confidence when not returned.
    """
    if score is None:
        return 1.0
    return score


def get_elements(field, read_result):
    text_elements = []

    try:
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
    except IndexError:
        return None  # https://github.com/Azure/azure-sdk-for-python/issues/11014


def get_field_value(field, value, read_result):  # pylint: disable=too-many-return-statements
    if value is None:
        return value
    if value.type == "string":
        return value.value_string
    if value.type == "number":
        return value.value_number
    if value.type == "integer":
        return value.value_integer
    if value.type == "date":
        return value.value_date
    if value.type == "phoneNumber":
        return value.value_phone_number
    if value.type == "time":
        return value.value_time
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
    return None


class LengthUnit(str, Enum):
    """The unit used by the width, height and bounding box properties.
    For images, the unit is "pixel". For PDF, the unit is "inch".
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
    """Status indicating the model's readiness for use.
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


class FormPageRange(namedtuple("FormPageRange", "first_page_number last_page_number")):
    """The 1-based page range of the form.

    :ivar int first_page_number: The first page number of the form.
    :ivar int last_page_number: The last page number of the form.
    """

    __slots__ = ()

    def __new__(cls, first_page_number, last_page_number):
        return super(FormPageRange, cls).__new__(cls, first_page_number, last_page_number)


class FormContent(object):
    """Base type which includes properties for text.

    :ivar str text: The text content of the line.
    :ivar list[~azure.ai.formrecognizer.Point] bounding_box:
        A list of 4 points representing the quadrilateral bounding box
        that outlines the text. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF.
    :ivar int page_number:
        The 1-based number of the page in which this content is present.
    """
    def __init__(self, **kwargs):
        self.bounding_box = kwargs.get("bounding_box", None)
        self.page_number = kwargs.get("page_number", None)
        self.text = kwargs.get("text", None)


class RecognizedForm(object):
    """Represents a form that has been recognized by a trained model.

    :ivar str form_type:
        The type of form the model identified the submitted form to be.
    :ivar fields:
        A dictionary of the fields found on the form. The fields dictionary
        keys are the `name` of the field. For models trained with labels,
        this is the training-time label of the field. For models trained
        without labels, a unique name is generated for each field.
    :vartype fields: dict[str, ~azure.ai.formrecognizer.FormField]
    :ivar ~azure.ai.formrecognizer.FormPageRange page_range:
        The first and last page number of the input form.
    :ivar list[~azure.ai.formrecognizer.FormPage] pages:
        A list of pages recognized from the input document. Contains lines,
        words, tables and page metadata.
    """
    def __init__(self, **kwargs):
        self.fields = kwargs.get("fields", None)
        self.form_type = kwargs.get("form_type", None)
        self.page_range = kwargs.get("page_range", None)
        self.pages = kwargs.get("pages", None)

    def __repr__(self):
        return "RecognizedForm(form_type={}, fields={}, page_range={}, pages={})".format(
            self.form_type, repr(self.fields), repr(self.page_range), repr(self.pages)
        )[:1024]

class RecognizedReceipt(RecognizedForm):
    """Represents a receipt that has been recognized by a trained model.

    :ivar str form_type:
        The type of form the model identified the submitted form to be.
    :ivar fields:
        A dictionary of the fields found on the form. The fields dictionary
        keys are the `name` of the field. For models trained with labels,
        this is the training-time label of the field. For models trained
        without labels, a unique name is generated for each field.
    :vartype fields: dict[str, ~azure.ai.formrecognizer.FormField]
    :ivar ~azure.ai.formrecognizer.FormPageRange page_range:
        The first and last page number of the input form.
    :ivar list[~azure.ai.formrecognizer.FormPage] pages:
        A list of pages recognized from the input document. Contains lines,
        words, tables and page metadata.
    """

    def __repr__(self):
        return "RecognizedReceipt(form_type={}, fields={}, page_range={}, pages={})".format(
            self.form_type, repr(self.fields), repr(self.page_range), repr(self.pages)
        )[:1024]


class FormField(object):
    """Represents a field recognized in an input form.

    :ivar ~azure.ai.formrecognizer.FieldText label_data:
        Contains the text, bounding box, and text content of the field label.
    :ivar ~azure.ai.formrecognizer.FieldText value_data:
        Contains the text, bounding box, and text content of the field value.
    :ivar str name: The unique name of the field or label.
    :ivar value:
        The value for the recognized field. Possible types include: 'string',
        'date', 'time', 'phoneNumber', 'number', 'integer', 'object', or 'array'.
    :vartype value: str, int, float, :class:`~datetime.date`, :class:`~datetime.time`,
        :class:`~azure.ai.formrecognizer.FormField`, or list[:class:`~azure.ai.formrecognizer.FormField`]
    :ivar float confidence:
        Measures the degree of certainty of the recognition result. Value is between [0.0, 1.0].
    """

    def __init__(self, **kwargs):
        self.label_data = kwargs.get("label_data", None)
        self.value_data = kwargs.get("value_data", None)
        self.name = kwargs.get("name", None)
        self.value = kwargs.get("value", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, field, value, read_result):
        return cls(
            label_data=FieldText._from_generated(field, read_result),
            value_data=FieldText._from_generated(value, read_result),
            value=get_field_value(field, value, read_result),
            name=field,
            confidence=adjust_confidence(value.confidence) if value else None,
        )

    @classmethod
    def _from_generated_unlabeled(cls, field, idx, page, read_result):
        return cls(
            label_data=FieldText._from_generated_unlabeled(field.key, page, read_result),
            value_data=FieldText._from_generated_unlabeled(field.value, page, read_result),
            value=field.value.text,
            name="field-" + str(idx),
            confidence=adjust_confidence(field.confidence),
        )

    def __repr__(self):
        return "FormField(label_data={}, value_data={}, name={}, value={}, confidence={})".format(
            repr(self.label_data), repr(self.value_data), self.name, repr(self.value), self.confidence
        )[:1024]


class FieldText(FormContent):
    """Represents the text that is part of a form field. This includes
    the location of the text in the form and a collection of the
    elements that make up the text.

    :ivar int page_number:
        The 1-based number of the page in which this content is present.
    :ivar str text: The string representation of the field or value.
    :ivar list[~azure.ai.formrecognizer.Point] bounding_box:
        A list of 4 points representing the quadrilateral bounding box
        that outlines the text. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF.
    :ivar text_content:
        When `include_text_content` is set to true, a list of text
        elements constituting this field or value is returned.
    :vartype text_content: list[~azure.ai.formrecognizer.FormWord, ~azure.ai.formrecognizer.FormLine]
    """

    def __init__(self, **kwargs):
        super(FieldText, self).__init__(**kwargs)
        self.text_content = kwargs.get("text_content", None)

    @classmethod
    def _from_generated(cls, field, read_result):
        if field is None or isinstance(field, six.string_types):
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

    def __repr__(self):
        return "FieldText(page_number={}, text={}, bounding_box={}, text_content={})".format(
            self.page_number, self.text, self.bounding_box, repr(self.text_content)
        )[:1024]


class FormPage(object):
    """Represents a page recognized from the input document. Contains lines,
    words, tables and page metadata.

    :ivar int page_number:
        The 1-based number of the page in which this content is present.
    :ivar float text_angle:
        The general orientation of the text in clockwise direction, measured in
        degrees between (-180, 180].
    :ivar float width:
        The width of the image/PDF in pixels/inches, respectively.
    :ivar float height:
        The height of the image/PDF in pixels/inches, respectively.
    :ivar str unit:
        The :class:`~azure.ai.formrecognizer.LengthUnit` used by the width,
        height, and bounding box properties. For images, the unit is "pixel".
        For PDF, the unit is "inch".
    :ivar list[~azure.ai.formrecognizer.FormTable] tables:
        A list of extracted tables contained in a page.
    :ivar list[~azure.ai.formrecognizer.FormLine] lines:
        When `include_text_content` is set to true, a list of recognized text lines is returned.
        For calls to recognize content, this list is always populated. The maximum number of lines
        returned is 300 per page. The lines are sorted top to bottom, left to right, although in
        certain cases proximity is treated with higher priority. As the sorting order depends on
        the detected text, it may change across images and OCR version updates. Thus, business
        logic should be built upon the actual line location instead of order.
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

    def __repr__(self):
        return "FormPage(page_number={}, text_angle={}, width={}, height={}, unit={}, tables={}, lines={})".format(
            self.page_number, self.text_angle, self.width, self.height, self.unit, repr(self.tables), repr(self.lines)
        )[:1024]


class FormLine(FormContent):
    """An object representing an extracted line of text.

    :ivar str text: The text content of the line.
    :ivar list[~azure.ai.formrecognizer.Point] bounding_box:
        A list of 4 points representing the quadrilateral bounding box
        that outlines the text. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF.
    :ivar list[~azure.ai.formrecognizer.FormWord] words:
        A list of the words that make up the line.
    :ivar int page_number:
        The 1-based number of the page in which this content is present.
    """

    def __init__(self, **kwargs):
        super(FormLine, self).__init__(**kwargs)
        self.words = kwargs.get("words", [])

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

    def __repr__(self):
        return "FormLine(text={}, bounding_box={}, words={}, page_number={})".format(
            self.text, self.bounding_box, repr(self.words), self.page_number
        )[:1024]


class FormWord(FormContent):
    """Represents a word recognized from the input document.

    :ivar str text: The text content of the word.
    :ivar list[~azure.ai.formrecognizer.Point] bounding_box:
        A list of 4 points representing the quadrilateral bounding box
        that outlines the text. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF.
    :ivar float confidence:
        Measures the degree of certainty of the recognition result. Value is between [0.0, 1.0].
    :ivar int page_number:
        The 1-based number of the page in which this content is present.
    """

    def __init__(self, **kwargs):
        super(FormWord, self).__init__(**kwargs)
        self.confidence = kwargs.get("confidence", None)

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
            confidence=adjust_confidence(word.confidence),
            page_number=page
        )

    def __repr__(self):
        return "FormWord(text={}, bounding_box={}, confidence={}, page_number={})".format(
            self.text, self.bounding_box, self.confidence, self.page_number
        )[:1024]


class FormTable(object):
    """Information about the extracted table contained on a page.

    :ivar int page_number:
        The 1-based number of the page in which this table is present.
    :ivar list[~azure.ai.formrecognizer.FormTableCell] cells:
        List of cells contained in the table.
    :ivar int row_count:
        Number of rows in table.
    :ivar int column_count:
        Number of columns in table.
    """

    def __init__(self, **kwargs):
        self.page_number = kwargs.get("page_number", None)
        self.cells = kwargs.get("cells", [])
        self.row_count = kwargs.get("row_count", None)
        self.column_count = kwargs.get("column_count", None)

    def __repr__(self):
        return "FormTable(page_number={}, cells={}, row_count={}, column_count={})".format(
            self.page_number, repr(self.cells), self.row_count, self.column_count
        )[:1024]


class FormTableCell(FormContent):
    """Represents a cell contained in a table recognized from the input document.

    :ivar str text: Text content of the cell.
    :ivar int row_index: Row index of the cell.
    :ivar int column_index: Column index of the cell.
    :ivar int row_span: Number of rows spanned by this cell.
    :ivar int column_span: Number of columns spanned by this cell.
    :ivar list[~azure.ai.formrecognizer.Point] bounding_box:
        A list of 4 points representing the quadrilateral bounding box
        that outlines the text. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF.
    :ivar float confidence:
        Measures the degree of certainty of the recognition result. Value is between [0.0, 1.0].
    :ivar bool is_header: Whether the current cell is a header cell.
    :ivar bool is_footer: Whether the current cell is a footer cell.
    :ivar int page_number:
        The 1-based number of the page in which this content is present.
    :ivar text_content:
        When `include_text_content` is set to true, a list of text
        elements constituting this cell is returned.
        For calls to recognize content, this list is always populated.
    :vartype text_content: list[~azure.ai.formrecognizer.FormWord, ~azure.ai.formrecognizer.FormLine]
    """

    def __init__(self, **kwargs):
        super(FormTableCell, self).__init__(**kwargs)
        self.row_index = kwargs.get("row_index", None)
        self.column_index = kwargs.get("column_index", None)
        self.row_span = kwargs.get("row_span", 1)
        self.column_span = kwargs.get("column_span", 1)
        self.confidence = kwargs.get("confidence", None)
        self.is_header = kwargs.get("is_header", False)
        self.is_footer = kwargs.get("is_footer", False)
        self.text_content = kwargs.get("text_content", None)

    @classmethod
    def _from_generated(cls, cell, page, read_result):
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
            confidence=adjust_confidence(cell.confidence),
            is_header=cell.is_header or False,
            is_footer=cell.is_footer or False,
            page_number=page,
            text_content=get_elements(cell, read_result) if cell.elements else None
        )

    def __repr__(self):
        return "FormTableCell(text={}, row_index={}, column_index={}, row_span={}, column_span={}, " \
                "bounding_box={}, confidence={}, is_header={}, is_footer={}, page_number={}, text_content={})".format(
                    self.text, self.row_index, self.column_index, self.row_span, self.column_span, self.bounding_box,
                    self.confidence, self.is_header, self.is_footer, self.page_number, repr(self.text_content)
                )[:1024]


class CustomFormModel(object):
    """Represents a model trained from custom forms.

    :ivar str model_id: The unique identifier of this model.
    :ivar str status:
        Status indicating the model's readiness for use,
        :class:`~azure.ai.formrecognizer.CustomFormModelStatus`.
        Possible values include: 'creating', 'ready', 'invalid'.
    :ivar ~datetime.datetime requested_on:
        The date and time (UTC) when model training was requested.
    :ivar ~datetime.datetime completed_on:
        Date and time (UTC) when model training completed.
    :ivar list[~azure.ai.formrecognizer.CustomFormSubmodel] submodels:
        A list of submodels that are part of this model, each of
        which can recognize and extract fields from a different type of form.
    :ivar list[~azure.ai.formrecognizer.FormRecognizerError] errors:
        List of any training errors.
    :ivar ~azure.ai.formrecognizer.TrainingDocumentInfo training_documents:
         Metadata about each of the documents used to train the model.
    """

    def __init__(self, **kwargs):
        self.model_id = kwargs.get("model_id", None)
        self.status = kwargs.get("status", None)
        self.requested_on = kwargs.get("requested_on", None)
        self.completed_on = kwargs.get("completed_on", None)
        self.submodels = kwargs.get("submodels", None)
        self.errors = kwargs.get("errors", None)
        self.training_documents = kwargs.get("training_documents", [])

    @classmethod
    def _from_generated(cls, model):
        return cls(
            model_id=model.model_info.model_id,
            status=model.model_info.status,
            requested_on=model.model_info.created_date_time,
            completed_on=model.model_info.last_updated_date_time,
            submodels=CustomFormSubmodel._from_generated_unlabeled(model)
            if model.keys else CustomFormSubmodel._from_generated_labeled(model),
            errors=FormRecognizerError._from_generated(model.train_result.errors) if model.train_result else None,
            training_documents=TrainingDocumentInfo._from_generated(model.train_result)
            if model.train_result else None
        )

    def __repr__(self):
        return "CustomFormModel(model_id={}, status={}, requested_on={}, completed_on={}, submodels={}, " \
                "errors={}, training_documents={})".format(
                    self.model_id, self.status, self.requested_on, self.completed_on, repr(self.submodels),
                    repr(self.errors), repr(self.training_documents)
                )[:1024]


class CustomFormSubmodel(object):
    """Represents a submodel that extracts fields from a specific type of form.

    :ivar float accuracy: The mean of the model's field accuracies.
    :ivar fields: A dictionary of the fields that this submodel will recognize
        from the input document. The fields dictionary keys are the `name` of
        the field. For models trained with labels, this is the training-time
        label of the field. For models trained without labels, a unique name
        is generated for each field.
    :vartype fields: dict[str, ~azure.ai.formrecognizer.CustomFormModelField]
    :ivar str form_type: Type of form this submodel recognizes.
    """
    def __init__(self, **kwargs):
        self.accuracy = kwargs.get("accuracy", None)
        self.fields = kwargs.get("fields", None)
        self.form_type = kwargs.get("form_type", None)

    @classmethod
    def _from_generated_unlabeled(cls, model):
        return [cls(
            accuracy=None,
            fields=CustomFormModelField._from_generated_unlabeled(fields),
            form_type="form-" + cluster_id
        ) for cluster_id, fields in model.keys.clusters.items()]

    @classmethod
    def _from_generated_labeled(cls, model):
        return [cls(
            accuracy=model.train_result.average_model_accuracy,
            fields={field.field_name: CustomFormModelField._from_generated_labeled(field)
                    for field in model.train_result.fields} if model.train_result.fields else None,
            form_type="form-" + model.model_info.model_id
        )] if model.train_result else None

    def __repr__(self):
        return "CustomFormSubmodel(accuracy={}, fields={}, form_type={})".format(
            self.accuracy, repr(self.fields), self.form_type
        )[:1024]


class CustomFormModelField(object):
    """A field that the model will extract from forms it analyzes.

    :ivar str label: The form fields label on the form.
    :ivar str name: Canonical name; uniquely identifies a field within the form.
    :ivar float accuracy: The estimated recognition accuracy for this field.
    """
    def __init__(self, **kwargs):
        self.label = kwargs.get("label", None)
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
        return {
            "field-{}".format(idx): cls(
                name="field-{}".format(idx),
                label=field_name,
            ) for idx, field_name in enumerate(fields)
        }

    def __repr__(self):
        return "CustomFormModelField(label={}, name={}, accuracy={})".format(
            self.label, self.name, self.accuracy
        )[:1024]


class TrainingDocumentInfo(object):
    """Report for an individual document used for training
    a custom model.

    :ivar str document_name:
        The name of the document.
    :ivar str status:
        The :class:`~azure.ai.formrecognizer.TrainingStatus`
        of the training operation. Possible values include:
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
        self.errors = kwargs.get("errors", [])

    @classmethod
    def _from_generated(cls, train_result):
        return [cls(
            document_name=doc.document_name,
            status=doc.status,
            page_count=doc.pages,
            errors=FormRecognizerError._from_generated(doc.errors)
        ) for doc in train_result.training_documents] if train_result.training_documents else None

    def __repr__(self):
        return "TrainingDocumentInfo(document_name={}, status={}, page_count={}, errors={})".format(
            self.document_name, self.status, self.page_count, repr(self.errors)
        )[:1024]


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

    def __repr__(self):
        return "FormRecognizerError(code={}, message={})".format(self.code, self.message)[:1024]


class CustomFormModelInfo(object):
    """Custom model information.

    :ivar str model_id: The unique identifier of the model.
    :ivar str status:
        The status of the model, :class:`~azure.ai.formrecognizer.CustomFormModelStatus`.
        Possible values include: 'creating', 'ready', 'invalid'.
    :ivar ~datetime.datetime requested_on:
        Date and time (UTC) when model training was requested.
    :ivar ~datetime.datetime completed_on:
        Date and time (UTC) when model training completed.
    """

    def __init__(self, **kwargs):
        self.model_id = kwargs.get("model_id", None)
        self.status = kwargs.get("status", None)
        self.requested_on = kwargs.get("requested_on", None)
        self.completed_on = kwargs.get("completed_on", None)

    @classmethod
    def _from_generated(cls, model, model_id=None):
        if model.status == "succeeded":  # map copy status to model status
            model.status = "ready"
        return cls(
            model_id=model_id if model_id else model.model_id,
            status=model.status,
            requested_on=model.created_date_time,
            completed_on=model.last_updated_date_time
        )

    def __repr__(self):
        return "CustomFormModelInfo(model_id={}, status={}, requested_on={}, completed_on={})".format(
            self.model_id, self.status, self.requested_on, self.completed_on
        )[:1024]


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

    def __repr__(self):
        return "AccountProperties(custom_model_count={}, custom_model_limit={})".format(
            self.custom_model_count, self.custom_model_limit
        )[:1024]
