# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access, too-many-lines

from typing import Any, Dict, Iterable, List, NewType
from enum import Enum
from collections import namedtuple
from azure.core import CaseInsensitiveEnumMeta
from ._generated.v2022_06_30_preview.models import ModelInfo, Error
from ._helpers import (
    adjust_value_type,
    adjust_confidence,
    get_element,
    adjust_text_angle,
    _get_deserialize,
)


TargetAuthorization = NewType('TargetAuthorization', Dict[str, str])

def prepare_document_spans(spans):
    return [DocumentSpan._from_generated(span) for span in spans] if spans else []


def prepare_bounding_regions(regions):
    return (
        [BoundingRegion._from_generated(region) for region in regions]
        if regions
        else []
    )


def get_bounding_box(field):
    return (
        [
            Point(x=field.bounding_box[0], y=field.bounding_box[1]),
            Point(x=field.bounding_box[2], y=field.bounding_box[3]),
            Point(x=field.bounding_box[4], y=field.bounding_box[5]),
            Point(x=field.bounding_box[6], y=field.bounding_box[7]),
        ]
        if field.bounding_box
        else None
    )


def get_polygon(field):
    return (
        [
            Point(x=field.polygon[point], y=field.polygon[point+1])
            for point in range(0, len(field.polygon), 2)
        ]
        if field.polygon
        else None
    )


def resolve_element(element, read_result):
    element_type, element, page = get_element(element, read_result)
    if element_type == "word":
        return FormWord._from_generated(element, page=page)
    if element_type == "line":
        return FormLine._from_generated(element, page=page)
    if element_type == "selectionMark":
        return FormSelectionMark._from_generated(element, page=page)
    raise ValueError("Failed to parse element reference.")


def get_field_value(
    field, value, read_result
):  # pylint: disable=too-many-return-statements
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
        return (
            [
                FormField._from_generated(field, value, read_result)
                for value in value.value_array
            ]
            if value.value_array
            else []
        )
    if value.type == "object":
        return (
            {
                key: FormField._from_generated(key, value, read_result)
                for key, value in value.value_object.items()
            }
            if value.value_object
            else {}
        )
    if value.type == "selectionMark":
        return value.value_selection_mark
    if value.type == "countryRegion":
        return value.value_country_region
    return None


def get_field_value_v3(value):  # pylint: disable=too-many-return-statements
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
    if value.type == "signature":
        return value.value_signature
    if value.type == "array":
        return (
            [DocumentField._from_generated(value) for value in value.value_array]
            if value.value_array
            else []
        )
    if value.type == "currency":
        return CurrencyValue._from_generated(value.value_currency)
    if value.type == "address":
        return AddressValue._from_generated(value.value_address)
    if value.type == "object":
        return (
            {
                key: DocumentField._from_generated(value)
                for key, value in value.value_object.items()
            }
            if value.value_object
            else {}
        )
    if value.type == "selectionMark":
        return value.value_selection_mark
    if value.type == "countryRegion":
        return value.value_country_region
    return None

class DocumentBuildMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The mode used when building custom models.

    For more information, see https://aka.ms/azsdk/formrecognizer/buildmode.
    """

    NEURAL = "neural"
    TEMPLATE = "template"


class FieldValueType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Semantic data type of the field value.

    .. versionadded:: v2.1
        The *selectionMark* and *countryRegion* values
    """

    STRING = "string"
    DATE = "date"
    TIME = "time"
    PHONE_NUMBER = "phoneNumber"
    FLOAT = "float"
    INTEGER = "integer"
    LIST = "list"
    DICTIONARY = "dictionary"
    SELECTION_MARK = "selectionMark"
    COUNTRY_REGION = "countryRegion"


class LengthUnit(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """The unit used by the width, height and bounding box properties.
    For images, the unit is "pixel". For PDF, the unit is "inch".
    """

    PIXEL = "pixel"
    INCH = "inch"


class TrainingStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Status of the training operation."""

    SUCCEEDED = "succeeded"
    PARTIALLY_SUCCEEDED = "partiallySucceeded"
    FAILED = "failed"


class CustomFormModelStatus(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Status indicating the model's readiness for use."""

    CREATING = "creating"
    READY = "ready"
    INVALID = "invalid"


class FormContentType(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Content type for upload.

    .. versionadded:: v2.1
        Support for image/bmp
    """

    APPLICATION_PDF = "application/pdf"
    IMAGE_JPEG = "image/jpeg"
    IMAGE_PNG = "image/png"
    IMAGE_TIFF = "image/tiff"
    IMAGE_BMP = "image/bmp"


class Point(namedtuple("Point", "x y")):
    """The x, y coordinate of a point on a bounding box.

    :ivar float x: x-coordinate
    :ivar float y: y-coordinate

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """

    __slots__ = ()

    def __new__(cls, x, y):
        return super().__new__(cls, x, y)

    def to_dict(self) -> dict:
        """Returns a dict representation of Point.

        :return: dict
        :rtype: dict
        """
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, data: dict) -> "Point":
        """Converts a dict in the shape of a Point to the model itself.

        :param dict data: A dictionary in the shape of Point.
        :return: Point
        :rtype: Point
        """
        return cls(x=data.get("x", None), y=data.get("y", None))


class FormPageRange(namedtuple("FormPageRange", "first_page_number last_page_number")):
    """The 1-based page range of the form.

    :ivar int first_page_number: The first page number of the form.
    :ivar int last_page_number: The last page number of the form.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """

    __slots__ = ()

    def __new__(cls, first_page_number, last_page_number):
        return super().__new__(
            cls, first_page_number, last_page_number
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of FormPageRange.

        :return: dict
        :rtype: dict
        """
        return {
            "first_page_number": self.first_page_number,
            "last_page_number": self.last_page_number,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FormPageRange":
        """Converts a dict in the shape of a FormPageRange to the model itself.

        :param dict data: A dictionary in the shape of FormPageRange.
        :return: FormPageRange
        :rtype: FormPageRange
        """
        return cls(
            first_page_number=data.get("first_page_number", None),
            last_page_number=data.get("last_page_number", None),
        )


class FormElement:
    """Base type which includes properties for a form element.

    :ivar str text: The text content of the element.
    :ivar list[~azure.ai.formrecognizer.Point] bounding_box:
        A list of 4 points representing the quadrilateral bounding box
        that outlines the text. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF.
    :ivar int page_number:
        The 1-based number of the page in which this content is present.
    :ivar str kind:
        The kind of form element. Possible kinds are "word", "line", or "selectionMark" which
        correspond to a :class:`~azure.ai.formrecognizer.FormWord` :class:`~azure.ai.formrecognizer.FormLine`,
        or :class:`~azure.ai.formrecognizer.FormSelectionMark`, respectively.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        self.bounding_box = kwargs.get("bounding_box", None)
        self.page_number = kwargs.get("page_number", None)
        self.text = kwargs.get("text", None)
        self.kind = kwargs.get("kind", None)

    def to_dict(self) -> dict:
        """Returns a dict representation of FormElement.

        :return: dict
        :rtype: dict
        """
        return {
            "text": self.text,
            "bounding_box": [f.to_dict() for f in self.bounding_box]
            if self.bounding_box
            else [],
            "page_number": self.page_number,
            "kind": self.kind,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FormElement":
        """Converts a dict in the shape of a FormElement to the model itself.

        :param dict data: A dictionary in the shape of FormElement.
        :return: FormElement
        :rtype: FormElement
        """
        return cls(
            text=data.get("text", None),
            page_number=data.get("page_number", None),
            kind=data.get("kind", None),
            bounding_box=[Point.from_dict(f) for f in data.get("bounding_box")]  # type: ignore
            if len(data.get("bounding_box", [])) > 0
            else [],
        )


class RecognizedForm:
    """Represents a form that has been recognized by a trained or prebuilt model.
    The `fields` property contains the form fields that were extracted from the
    form. Tables, text lines/words, and selection marks are extracted per page
    and found in the `pages` property.

    :ivar str form_type:
        The type of form the model identified the submitted form to be.
    :ivar str form_type_confidence:
        Confidence of the type of form the model identified the submitted form to be.
    :ivar str model_id:
        Model identifier of model used to analyze form if not using a prebuilt
        model.
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
        words, selection marks, tables and page metadata.

    .. versionadded:: v2.1
        The *form_type_confidence* and *model_id* properties, support for
        *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        self.fields = kwargs.get("fields", None)
        self.form_type = kwargs.get("form_type", None)
        self.page_range = kwargs.get("page_range", None)
        self.pages = kwargs.get("pages", None)
        self.model_id = kwargs.get("model_id", None)
        self.form_type_confidence = kwargs.get("form_type_confidence", None)

    def __repr__(self):
        return (
            f"RecognizedForm(form_type={self.form_type}, fields={repr(self.fields)}, "
            f"page_range={repr(self.page_range)}, pages={repr(self.pages)}, "
            f"form_type_confidence={self.form_type_confidence}, model_id={self.model_id})"
            )[:1024]

    def to_dict(self) -> dict:
        """Returns a dict representation of RecognizedForm.

        :return: dict
        :rtype: dict
        """
        return {
            "fields": {k: v.to_dict() for k, v in self.fields.items()}
            if self.fields
            else {},
            "form_type": self.form_type,
            "pages": [v.to_dict() for v in self.pages] if self.pages else [],
            "model_id": self.model_id,
            "form_type_confidence": self.form_type_confidence,
            "page_range": self.page_range.to_dict() if self.page_range else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "RecognizedForm":
        """Converts a dict in the shape of a RecognizedForm to the model itself.

        :param dict data: A dictionary in the shape of RecognizedForm.
        :return: RecognizedForm
        :rtype: RecognizedForm
        """
        return cls(
            fields={k: FormField.from_dict(v) for k, v in data.get("fields").items()}  # type: ignore
            if data.get("fields")
            else {},
            form_type=data.get("form_type", None),
            pages=[FormPage.from_dict(v) for v in data.get("pages")]  # type: ignore
            if len(data.get("pages", [])) > 0
            else [],
            model_id=data.get("model_id", None),
            form_type_confidence=data.get("form_type_confidence", None),
            page_range=FormPageRange.from_dict(data.get("page_range"))  # type: ignore
            if data.get("page_range")
            else None,
        )


class FormField:
    """Represents a field recognized in an input form.

    :ivar str value_type: The type of `value` found on FormField. Described in
        :class:`~azure.ai.formrecognizer.FieldValueType`, possible types include: 'string',
        'date', 'time', 'phoneNumber', 'float', 'integer', 'dictionary', 'list', 'selectionMark',
        or 'countryRegion'.
    :ivar ~azure.ai.formrecognizer.FieldData label_data:
        Contains the text, bounding box, and field elements for the field label.
        Note that this is not returned for forms analyzed by models trained with labels.
    :ivar ~azure.ai.formrecognizer.FieldData value_data:
        Contains the text, bounding box, and field elements for the field value.
    :ivar str name: The unique name of the field or the training-time label if
        analyzed from a custom model that was trained with labels.
    :ivar value:
        The value for the recognized field. Its semantic data type is described by `value_type`.
        If the value is extracted from the form, but cannot be normalized to its type,
        then access the `value_data.text` property for a textual representation of the value.
    :vartype value: str, int, float, :class:`~datetime.date`, :class:`~datetime.time`,
        dict[str, :class:`~azure.ai.formrecognizer.FormField`], or list[:class:`~azure.ai.formrecognizer.FormField`]
    :ivar float confidence:
        Measures the degree of certainty of the recognition result. Value is between [0.0, 1.0].

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        self.value_type = kwargs.get("value_type", None)
        self.label_data = kwargs.get("label_data", None)
        self.value_data = kwargs.get("value_data", None)
        self.name = kwargs.get("name", None)
        self.value = kwargs.get("value", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, field, value, read_result):
        return cls(
            value_type=adjust_value_type(value.type) if value else None,
            label_data=None,  # not returned with receipt/supervised
            value_data=FieldData._from_generated(value, read_result),
            value=get_field_value(field, value, read_result),
            name=field,
            confidence=adjust_confidence(value.confidence) if value else None,
        )

    @classmethod
    def _from_generated_unlabeled(cls, field, idx, page, read_result):
        return cls(
            value_type="string",  # unlabeled only returns string
            label_data=FieldData._from_generated_unlabeled(
                field.key, page, read_result
            ),
            value_data=FieldData._from_generated_unlabeled(
                field.value, page, read_result
            ),
            value=field.value.text,
            name="field-" + str(idx),
            confidence=adjust_confidence(field.confidence),
        )

    def __repr__(self):
        return (
                f"FormField(value_type={self.value_type}, label_data={repr(self.label_data)}, "
                f"value_data={repr(self.value_data)}, name={self.name}, value={repr(self.value)}, "
                f"confidence={self.confidence})"
            )[:1024]

    def to_dict(self) -> dict:
        """Returns a dict representation of FormField.

        :return: dict
        :rtype: dict
        """
        value = self.value
        if isinstance(self.value, dict):
            value = {k: v.to_dict() for k, v in self.value.items()}
        elif isinstance(self.value, list):
            value = [v.to_dict() for v in self.value]
        return {
            "value_type": self.value_type,
            "name": self.name,
            "value": value,
            "confidence": self.confidence,
            "label_data": self.label_data.to_dict() if self.label_data else None,
            "value_data": self.value_data.to_dict() if self.value_data else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FormField":
        """Converts a dict in the shape of a FormField to the model itself.

        :param dict data: A dictionary in the shape of FormField.
        :return: FormField
        :rtype: FormField
        """
        value = data.get("value", None)
        if isinstance(data.get("value"), dict):
            value = {k: FormField.from_dict(v) for k, v in data.get("value").items()}  # type: ignore
        elif isinstance(data.get("value"), list):
            value = [FormField.from_dict(v) for v in data.get("value")]  # type: ignore

        return cls(
            value_type=data.get("value_type", None),
            name=data.get("name", None),
            value=value,
            confidence=data.get("confidence", None),
            label_data=FieldData.from_dict(data.get("label_data"))  # type: ignore
            if data.get("label_data")
            else None,
            value_data=FieldData.from_dict(data.get("value_data"))  # type: ignore
            if data.get("value_data")
            else None,
        )


class FieldData:
    """Contains the data for the form field. This includes the text,
    location of the text on the form, and a collection of the
    elements that make up the text.

    :ivar int page_number:
        The 1-based number of the page in which this content is present.
    :ivar str text: The string representation of the field or value.
    :ivar list[~azure.ai.formrecognizer.Point] bounding_box:
        A list of 4 points representing the quadrilateral bounding box
        that outlines the text. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF.
    :ivar field_elements:
        When `include_field_elements` is set to true, a list of
        elements constituting this field or value is returned. The list
        constitutes of elements such as lines, words, and selection marks.
    :vartype field_elements: list[Union[~azure.ai.formrecognizer.FormElement, ~azure.ai.formrecognizer.FormWord,
        ~azure.ai.formrecognizer.FormLine,  ~azure.ai.formrecognizer.FormSelectionMark]]

    .. versionadded:: v2.1
        *FormSelectionMark* is added to the types returned in the list of field_elements, support for
        *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        self.page_number = kwargs.get("page_number", None)
        self.text = kwargs.get("text", None)
        self.bounding_box = kwargs.get("bounding_box", None)
        self.field_elements = kwargs.get("field_elements", None)

    @classmethod
    def _from_generated(cls, field, read_result):
        if field is None or all(
            field_data is None
            for field_data in [field.page, field.text, field.bounding_box]
        ):
            return None
        return cls(
            page_number=field.page,
            text=field.text,
            bounding_box=get_bounding_box(field),
            field_elements=[
                resolve_element(element, read_result) for element in field.elements
            ]
            if field.elements
            else None,
        )

    @classmethod
    def _from_generated_unlabeled(cls, field, page, read_result):
        return cls(
            page_number=page,
            text=field.text,
            bounding_box=get_bounding_box(field),
            field_elements=[
                resolve_element(element, read_result) for element in field.elements
            ]
            if field.elements
            else None,
        )

    def __repr__(self):
        return (
            f"FieldData(page_number={self.page_number}, text={self.text}, bounding_box={self.bounding_box}, "
            f"field_elements={repr(self.field_elements)})"
        )[:1024]

    def to_dict(self) -> dict:
        """Returns a dict representation of FieldData.

        :return: dict
        :rtype: dict
        """
        return {
            "text": self.text,
            "bounding_box": [f.to_dict() for f in self.bounding_box]
            if self.bounding_box
            else [],
            "page_number": self.page_number,
            "field_elements": [f.to_dict() for f in self.field_elements]
            if self.field_elements
            else [],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FieldData":
        """Converts a dict in the shape of a FieldData to the model itself.

        :param dict data: A dictionary in the shape of FieldData.
        :return: FieldData
        :rtype: FieldData
        """
        field_elements = []
        for v in data.get("field_elements"):  # type: ignore
            if v.get("kind") == "word":
                field_elements.append(FormWord.from_dict(v))
            elif v.get("kind") == "line":
                field_elements.append(FormLine.from_dict(v))  # type: ignore
            elif v.get("kind") == "selectionMark":
                field_elements.append(FormSelectionMark.from_dict(v))  # type: ignore
            else:
                field_elements.append(FormElement.from_dict(v))  # type: ignore

        return cls(
            text=data.get("text", None),
            page_number=data.get("page_number", None),
            bounding_box=[Point.from_dict(f) for f in data.get("bounding_box")]  # type: ignore
            if len(data.get("bounding_box", [])) > 0
            else [],
            field_elements=field_elements,
        )


class FormPage:
    """Represents a page recognized from the input document. Contains lines,
    words, selection marks, tables and page metadata.

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
        When `include_field_elements` is set to true, a list of recognized text lines is returned.
        For calls to recognize content, this list is always populated. The maximum number of lines
        returned is 300 per page. The lines are sorted top to bottom, left to right, although in
        certain cases proximity is treated with higher priority. As the sorting order depends on
        the detected text, it may change across images and OCR version updates. Thus, business
        logic should be built upon the actual line location instead of order. The reading order
        of lines can be specified by the `reading_order` keyword argument (Note: `reading_order`
        only supported in `begin_recognize_content` and `begin_recognize_content_from_url`).
    :ivar selection_marks: List of selection marks extracted from the page.
    :vartype selection_marks: list[~azure.ai.formrecognizer.FormSelectionMark]

    .. versionadded:: v2.1
        *selection_marks* property, support for *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        self.page_number = kwargs.get("page_number", None)
        self.text_angle = kwargs.get("text_angle", None)
        self.width = kwargs.get("width", None)
        self.height = kwargs.get("height", None)
        self.unit = kwargs.get("unit", None)
        self.tables = kwargs.get("tables", None)
        self.lines = kwargs.get("lines", None)
        self.selection_marks = kwargs.get("selection_marks", None)

    def __repr__(self):
        return (
            f"FormPage(page_number={self.page_number}, text_angle={self.text_angle}, "
            f"width={self.width}, height={self.height}, unit={self.unit}, tables={repr(self.tables)}, "
            f"lines={repr(self.lines)}, selection_marks={repr(self.selection_marks)})"
        )[:1024]

    def to_dict(self) -> dict:
        """Returns a dict representation of FormPage.

        :return: dict
        :rtype: dict
        """
        return {
            "page_number": self.page_number,
            "text_angle": self.text_angle,
            "width": self.width,
            "height": self.height,
            "unit": self.unit,
            "tables": [table.to_dict() for table in self.tables] if self.tables else [],
            "lines": [line.to_dict() for line in self.lines] if self.lines else [],
            "selection_marks": [mark.to_dict() for mark in self.selection_marks]
            if self.selection_marks
            else [],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FormPage":
        """Converts a dict in the shape of a FormPage to the model itself.

        :param dict data: A dictionary in the shape of FormPage.
        :return: FormPage
        :rtype: FormPage
        """
        return cls(
            text_angle=data.get("text_angle", None),
            width=data.get("width", None),
            height=data.get("height", None),
            unit=data.get("unit", None),
            page_number=data.get("page_number", None),
            tables=[FormTable.from_dict(v) for v in data.get("tables")]  # type: ignore
            if len(data.get("tables", [])) > 0
            else [],
            lines=[FormLine.from_dict(v) for v in data.get("lines")]  # type: ignore
            if len(data.get("lines", [])) > 0
            else [],
            selection_marks=[
                FormSelectionMark.from_dict(v) for v in data.get("selection_marks")  # type: ignore
            ]
            if len(data.get("selection_marks", [])) > 0
            else [],
        )


class FormLine(FormElement):
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
    :ivar str kind: For FormLine, this is "line".
    :ivar appearance: An object representing the appearance of the line.
    :vartype appearance: ~azure.ai.formrecognizer.Appearance

    .. versionadded:: v2.1
        *appearance* property, support for *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        super().__init__(kind="line", **kwargs)
        self.words = kwargs.get("words", None)
        self.appearance = kwargs.get("appearance", None)

    @classmethod
    def _from_generated(cls, line, page):
        line_appearance = (
            TextAppearance._from_generated(line.appearance)
            if hasattr(line, "appearance")
            else None
        )
        return cls(
            text=line.text,
            bounding_box=get_bounding_box(line),
            page_number=page,
            words=[FormWord._from_generated(word, page) for word in line.words]
            if line.words
            else None,
            appearance=line_appearance,
        )

    def __repr__(self):
        return (
            f"FormLine(text={self.text}, bounding_box={self.bounding_box}, words={repr(self.words)}, "
            f"page_number={self.page_number}, kind={self.kind}, appearance={self.appearance})"
        )[:1024]

    def to_dict(self) -> dict:
        """Returns a dict representation of FormLine.

        :return: dict
        :rtype: dict
        """
        return {
            "text": self.text,
            "bounding_box": [f.to_dict() for f in self.bounding_box]
            if self.bounding_box
            else [],
            "words": [f.to_dict() for f in self.words] if self.words else [],
            "page_number": self.page_number,
            "kind": self.kind,
            "appearance": self.appearance.to_dict() if self.appearance else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FormLine":
        """Converts a dict in the shape of a FormLine to the model itself.

        :param dict data: A dictionary in the shape of FormLine.
        :return: FormLine
        :rtype: FormLine
        """
        return cls(
            text=data.get("text", None),
            page_number=data.get("page_number", None),
            bounding_box=[Point.from_dict(v) for v in data.get("bounding_box")]  # type: ignore
            if len(data.get("bounding_box", [])) > 0
            else [],
            words=[FormWord.from_dict(v) for v in data.get("words")]  # type: ignore
            if len(data.get("words", [])) > 0
            else [],
            appearance=TextAppearance.from_dict(data.get("appearance"))  # type: ignore
            if data.get("appearance")
            else None,
        )


class FormWord(FormElement):
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
    :ivar str kind: For FormWord, this is "word".

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        super().__init__(kind="word", **kwargs)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, word, page):
        return cls(
            text=word.text,
            bounding_box=get_bounding_box(word),
            confidence=adjust_confidence(word.confidence),
            page_number=page,
        )

    def __repr__(self):
        return (
            f"FormWord(text={self.text}, bounding_box={self.bounding_box}, confidence={self.confidence}, "
            f"page_number={self.page_number}, kind={self.kind})"
        )[:1024]

    def to_dict(self) -> dict:
        """Returns a dict representation of FormWord.

        :return: dict
        :rtype: dict
        """
        return {
            "text": self.text,
            "bounding_box": [f.to_dict() for f in self.bounding_box]
            if self.bounding_box
            else [],
            "confidence": self.confidence,
            "page_number": self.page_number,
            "kind": self.kind,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FormWord":
        """Converts a dict in the shape of a FormWord to the model itself.

        :param dict data: A dictionary in the shape of FormWord.
        :return: FormWord
        :rtype: FormWord
        """
        return cls(
            text=data.get("text", None),
            page_number=data.get("page_number", None),
            bounding_box=[Point.from_dict(v) for v in data.get("bounding_box")]  # type: ignore
            if len(data.get("bounding_box", [])) > 0
            else [],
            confidence=data.get("confidence", None),
        )


class FormSelectionMark(FormElement):
    """Information about the extracted selection mark.

    :ivar str text: The text content - not returned for FormSelectionMark.
    :ivar list[~azure.ai.formrecognizer.Point] bounding_box:
        A list of 4 points representing the quadrilateral bounding box
        that outlines the text. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF.
    :ivar float confidence:
        Measures the degree of certainty of the recognition result. Value is between [0.0, 1.0].
    :ivar str state: State of the selection mark. Possible values include: "selected",
     "unselected".
    :ivar int page_number:
        The 1-based number of the page in which this content is present.
    :ivar str kind: For FormSelectionMark, this is "selectionMark".

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        super().__init__(kind="selectionMark", **kwargs)
        self.confidence = kwargs["confidence"]
        self.state = kwargs["state"]

    @classmethod
    def _from_generated(cls, mark, page):
        return cls(
            confidence=adjust_confidence(mark.confidence),
            state=mark.state,
            bounding_box=get_bounding_box(mark),
            page_number=page,
        )

    def __repr__(self):
        return (
            f"FormSelectionMark(text={self.text}, bounding_box={self.bounding_box}, confidence={self.confidence}, "
            f"page_number={self.page_number}, state={self.state}, kind={self.kind})"
        )[:1024]

    def to_dict(self) -> dict:
        """Returns a dict representation of FormSelectionMark.

        :return: dict
        :rtype: dict
        """
        return {
            "text": self.text,
            "bounding_box": [f.to_dict() for f in self.bounding_box]
            if self.bounding_box
            else [],
            "confidence": self.confidence,
            "state": self.state,
            "page_number": self.page_number,
            "kind": self.kind,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FormSelectionMark":
        """Converts a dict in the shape of a FormSelectionMark to the model itself.

        :param dict data: A dictionary in the shape of FormSelectionMark.
        :return: FormSelectionMark
        :rtype: FormSelectionMark
        """
        return cls(
            text=data.get("text", None),
            page_number=data.get("page_number", None),
            bounding_box=[Point.from_dict(v) for v in data.get("bounding_box")]  # type: ignore
            if len(data.get("bounding_box", [])) > 0
            else [],
            confidence=data.get("confidence", None),
            state=data.get("state", None),
        )


class FormTable:
    """Information about the extracted table contained on a page.

    :ivar int page_number:
        The 1-based number of the page in which this table is present.
    :ivar list[~azure.ai.formrecognizer.FormTableCell] cells:
        List of cells contained in the table.
    :ivar int row_count:
        Number of rows in table.
    :ivar int column_count:
        Number of columns in table.
    :ivar list[~azure.ai.formrecognizer.Point] bounding_box:
        A list of 4 points representing the quadrilateral bounding box
        that outlines the table. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF.

    .. versionadded:: v2.1
        The *bounding_box* property, support for *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        self.page_number = kwargs.get("page_number", None)
        self.cells = kwargs.get("cells", None)
        self.row_count = kwargs.get("row_count", None)
        self.column_count = kwargs.get("column_count", None)
        self.bounding_box = kwargs.get("bounding_box", None)

    def __repr__(self):
        return (
            f"FormTable(page_number={self.page_number}, cells={repr(self.cells)}, row_count={self.row_count}, "
            f"column_count={self.column_count}, bounding_box={self.bounding_box})"
        )[:1024]

    def to_dict(self) -> dict:
        """Returns a dict representation of FormTable.

        :return: dict
        :rtype: dict
        """
        return {
            "page_number": self.page_number,
            "row_count": self.row_count,
            "column_count": self.column_count,
            "cells": [cell.to_dict() for cell in self.cells],
            "bounding_box": [box.to_dict() for box in self.bounding_box]
            if self.bounding_box
            else [],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FormTable":
        """Converts a dict in the shape of a FormTable to the model itself.

        :param dict data: A dictionary in the shape of FormTable.
        :return: FormTable
        :rtype: FormTable
        """
        return cls(
            row_count=data.get("row_count", None),
            page_number=data.get("page_number", None),
            column_count=data.get("column_count", None),
            bounding_box=[Point.from_dict(v) for v in data.get("bounding_box")]  # type: ignore
            if len(data.get("bounding_box", [])) > 0
            else [],
            cells=[FormTableCell.from_dict(v) for v in data.get("cells")]  # type: ignore
            if len(data.get("cells", [])) > 0
            else [],
        )


class FormTableCell:  # pylint:disable=too-many-instance-attributes
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
    :ivar field_elements:
        When `include_field_elements` is set to true, a list of
        elements constituting this cell is returned. The list
        constitutes of elements such as lines, words, and selection marks.
        For calls to begin_recognize_content(), this list is always populated.
    :vartype field_elements: list[Union[~azure.ai.formrecognizer.FormElement, ~azure.ai.formrecognizer.FormWord,
        ~azure.ai.formrecognizer.FormLine, ~azure.ai.formrecognizer.FormSelectionMark]]

    .. versionadded:: v2.1
        *FormSelectionMark* is added to the types returned in the list of field_elements, support for
        *to_dict* and *from_dict* methods
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
        self.page_number = kwargs.get("page_number", None)
        self.field_elements = kwargs.get("field_elements", None)

    @classmethod
    def _from_generated(cls, cell, page, read_result):
        return cls(
            text=cell.text,
            row_index=cell.row_index,
            column_index=cell.column_index,
            row_span=cell.row_span or 1,
            column_span=cell.column_span or 1,
            bounding_box=get_bounding_box(cell),
            confidence=adjust_confidence(cell.confidence),
            is_header=cell.is_header or False,
            is_footer=cell.is_footer or False,
            page_number=page,
            field_elements=[
                resolve_element(element, read_result) for element in cell.elements
            ]
            if cell.elements
            else None,
        )

    def __repr__(self):
        return (
            f"FormTableCell(text={self.text}, row_index={self.row_index}, column_index={self.column_index}, "
            f"row_span={self.row_span}, column_span={self.column_span}, bounding_box={self.bounding_box}, "
            f"confidence={self.confidence}, is_header={self.is_header}, is_footer={self.is_footer}, "
            f"page_number={self.page_number}, field_elements={repr(self.field_elements)})"
        )[:1024]

    def to_dict(self) -> dict:
        """Returns a dict representation of FormTableCell.

        :return: dict
        :rtype: dict
        """
        return {
            "text": self.text,
            "row_index": self.row_index,
            "column_index": self.column_index,
            "row_span": self.row_span,
            "column_span": self.column_span,
            "confidence": self.confidence,
            "is_header": self.is_header,
            "is_footer": self.is_footer,
            "page_number": self.page_number,
            "bounding_box": [box.to_dict() for box in self.bounding_box]
            if self.bounding_box
            else [],
            "field_elements": [element.to_dict() for element in self.field_elements]
            if self.field_elements
            else [],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FormTableCell":
        """Converts a dict in the shape of a FormTableCell to the model itself.

        :param dict data: A dictionary in the shape of FormTableCell.
        :return: FormTableCell
        :rtype: FormTableCell
        """
        field_elements = []
        for v in data.get("field_elements"):  # type: ignore
            if v.get("kind") == "word":
                field_elements.append(FormWord.from_dict(v))  # type: ignore
            elif v.get("kind") == "line":
                field_elements.append(FormLine.from_dict(v))  # type: ignore
            elif v.get("kind") == "selectionMark":
                field_elements.append(FormSelectionMark.from_dict(v))  # type: ignore
            else:
                field_elements.append(FormElement.from_dict(v))  # type: ignore

        return cls(
            text=data.get("text", None),
            row_index=data.get("row_index", None),
            column_index=data.get("column_index", None),
            row_span=data.get("row_span", None),
            column_span=data.get("column_span", None),
            confidence=data.get("confidence", None),
            is_header=data.get("is_header", None),
            is_footer=data.get("is_footer", None),
            page_number=data.get("page_number", None),
            bounding_box=[Point.from_dict(v) for v in data.get("bounding_box")]  # type: ignore
            if len(data.get("bounding_box", [])) > 0
            else [],
            field_elements=field_elements,
        )


class CustomFormModel:
    """Represents a trained model.

    :ivar str model_id: The unique identifier of this model.
    :ivar str status:
        Status indicating the model's readiness for use,
        :class:`~azure.ai.formrecognizer.CustomFormModelStatus`.
        Possible values include: 'creating', 'ready', 'invalid'.
    :ivar ~datetime.datetime training_started_on:
        The date and time (UTC) when model training was started.
    :ivar ~datetime.datetime training_completed_on:
        Date and time (UTC) when model training completed.
    :ivar list[~azure.ai.formrecognizer.CustomFormSubmodel] submodels:
        A list of submodels that are part of this model, each of
        which can recognize and extract fields from a different type of form.
    :ivar list[~azure.ai.formrecognizer.FormRecognizerError] errors:
        List of any training errors.
    :ivar list[~azure.ai.formrecognizer.TrainingDocumentInfo] training_documents:
         Metadata about each of the documents used to train the model.
    :ivar str model_name: Optional user defined model name.
    :ivar properties: Optional model properties.
    :vartype properties: ~azure.ai.formrecognizer.CustomFormModelProperties

    .. versionadded:: v2.1
        The *model_name* and *properties* properties, support for *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        self.model_id = kwargs.get("model_id", None)
        self.status = kwargs.get("status", None)
        self.training_started_on = kwargs.get("training_started_on", None)
        self.training_completed_on = kwargs.get("training_completed_on", None)
        self.submodels = kwargs.get("submodels", None)
        self.errors = kwargs.get("errors", None)
        self.training_documents = kwargs.get("training_documents", None)
        self.model_name = kwargs.get("model_name", None)
        self.properties = kwargs.get("properties", None)

    @classmethod
    def _from_generated(cls, model, api_version):
        model_name = (
            model.model_info.model_name
            if hasattr(model.model_info, "model_name")
            else None
        )
        properties = (
            CustomFormModelProperties._from_generated(model.model_info)
            if hasattr(model.model_info, "attributes")
            else None
        )
        return cls(
            model_id=model.model_info.model_id,
            status=model.model_info.status,
            training_started_on=model.model_info.created_date_time,
            training_completed_on=model.model_info.last_updated_date_time,
            submodels=CustomFormSubmodel._from_generated_unlabeled(model)
            if model.keys
            else CustomFormSubmodel._from_generated_labeled(
                model, api_version, model_name=model_name
            ),
            errors=FormRecognizerError._from_generated(model.train_result.errors)
            if model.train_result
            else None,
            training_documents=TrainingDocumentInfo._from_generated(model.train_result)
            if model.train_result
            else None,
            properties=properties,
            model_name=model_name,
        )

    @classmethod
    def _from_generated_composed(cls, model):
        return cls(
            model_id=model.model_info.model_id,
            status=model.model_info.status,
            training_started_on=model.model_info.created_date_time,
            training_completed_on=model.model_info.last_updated_date_time,
            submodels=CustomFormSubmodel._from_generated_composed(model),
            training_documents=TrainingDocumentInfo._from_generated_composed(model),
            properties=CustomFormModelProperties._from_generated(model.model_info),
            model_name=model.model_info.model_name,
        )

    def __repr__(self):
        return (
            f"CustomFormModel(model_id={self.model_id}, status={self.status}, "
            f"training_started_on={self.training_started_on}, training_completed_on={self.training_completed_on}, "
            f"submodels={repr(self.submodels)}, errors={repr(self.errors)}, "
            f"training_documents={repr(self.training_documents)}, model_name={self.model_name}, "
            f"properties={repr(self.properties)})"
        )[:1024]

    def to_dict(self) -> dict:
        """Returns a dict representation of CustomFormModel.

        :return: dict
        :rtype: dict
        """
        return {
            "model_id": self.model_id,
            "status": self.status,
            "training_started_on": self.training_started_on,
            "training_completed_on": self.training_completed_on,
            "submodels": [submodel.to_dict() for submodel in self.submodels]
            if self.submodels
            else [],
            "errors": [err.to_dict() for err in self.errors] if self.errors else [],
            "training_documents": [doc.to_dict() for doc in self.training_documents]
            if self.training_documents
            else [],
            "model_name": self.model_name,
            "properties": self.properties.to_dict() if self.properties else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CustomFormModel":
        """Converts a dict in the shape of a CustomFormModel to the model itself.

        :param dict data: A dictionary in the shape of CustomFormModel.
        :return: CustomFormModel
        :rtype: CustomFormModel
        """
        return cls(
            model_id=data.get("model_id", None),
            status=data.get("status", None),
            training_started_on=data.get("training_started_on", None),
            training_completed_on=data.get("training_completed_on", None),
            submodels=[CustomFormSubmodel.from_dict(v) for v in data.get("submodels")]  # type: ignore
            if len(data.get("submodels", [])) > 0
            else [],
            errors=[FormRecognizerError.from_dict(v) for v in data.get("errors")]  # type: ignore
            if len(data.get("errors", [])) > 0
            else [],
            training_documents=[
                TrainingDocumentInfo.from_dict(v) for v in data.get("training_documents")  # type: ignore
            ]
            if len(data.get("training_documents", [])) > 0
            else [],
            model_name=data.get("model_name", None),
            properties=CustomFormModelProperties.from_dict(data.get("properties"))  # type: ignore
            if data.get("properties")
            else None,
        )


class CustomFormSubmodel:
    """Represents a submodel that extracts fields from a specific type of form.

    :ivar str model_id: Model identifier of the submodel.
    :ivar float accuracy: The mean of the model's field accuracies.
    :ivar fields: A dictionary of the fields that this submodel will recognize
        from the input document. The fields dictionary keys are the `name` of
        the field. For models trained with labels, this is the training-time
        label of the field. For models trained without labels, a unique name
        is generated for each field.
    :vartype fields: dict[str, ~azure.ai.formrecognizer.CustomFormModelField]
    :ivar str form_type: Type of form this submodel recognizes.

    .. versionadded:: v2.1
        The *model_id* property, support for *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        self.model_id = kwargs.get("model_id", None)
        self.accuracy = kwargs.get("accuracy", None)
        self.fields = kwargs.get("fields", None)
        self.form_type = kwargs.get("form_type", None)

    @classmethod
    def _from_generated_unlabeled(cls, model):
        return [
            cls(
                model_id=model.model_info.model_id,
                accuracy=None,
                fields=CustomFormModelField._from_generated_unlabeled(fields),
                form_type="form-" + cluster_id,
            )
            for cluster_id, fields in model.keys.clusters.items()
        ]

    @classmethod
    def _from_generated_labeled(cls, model, api_version, model_name):
        if api_version == "2.0":
            form_type = "form-" + model.model_info.model_id
        elif model_name:
            form_type = "custom:" + model_name
        else:
            form_type = "custom:" + model.model_info.model_id

        return (
            [
                cls(
                    model_id=model.model_info.model_id,
                    accuracy=model.train_result.average_model_accuracy,
                    fields={
                        field.field_name: CustomFormModelField._from_generated_labeled(
                            field
                        )
                        for field in model.train_result.fields
                    }
                    if model.train_result.fields
                    else None,
                    form_type=form_type,
                )
            ]
            if model.train_result
            else None
        )

    @classmethod
    def _from_generated_composed(cls, model):
        return [
            cls(
                accuracy=train_result.average_model_accuracy,
                fields={
                    field.field_name: CustomFormModelField._from_generated_labeled(
                        field
                    )
                    for field in train_result.fields
                }
                if train_result.fields
                else None,
                form_type="custom:" + train_result.model_id,
                model_id=train_result.model_id,
            )
            for train_result in model.composed_train_results
        ]

    def __repr__(self):
        return (
            f"CustomFormSubmodel(accuracy={self.accuracy}, model_id={self.model_id}, "
            f"fields={repr(self.fields)}, form_type={self.form_type})"
        )[:1024]

    def to_dict(self) -> dict:
        """Returns a dict representation of CustomFormSubmodel.

        :return: dict
        :rtype: dict
        """
        return {
            "model_id": self.model_id,
            "accuracy": self.accuracy,
            "fields": {k: v.to_dict() for k, v in self.fields.items()}
            if self.fields
            else {},
            "form_type": self.form_type,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CustomFormSubmodel":
        """Converts a dict in the shape of a CustomFormSubmodel to the model itself.

        :param dict data: A dictionary in the shape of CustomFormSubmodel.
        :return: CustomFormSubmodel
        :rtype: CustomFormSubmodel
        """
        return cls(
            model_id=data.get("model_id", None),
            accuracy=data.get("accuracy", None),
            fields={k: CustomFormModelField.from_dict(v) for k, v in data.get("fields").items()}  # type: ignore
            if data.get("fields")
            else {},
            form_type=data.get("form_type", None),
        )


class CustomFormModelField:
    """A field that the model will extract from forms it analyzes.

    :ivar str label: The form fields label on the form.
    :ivar str name: Canonical name; uniquely identifies a field within the form.
    :ivar float accuracy: The estimated recognition accuracy for this field.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        self.label = kwargs.get("label", None)
        self.name = kwargs.get("name", None)
        self.accuracy = kwargs.get("accuracy", None)

    @classmethod
    def _from_generated_labeled(cls, field):
        return cls(name=field.field_name, accuracy=field.accuracy)

    @classmethod
    def _from_generated_unlabeled(cls, fields):
        return {
            f"field-{idx}": cls(
                name=f"field-{idx}",
                label=field_name,
            )
            for idx, field_name in enumerate(fields)
        }

    def __repr__(self):
        return f"CustomFormModelField(label={self.label}, name={self.name}, accuracy={self.accuracy})"[:1024]

    def to_dict(self) -> dict:
        """Returns a dict representation of CustomFormModelField.

        :return: dict
        :rtype: dict
        """
        return {"label": self.label, "accuracy": self.accuracy, "name": self.name}

    @classmethod
    def from_dict(cls, data: dict) -> "CustomFormModelField":
        """Converts a dict in the shape of a CustomFormModelField to the model itself.

        :param dict data: A dictionary in the shape of CustomFormModelField.
        :return: CustomFormModelField
        :rtype: CustomFormModelField
        """
        return cls(
            label=data.get("label", None),
            accuracy=data.get("accuracy", None),
            name=data.get("name", None),
        )


class TrainingDocumentInfo:
    """Report for an individual document used for training
    a custom model.

    :ivar str name:
        The name of the document.
    :ivar str status:
        The :class:`~azure.ai.formrecognizer.TrainingStatus`
        of the training operation. Possible values include:
        'succeeded', 'partiallySucceeded', 'failed'.
    :ivar int page_count:
        Total number of pages trained.
    :ivar list[~azure.ai.formrecognizer.FormRecognizerError] errors:
        List of any errors for document.
    :ivar str model_id:
        The model ID that used the document to train.

    .. versionadded:: v2.1
        The *model_id* property, support for *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        self.name = kwargs.get("name", None)
        self.status = kwargs.get("status", None)
        self.page_count = kwargs.get("page_count", None)
        self.errors = kwargs.get("errors", None)
        self.model_id = kwargs.get("model_id", None)

    @classmethod
    def _from_generated(cls, train_result):
        return (
            [
                cls(
                    name=doc.document_name,
                    status=doc.status,
                    page_count=doc.pages,
                    errors=FormRecognizerError._from_generated(doc.errors),
                    model_id=train_result.model_id
                    if hasattr(train_result, "model_id")
                    else None,
                )
                for doc in train_result.training_documents
            ]
            if train_result.training_documents
            else None
        )

    @classmethod
    def _from_generated_composed(cls, model):
        training_document_info = []
        for train_result in model.composed_train_results:
            for doc in train_result.training_documents:
                training_document_info.append(
                    cls(
                        name=doc.document_name,
                        status=doc.status,
                        page_count=doc.pages,
                        errors=FormRecognizerError._from_generated(doc.errors),
                        model_id=train_result.model_id,
                    )
                )
        return training_document_info

    def __repr__(self):
        return (
            f"TrainingDocumentInfo(name={self.name}, status={self.status}, page_count={self.page_count}, "
            f"errors={repr(self.errors)}, model_id={self.model_id})"[:1024]
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of TrainingDocumentInfo.

        :return: dict
        :rtype: dict
        """
        return {
            "name": self.name,
            "status": self.status,
            "page_count": self.page_count,
            "errors": [err.to_dict() for err in self.errors] if self.errors else [],
            "model_id": self.model_id,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TrainingDocumentInfo":
        """Converts a dict in the shape of a TrainingDocumentInfo to the model itself.

        :param dict data: A dictionary in the shape of TrainingDocumentInfo.
        :return: TrainingDocumentInfo
        :rtype: TrainingDocumentInfo
        """
        return cls(
            name=data.get("name", None),
            status=data.get("status", None),
            page_count=data.get("page_count", None),
            errors=[
                FormRecognizerError.from_dict(v) for v in data.get("errors")  # type: ignore
            ],
            model_id=data.get("model_id", None),
        )


class FormRecognizerError:
    """Represents an error that occurred while training.

    :ivar str code: Error code.
    :ivar str message: Error message.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        self.code = kwargs.get("code", None)
        self.message = kwargs.get("message", None)

    @classmethod
    def _from_generated(cls, err):
        return (
            [cls(code=error.code, message=error.message) for error in err]
            if err
            else []
        )

    def __repr__(self):
        return f"FormRecognizerError(code={self.code}, message={self.message})"[:1024]

    def to_dict(self) -> dict:
        """Returns a dict representation of FormRecognizerError.

        :return: dict
        :rtype: dict
        """
        return {"code": self.code, "message": self.message}

    @classmethod
    def from_dict(cls, data: dict) -> "FormRecognizerError":
        """Converts a dict in the shape of a FormRecognizerError to the model itself.

        :param dict data: A dictionary in the shape of FormRecognizerError.
        :return: FormRecognizerError
        :rtype: FormRecognizerError
        """
        return cls(
            code=data.get("code", None),
            message=data.get("message", None),
        )


class CustomFormModelInfo:
    """Custom model information.

    :ivar str model_id: The unique identifier of the model.
    :ivar str status:
        The status of the model, :class:`~azure.ai.formrecognizer.CustomFormModelStatus`.
        Possible values include: 'creating', 'ready', 'invalid'.
    :ivar ~datetime.datetime training_started_on:
        Date and time (UTC) when model training was started.
    :ivar ~datetime.datetime training_completed_on:
        Date and time (UTC) when model training completed.
    :ivar model_name: Optional user defined model name.
    :vartype model_name: str
    :ivar properties: Optional model properties.
    :vartype properties: ~azure.ai.formrecognizer.CustomFormModelProperties

    .. versionadded:: v2.1
        The *model_name* and *properties* properties, support for *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        self.model_id = kwargs.get("model_id", None)
        self.status = kwargs.get("status", None)
        self.training_started_on = kwargs.get("training_started_on", None)
        self.training_completed_on = kwargs.get("training_completed_on", None)
        self.model_name = kwargs.get("model_name", None)
        self.properties = kwargs.get("properties", None)

    @classmethod
    def _from_generated(cls, model, model_id=None, **kwargs):
        if model.status == "succeeded":  # map copy status to model status
            model.status = "ready"

        model_name = None
        if hasattr(model, "attributes"):
            properties = CustomFormModelProperties._from_generated(model)
        elif kwargs.pop("api_version", None) == "2.0":
            properties = None
        else:
            properties = CustomFormModelProperties(is_composed_model=False)
        if hasattr(model, "model_name"):
            model_name = model.model_name
        return cls(
            model_id=model_id if model_id else model.model_id,
            status=model.status,
            training_started_on=model.created_date_time,
            training_completed_on=model.last_updated_date_time,
            properties=properties,
            model_name=model_name,
        )

    def __repr__(self):
        return (
            f"CustomFormModelInfo(model_id={self.model_id}, status={self.status}, "
            f"training_started_on={self.training_started_on}, training_completed_on={self.training_completed_on}, "
            f"properties={repr(self.properties)}, model_name={self.model_name})"
        )[:1024]

    def to_dict(self) -> dict:
        """Returns a dict representation of CustomFormModelInfo.

        :return: dict
        :rtype: dict
        """
        return {
            "model_id": self.model_id,
            "status": self.status,
            "training_started_on": self.training_started_on,
            "training_completed_on": self.training_completed_on,
            "model_name": self.model_name,
            "properties": self.properties.to_dict() if self.properties else None,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CustomFormModelInfo":
        """Converts a dict in the shape of a CustomFormModelInfo to the model itself.

        :param dict data: A dictionary in the shape of CustomFormModelInfo.
        :return: CustomFormModelInfo
        :rtype: CustomFormModelInfo
        """
        return cls(
            model_id=data.get("model_id", None),
            status=data.get("status", None),
            training_started_on=data.get("training_started_on", None),
            training_completed_on=data.get("training_completed_on", None),
            model_name=data.get("model_name", None),
            properties=CustomFormModelProperties.from_dict(data.get("properties"))  # type: ignore
            if data.get("properties")
            else None,
        )


class AccountProperties:
    """Summary of all the custom models on the account.

    :ivar int custom_model_count: Current count of trained custom models.
    :ivar int custom_model_limit: Max number of models that can be trained for this account.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
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
        return (
            f"AccountProperties(custom_model_count={self.custom_model_count}, "
            f"custom_model_limit={self.custom_model_limit})"
        )[:1024]

    def to_dict(self) -> dict:
        """Returns a dict representation of AccountProperties.

        :return: dict
        :rtype: dict
        """
        return {
            "custom_model_count": self.custom_model_count,
            "custom_model_limit": self.custom_model_limit,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AccountProperties":
        """Converts a dict in the shape of a AccountProperties to the model itself.

        :param dict data: A dictionary in the shape of AccountProperties.
        :return: AccountProperties
        :rtype: AccountProperties
        """
        return cls(
            custom_model_count=data.get("custom_model_count", None),
            custom_model_limit=data.get("custom_model_limit", None),
        )


class CustomFormModelProperties:
    """Optional model properties.

    :ivar bool is_composed_model: Is this model composed? (default: false).

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        self.is_composed_model = kwargs.get("is_composed_model", False)

    @classmethod
    def _from_generated(cls, model_info):
        if model_info.attributes:
            return cls(is_composed_model=model_info.attributes.is_composed)
        return cls(is_composed_model=False)

    def __repr__(self):
        return f"CustomFormModelProperties(is_composed_model={self.is_composed_model})"

    def to_dict(self) -> dict:
        """Returns a dict representation of CustomFormModelProperties.

        :return: dict
        :rtype: dict
        """
        return {"is_composed_model": self.is_composed_model}

    @classmethod
    def from_dict(cls, data: dict) -> "CustomFormModelProperties":
        """Converts a dict in the shape of a CustomFormModelProperties to the model itself.

        :param dict data: A dictionary in the shape of CustomFormModelProperties.
        :return: CustomFormModelProperties
        :rtype: CustomFormModelProperties
        """
        return cls(
            is_composed_model=data.get("is_composed_model", None),
        )


class DocumentSpan:
    """Contiguous region of the content of the property, specified as an offset and length.

    :ivar int offset: Zero-based index of the content represented by the span.
    :ivar int length: Number of characters in the content represented by the span.
    """

    def __init__(self, **kwargs):
        self.offset = kwargs.get("offset", None)
        self.length = kwargs.get("length", None)

    @classmethod
    def _from_generated(cls, span):
        if span is None:
            return span
        return cls(
            offset=span.offset,
            length=span.length,
        )

    def __repr__(self):
        return f"DocumentSpan(offset={self.offset}, length={self.length})"

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentSpan.

        :return: dict
        :rtype: dict
        """
        return {
            "offset": self.offset,
            "length": self.length,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentSpan":
        """Converts a dict in the shape of a DocumentSpan to the model itself.

        :param dict data: A dictionary in the shape of DocumentSpan.
        :return: DocumentSpan
        :rtype: DocumentSpan
        """
        return cls(
            offset=data.get("offset", None),
            length=data.get("length", None),
        )


class TextAppearance:
    """An object representing the appearance of the text line.

    :ivar str style_name: The text line style name.
        Possible values include: "other", "handwriting".
    :ivar float style_confidence: The confidence of text line style.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """

    def __init__(self, **kwargs):
        self.style_name = kwargs.get("style_name", None)
        self.style_confidence = kwargs.get("style_confidence", None)

    @classmethod
    def _from_generated(cls, appearance):
        if appearance is None:
            return appearance
        return cls(
            style_name=appearance.style.name,
            style_confidence=appearance.style.confidence,
        )

    def __repr__(self):
        return f"TextAppearance(style_name={self.style_name}, style_confidence={self.style_confidence})"

    def to_dict(self) -> dict:
        """Returns a dict representation of TextAppearance.

        :return: dict
        :rtype: dict
        """
        return {
            "style_name": self.style_name,
            "style_confidence": self.style_confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "TextAppearance":
        """Converts a dict in the shape of a TextAppearance to the model itself.

        :param dict data: A dictionary in the shape of TextAppearance.
        :return: TextAppearance
        :rtype: TextAppearance
        """
        return cls(
            style_name=data.get("style_name", None),
            style_confidence=data.get("style_confidence", None),
        )


class BoundingRegion:
    """The bounding region corresponding to a page.

    :ivar Optional[list[~azure.ai.formrecognizer.Point]] polygon:
        A list of points representing the bounding polygon
        that outlines the document component. The points are listed in
        clockwise order relative to the document component orientation
        starting from the top-left.
        Units are in pixels for images and inches for PDF.
    :ivar int page_number:
        The 1-based number of the page in which this content is present.
    """

    def __init__(self, **kwargs):
        self.page_number = kwargs.get("page_number", None)
        self.polygon = kwargs.get("polygon", None)

    def __repr__(self):
        return f"BoundingRegion(page_number={self.page_number}, polygon={self.polygon})"

    @classmethod
    def _from_generated(cls, region):
        return cls(
            page_number=region.page_number,
            polygon=get_polygon(region),
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of BoundingRegion.

        :return: dict
        :rtype: dict
        """
        return {
            "page_number": self.page_number,
            "polygon": [f.to_dict() for f in self.polygon]
            if self.polygon
            else [],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "BoundingRegion":
        """Converts a dict in the shape of a BoundingRegion to the model itself.

        :param dict data: A dictionary in the shape of BoundingRegion.
        :return: BoundingRegion
        :rtype: BoundingRegion
        """
        return cls(
            page_number=data.get("page_number", None),
            polygon=[Point.from_dict(v) for v in data.get("polygon")]  # type: ignore
            if len(data.get("polygon", [])) > 0
            else [],
        )


class AddressValue:
    """An address field value.

    :ivar house_number: House or building number.
    :vartype house_number: Optional[str]
    :ivar po_box: Post office box number.
    :vartype po_box: Optional[str]
    :ivar road: Street name.
    :vartype road: Optional[str]
    :ivar city: Name of city, town, village, etc.
    :vartype city: Optional[str]
    :ivar state: First-level administrative division.
    :vartype state: Optional[str]
    :ivar postal_code: Postal code used for mail sorting.
    :vartype postal_code: Optional[str]
    :ivar country_region: Country/region.
    :vartype country_region: Optional[str]
    :ivar street_address: Street-level address, excluding city, state, countryRegion, and
     postalCode.
    :vartype street_address: Optional[str]
    """

    def __init__(self, **kwargs):
        self.house_number = kwargs.get("house_number", None)
        self.po_box = kwargs.get("po_box", None)
        self.road = kwargs.get("road", None)
        self.city = kwargs.get("city", None)
        self.state = kwargs.get("state", None)
        self.postal_code = kwargs.get("postal_code", None)
        self.country_region = kwargs.get("country_region", None)
        self.street_address = kwargs.get("street_address", None)

    @classmethod
    def _from_generated(cls, data):
        return cls(
            house_number=data.house_number,
            po_box=data.po_box,
            road=data.road,
            city=data.city,
            state=data.state,
            postal_code=data.postal_code,
            country_region=data.country_region,
            street_address=data.street_address,
        )

    def __repr__(self):
        return (
            f"AddressValue(house_number={self.house_number}, po_box={self.po_box}, road={self.road}, "
            f"city={self.city}, state={self.state}, postal_code={self.postal_code}, "
            f"country_region={self.country_region}, street_address={self.street_address})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of AddressValue.

        :return: dict
        :rtype: dict
        """
        return {
            "house_number": self.house_number,
            "po_box": self.po_box,
            "road": self.road,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country_region": self.country_region,
            "street_address": self.street_address,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AddressValue":
        """Converts a dict in the shape of a AddressValue to the model itself.

        :param dict data: A dictionary in the shape of AddressValue.
        :return: AddressValue
        :rtype: AddressValue
        """
        return cls(
            house_number=data.get("house_number", None),
            po_box=data.get("po_box", None),
            road=data.get("road", None),
            city=data.get("city", None),
            state=data.get("state", None),
            postal_code=data.get("postal_code", None),
            country_region=data.get("country_region", None),
            street_address=data.get("street_address", None),
        )


class CurrencyValue:
    """A currency value element.

    :ivar amount: The currency amount.
    :vartype: float
    :ivar symbol: The currency symbol, if found.
    :vartype: Optional[str]
    """

    def __init__(self, **kwargs):
        self.amount = kwargs.get("amount", None)
        self.symbol = kwargs.get("symbol", None)

    @classmethod
    def _from_generated(cls, data):
        return cls(
            amount=data.amount,
            symbol=data.currency_symbol,
        )

    def __str__(self):
        if self.symbol is not None:
            return f"{self.symbol}{self.amount}"
        return f"{self.amount}"

    def __repr__(self):
        return f"CurrencyValue(amount={self.amount}, symbol={self.symbol})"

    def to_dict(self) -> dict:
        """Returns a dict representation of CurrencyValue.

        :return: dict
        :rtype: dict
        """
        return {
            "amount": self.amount,
            "symbol": self.symbol,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "CurrencyValue":
        """Converts a dict in the shape of a CurrencyValue to the model itself.

        :param dict data: A dictionary in the shape of CurrencyValue.
        :return: CurrencyValue
        :rtype: CurrencyValue
        """
        return cls(
            amount=data.get("amount", None),
            symbol=data.get("symbol", None),
        )


class DocumentContentElement:
    """A DocumentContentElement.

    :ivar content: Text content of the document content element.
    :vartype content: str
    :ivar polygon: Bounding polygon of the document content element.
    :vartype polygon: Optional[list[~azure.ai.formrecognizer.Point]]
    :ivar span: Location of the element in the full document content.
    :vartype span: ~azure.ai.formrecognizer.DocumentSpan
    :ivar confidence: Confidence of accurately extracting the document content element.
    :vartype confidence: float
    :ivar str kind: The kind of document element. Possible kinds are "word" or "selectionMark" which
        correspond to a :class:`~azure.ai.formrecognizer.DocumentWord` or
        :class:`~azure.ai.formrecognizer.DocumentSelectionMark`, respectively.
    """

    def __init__(self, **kwargs):
        self.content = kwargs.get("content", None)
        self.polygon = kwargs.get("polygon", None)
        self.span = kwargs.get("span", None)
        self.confidence = kwargs.get("confidence", None)
        self.kind = kwargs.get("kind", None)

    def __repr__(self):
        return (
            f"DocumentContentElement(content={self.content}, polygon={self.polygon}, span={self.span}, "
            f"confidence={self.confidence}, kind={self.kind})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentContentElement.

        :return: dict
        :rtype: dict
        """
        return {
            "content": self.content,
            "polygon": [f.to_dict() for f in self.polygon]
            if self.polygon
            else [],
            "span": self.span.to_dict() if self.span else None,
            "confidence": self.confidence,
            "kind": self.kind,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentContentElement":
        """Converts a dict in the shape of a DocumentContentElement to the model itself.

        :param dict data: A dictionary in the shape of DocumentContentElement.
        :return: DocumentContentElement
        :rtype: DocumentContentElement
        """
        return cls(
            content=data.get("content", None),
            polygon=[Point.from_dict(v) for v in data.get("polygon")]  # type: ignore
            if len(data.get("polygon", [])) > 0
            else [],
            span=DocumentSpan.from_dict(data.get("span")) if data.get("span") else None,  # type: ignore
            confidence=data.get("confidence", None),
            kind=data.get("kind", None),
        )


class DocumentLanguage:
    """An object representing the detected language for a given text span.

    :ivar locale: Detected language code. Value may be an ISO 639-1 language code (ex.
     "en", "fr") or a BCP 47 language tag (ex. "zh-Hans").
    :vartype locale: str
    :ivar spans: Location of the text elements in the concatenated content that the language
     applies to.
    :vartype spans: list[~azure.ai.formrecognizer.DocumentSpan]
    :ivar confidence: Confidence of correctly identifying the language.
    :vartype confidence: float
    """

    def __init__(self, **kwargs):
        self.locale = kwargs.get("locale", None)
        self.spans = kwargs.get("spans", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, language):
        return cls(
            locale=language.locale,
            spans=prepare_document_spans(language.spans),
            confidence=language.confidence,
        )

    def __repr__(self):
        return f"DocumentLanguage(locale={self.locale}, spans={repr(self.spans)}, confidence={self.confidence})"

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentLanguage.

        :return: dict
        :rtype: dict
        """
        return {
            "locale": self.locale,
            "spans": [f.to_dict() for f in self.spans]
            if self.spans
            else [],
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentLanguage":
        """Converts a dict in the shape of a DocumentLanguage to the model itself.

        :param dict data: A dictionary in the shape of DocumentLanguage.
        :return: DocumentLanguage
        :rtype: DocumentLanguage
        """
        return cls(
            locale=data.get("locale", None),
            spans=[DocumentSpan.from_dict(v) for v in data.get("spans")]  # type: ignore
            if len(data.get("spans", [])) > 0
            else [],
            confidence=data.get("confidence", None),
        )


class AnalyzedDocument:
    """An object describing the location and semantic content of a document.

    :ivar doc_type: The type of document that was analyzed.
    :vartype doc_type: str
    :ivar bounding_regions: Bounding regions covering the document.
    :vartype bounding_regions: Optional[list[~azure.ai.formrecognizer.BoundingRegion]]
    :ivar spans: The location of the document in the reading order concatenated content.
    :vartype spans: list[~azure.ai.formrecognizer.DocumentSpan]
    :ivar fields: A dictionary of named field values.
    :vartype fields: Optional[dict[str, ~azure.ai.formrecognizer.DocumentField]]
    :ivar confidence: Confidence of correctly extracting the document.
    :vartype confidence: float
    """

    def __init__(self, **kwargs):
        self.doc_type = kwargs.get("doc_type", None)
        self.bounding_regions = kwargs.get("bounding_regions", None)
        self.spans = kwargs.get("spans", None)
        self.fields = kwargs.get("fields", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, document):
        return cls(
            doc_type=document.doc_type,
            bounding_regions=prepare_bounding_regions(document.bounding_regions),
            spans=prepare_document_spans(document.spans),
            fields={
                key: DocumentField._from_generated(field)
                for key, field in document.fields.items()
            }
            if document.fields
            else {},
            confidence=document.confidence,
        )

    def __repr__(self):
        return (
            f"AnalyzedDocument(doc_type={self.doc_type}, bounding_regions={repr(self.bounding_regions)}, "
            f"spans={repr(self.spans)}, fields={repr(self.fields)}, confidence={self.confidence})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of AnalyzedDocument.

        :return: dict
        :rtype: dict
        """
        return {
            "doc_type": self.doc_type,
            "bounding_regions": [f.to_dict() for f in self.bounding_regions]
            if self.bounding_regions
            else [],
            "spans": [f.to_dict() for f in self.spans]
            if self.spans
            else [],
            "fields": {k: v.to_dict() for k, v in self.fields.items()}
            if self.fields
            else {},
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AnalyzedDocument":
        """Converts a dict in the shape of a AnalyzedDocument to the model itself.

        :param dict data: A dictionary in the shape of AnalyzedDocument.
        :return: AnalyzedDocument
        :rtype: AnalyzedDocument
        """
        return cls(
            doc_type=data.get("doc_type", None),
            bounding_regions=[BoundingRegion.from_dict(v) for v in data.get("bounding_regions")]  # type: ignore
            if len(data.get("bounding_regions", [])) > 0
            else [],
            spans=[DocumentSpan.from_dict(v) for v in data.get("spans")]  # type: ignore
            if len(data.get("spans", [])) > 0
            else [],
            fields={k: DocumentField.from_dict(v) for k, v in data.get("fields").items()}  # type: ignore
            if data.get("fields")
            else {},
            confidence=data.get("confidence", None),
        )


class DocumentField:
    """An object representing the content and location of a document field value.

    :ivar str value_type: The type of `value` found on DocumentField. Possible types include:
     "string", "date", "time", "phoneNumber", "float", "integer", "selectionMark", "countryRegion",
     "signature", "currency", "list", "dictionary".
    :ivar value:
        The value for the recognized field. Its semantic data type is described by `value_type`.
        If the value is extracted from the document, but cannot be normalized to its type,
        then access the `content` property for a textual representation of the value.
    :vartype value: str, int, float, :class:`~datetime.date`, :class:`~datetime.time`,
        :class:`~azure.ai.formrecognizer.CurrencyValue`, :class:`~azure.ai.formrecognizer.AddressValue`,
        dict[str, :class:`~azure.ai.formrecognizer.DocumentField`],
        or list[:class:`~azure.ai.formrecognizer.DocumentField`]
    :ivar content: The field's content.
    :vartype content: Optional[str]
    :ivar bounding_regions: Bounding regions covering the field.
    :vartype bounding_regions: Optional[list[~azure.ai.formrecognizer.BoundingRegion]]
    :ivar spans: Location of the field in the reading order concatenated content.
    :vartype spans: Optional[list[~azure.ai.formrecognizer.DocumentSpan]]
    :ivar confidence: The confidence of correctly extracting the field.
    :vartype confidence: float
    """

    def __init__(self, **kwargs):
        self.value_type = kwargs.get("value_type", None)
        self.value = kwargs.get("value", None)
        self.content = kwargs.get("content", None)
        self.bounding_regions = kwargs.get("bounding_regions", None)
        self.spans = kwargs.get("spans", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, field):
        if field is None:
            return None
        return cls(
            value=get_field_value_v3(field),
            value_type=adjust_value_type(field.type) if field.type else None,
            content=field.content if field.content else None,
            bounding_regions=[
                BoundingRegion(
                    page_number=region.page_number,
                    polygon=get_polygon(region),
                )
                for region in field.bounding_regions
            ]
            if field.bounding_regions
            else [],
            spans=[
                DocumentSpan(
                    offset=span.offset,
                    length=span.length,
                )
                for span in field.spans
            ]
            if field.spans
            else [],
            confidence=field.confidence if field.confidence else None,
        )

    def __repr__(self):
        return (
            f"DocumentField(value_type={self.value_type}, value={repr(self.value)}, content={self.content}, "
            f"bounding_regions={repr(self.bounding_regions)}, spans={repr(self.spans)}, "
            f"confidence={self.confidence})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentField.

        :return: dict
        :rtype: dict
        """
        value = self.value
        # CurrencyValue objects are interpreted as dict, therefore need to be processed first
        # to call the proper to_dict() method.
        if self.value_type == "currency":
            value = self.value.to_dict()
        # AddressValue objects are interpreted as dict, therefore need to be processed first
        # to call the proper to_dict() method.
        elif self.value_type == "address":
            value = self.value.to_dict()
        elif isinstance(self.value, dict):
            value = {k: v.to_dict() for k, v in self.value.items()}
        elif isinstance(self.value, list):
            value = [v.to_dict() for v in self.value]
        return {
            "value_type": self.value_type,
            "value": value,
            "content": self.content,
            "bounding_regions": [f.to_dict() for f in self.bounding_regions]
            if self.bounding_regions
            else [],
            "spans": [f.to_dict() for f in self.spans]
            if self.spans
            else [],
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentField":
        """Converts a dict in the shape of a DocumentField to the model itself.

        :param dict data: A dictionary in the shape of DocumentField.
        :return: DocumentField
        :rtype: DocumentField
        """

        value = data.get("value", None)
        # CurrencyValue objects are interpreted as dict, therefore need to be processed first
        # to call the proper from_dict() method.
        if data.get("value_type", None) == "currency":
            value = CurrencyValue.from_dict(data.get("value"))  #type: ignore
        # AddressValue objects are interpreted as dict, therefore need to be processed first
        # to call the proper from_dict() method.
        elif data.get("value_type", None) == "address":
            value = AddressValue.from_dict(data.get("value"))  #type: ignore
        elif isinstance(data.get("value"), dict):
            value = {k: DocumentField.from_dict(v) for k, v in data.get("value").items()}  # type: ignore
        elif isinstance(data.get("value"), list):
            value = [DocumentField.from_dict(v) for v in data.get("value")]  # type: ignore

        return cls(
            value_type=data.get("value_type", None),
            value=value,
            content=data.get("content", None),
            bounding_regions=[BoundingRegion.from_dict(v) for v in data.get("bounding_regions")]  # type: ignore
            if len(data.get("bounding_regions", [])) > 0
            else [],
            spans=[DocumentSpan.from_dict(v) for v in data.get("spans")]  # type: ignore
            if len(data.get("spans", [])) > 0
            else [],
            confidence=data.get("confidence", None),
        )


class DocumentKeyValueElement:
    """An object representing the field key or value in a key-value pair.

    :ivar content: Concatenated content of the key-value element in reading order.
    :vartype content: str
    :ivar bounding_regions: Bounding regions covering the key-value element.
    :vartype bounding_regions: Optional[list[~azure.ai.formrecognizer.BoundingRegion]]
    :ivar spans: Location of the key-value element in the reading order of the concatenated
     content.
    :vartype spans: list[~azure.ai.formrecognizer.DocumentSpan]
    """

    def __init__(self, **kwargs):
        self.content = kwargs.get("content", None)
        self.bounding_regions = kwargs.get("bounding_regions", None)
        self.spans = kwargs.get("spans", None)

    @classmethod
    def _from_generated(cls, element):
        return cls(
            content=element.content,
            bounding_regions=[
                BoundingRegion._from_generated(region)
                for region in element.bounding_regions
            ]
            if element.bounding_regions
            else [],
            spans=[DocumentSpan._from_generated(span) for span in element.spans]
            if element.spans
            else [],
        )

    def __repr__(self):
        return (
            f"DocumentKeyValueElement(content={self.content}, bounding_regions={repr(self.bounding_regions)}, "
            f"spans={repr(self.spans)})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentKeyValueElement.

        :return: dict
        :rtype: dict
        """
        return {
            "content": self.content,
            "bounding_regions": [f.to_dict() for f in self.bounding_regions]
            if self.bounding_regions
            else [],
            "spans": [f.to_dict() for f in self.spans]
            if self.spans
            else [],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentKeyValueElement":
        """Converts a dict in the shape of a DocumentKeyValueElement to the model itself.

        :param dict data: A dictionary in the shape of DocumentKeyValueElement.
        :return: DocumentKeyValueElement
        :rtype: DocumentKeyValueElement
        """
        return cls(
            content=data.get("content", None),
            bounding_regions=[BoundingRegion.from_dict(v) for v in data.get("bounding_regions")]  # type: ignore
            if len(data.get("bounding_regions", [])) > 0
            else [],
            spans=[DocumentSpan.from_dict(v) for v in data.get("spans")]  # type: ignore
            if len(data.get("spans", [])) > 0
            else [],
        )


class DocumentKeyValuePair:
    """An object representing a document field with distinct field label (key) and field value (may be empty).

    :ivar key: Field label of the key-value pair.
    :vartype key: ~azure.ai.formrecognizer.DocumentKeyValueElement
    :ivar value: Field value of the key-value pair.
    :vartype value: ~azure.ai.formrecognizer.DocumentKeyValueElement
    :ivar confidence: Confidence of correctly extracting the key-value pair.
    :vartype confidence: float
    """

    def __init__(self, **kwargs):
        self.key = kwargs.get("key", None)
        self.value = kwargs.get("value", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, key_value_pair):
        return cls(
            key=DocumentKeyValueElement._from_generated(key_value_pair.key)
            if key_value_pair.key
            else None,
            value=DocumentKeyValueElement._from_generated(key_value_pair.value)
            if key_value_pair.value
            else None,
            confidence=key_value_pair.confidence,
        )

    def __repr__(self):
        return (
            f"DocumentKeyValuePair(key={repr(self.key)}, value={repr(self.value)}, "
            f"confidence={self.confidence})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentKeyValuePair.

        :return: dict
        :rtype: dict
        """
        return {
            "key": self.key.to_dict() if self.key else None,
            "value": self.value.to_dict() if self.value else None,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentKeyValuePair":
        """Converts a dict in the shape of a DocumentKeyValuePair to the model itself.

        :param dict data: A dictionary in the shape of DocumentKeyValuePair.
        :return: DocumentKeyValuePair
        :rtype: DocumentKeyValuePair
        """
        return cls(
            key=DocumentKeyValueElement.from_dict(data.get("key"))  # type: ignore
            if data.get("key")
            else None,
            value=DocumentKeyValueElement.from_dict(data.get("value"))  # type: ignore
            if data.get("value")
            else None,
            confidence=data.get("confidence", None),
        )


class DocumentLine:
    """A content line object representing the content found on a single line of the document.

    :ivar content: Concatenated content of the contained elements in reading order.
    :vartype content: str
    :ivar polygon: Bounding polygon of the line.
    :vartype polygon: Optional[list[~azure.ai.formrecognizer.Point]]
    :ivar spans: Location of the line in the reading order concatenated content.
    :vartype spans: list[~azure.ai.formrecognizer.DocumentSpan]
    """

    def __init__(self, **kwargs):
        self._parent = kwargs.get("_parent", None)
        self.content = kwargs.get("content", None)
        self.polygon = kwargs.get("polygon", None)
        self.spans = kwargs.get("spans", None)

    @classmethod
    def _from_generated(cls, line, document_page):
        return cls(
            _parent=document_page,
            content=line.content,
            polygon=get_polygon(line),
            spans=prepare_document_spans(line.spans),
        )

    def __repr__(self):
        return f"DocumentLine(content={self.content}, polygon={self.polygon}, spans={repr(self.spans)})"

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentLine.

        :return: dict
        :rtype: dict
        """
        return {
            "content": self.content,
            "polygon": [f.to_dict() for f in self.polygon]
            if self.polygon
            else [],
            "spans": [f.to_dict() for f in self.spans]
            if self.spans
            else [],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentLine":
        """Converts a dict in the shape of a DocumentLine to the model itself.

        :param dict data: A dictionary in the shape of DocumentLine.
        :return: DocumentLine
        :rtype: DocumentLine
        """
        return cls(
            content=data.get("content", None),
            polygon=[Point.from_dict(v) for v in data.get("polygon")]  # type: ignore
            if len(data.get("polygon", [])) > 0
            else [],
            spans=[DocumentSpan.from_dict(v) for v in data.get("spans")]  # type: ignore
            if len(data.get("spans", [])) > 0
            else [],
        )

    def get_words(self, **kwargs: Any) -> Iterable["DocumentWord"]:  # pylint: disable=unused-argument
        """Get the words found in the spans of this DocumentLine.

        :return: iterable[DocumentWord]
        :rtype: iterable[DocumentWord]
        """
        if not self._parent:
            raise ValueError(
                "Cannot use get_words() on a model that has been converted from a dictionary. "
                "Missing reference to parent element."
                )
        result = []
        for word in self._parent.words:
            if _in_span(word, self.spans):
                result.append(word)
        return result


class DocumentParagraph:
    """A paragraph object generally consisting of contiguous lines with common alignment and spacing.

    :ivar role: Semantic role of the paragraph. Known values are: "pageHeader", "pageFooter",
     "pageNumber", "title", "sectionHeading", "footnote".
    :vartype role: Optional[str]
    :ivar content: Concatenated content of the paragraph in reading order.
    :vartype content: str
    :ivar bounding_regions: Bounding regions covering the paragraph.
    :vartype bounding_regions: Optional[list[~azure.ai.formrecognizer.BoundingRegion]]
    :ivar spans: Location of the paragraph in the reading order concatenated content.
    :vartype spans: list[~azure.ai.formrecognizer.DocumentSpan]
    """

    def __init__(self, **kwargs):
        self.role = kwargs.get("role", None)
        self.content = kwargs.get("content", None)
        self.bounding_regions = kwargs.get("bounding_regions", None)
        self.spans = kwargs.get("spans", None)

    @classmethod
    def _from_generated(cls, paragraph):
        return cls(
            role=paragraph.role,
            content=paragraph.content,
            bounding_regions=prepare_bounding_regions(paragraph.bounding_regions),
            spans=prepare_document_spans(paragraph.spans),
        )

    def __repr__(self):
        return (
            f"DocumentParagraph(role={self.role}, content={self.content}, "
            f"bounding_regions={repr(self.bounding_regions)}, spans={repr(self.spans)})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentParagraph.

        :return: dict
        :rtype: dict
        """
        return {
            "role": self.role,
            "content": self.content,
            "bounding_regions": [f.to_dict() for f in self.bounding_regions]
            if self.bounding_regions
            else [],
            "spans": [f.to_dict() for f in self.spans]
            if self.spans
            else [],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentParagraph":
        """Converts a dict in the shape of a DocumentParagraph to the model itself.

        :param dict data: A dictionary in the shape of DocumentParagraph.
        :return: DocumentParagraph
        :rtype: DocumentParagraph
        """
        return cls(
            role=data.get("role", None),
            content=data.get("content", None),
            bounding_regions=[BoundingRegion.from_dict(v) for v in data.get("bounding_regions")]  # type: ignore
            if len(data.get("bounding_regions", [])) > 0
            else [],
            spans=[DocumentSpan.from_dict(v) for v in data.get("spans")]  # type: ignore
            if len(data.get("spans", [])) > 0
            else [],
        )


class DocumentPage:
    """Content and layout elements extracted from a page of the input.

    :ivar kind: Kind of document page. Known values are: "document", "sheet", "slide",
     "image".
    :vartype kind: str
    :ivar page_number: 1-based page number in the input document.
    :vartype page_number: int
    :ivar angle: The general orientation of the content in clockwise direction, measured
     in degrees between (-180, 180].
    :vartype angle: Optional[float]
    :ivar width: The width of the image/PDF in pixels/inches, respectively.
    :vartype width: Optional[float]
    :ivar height: The height of the image/PDF in pixels/inches, respectively.
    :vartype height: Optional[float]
    :ivar unit: The unit used by the width, height, and bounding box properties. For
     images, the unit is "pixel". For PDF, the unit is "inch". Possible values include: "pixel",
     "inch".
    :vartype unit: Optional[str]
    :ivar spans: Location of the page in the reading order concatenated content.
    :vartype spans: list[~azure.ai.formrecognizer.DocumentSpan]
    :ivar words: Extracted words from the page.
    :vartype words: Optional[list[~azure.ai.formrecognizer.DocumentWord]]
    :ivar selection_marks: Extracted selection marks from the page.
    :vartype selection_marks:
     Optional[list[~azure.ai.formrecognizer.DocumentSelectionMark]]
    :ivar lines: Extracted lines from the page, potentially containing both textual and
     visual elements.
    :vartype lines: Optional[list[~azure.ai.formrecognizer.DocumentLine]]
    """

    def __init__(self, **kwargs):
        self.kind = kwargs.get("kind", None)
        self.page_number = kwargs.get("page_number", None)
        self.angle = kwargs.get("angle", None)
        self.width = kwargs.get("width", None)
        self.height = kwargs.get("height", None)
        self.unit = kwargs.get("unit", None)
        self.spans = kwargs.get("spans", None)
        self.words = kwargs.get("words", None)
        self.selection_marks = kwargs.get("selection_marks", None)
        self.lines = kwargs.get("lines", None)

    @classmethod
    def _from_generated(cls, page):
        return cls(
            kind=page.kind,
            page_number=page.page_number,
            angle=adjust_text_angle(page.angle)
            if page.angle else None,
            width=page.width,
            height=page.height,
            unit=page.unit,
            lines=[DocumentLine._from_generated(line, page) for line in page.lines]
            if page.lines
            else [],
            words=[DocumentWord._from_generated(word) for word in page.words]
            if page.words
            else [],
            selection_marks=[
                DocumentSelectionMark._from_generated(mark)
                for mark in page.selection_marks
            ]
            if page.selection_marks
            else [],
            spans=prepare_document_spans(page.spans),
        )

    def __repr__(self):
        return (
            f"DocumentPage(kind={self.kind}, page_number={self.page_number}, angle={self.angle}, "
            f"width={self.width}, height={self.height}, unit={self.unit}, lines={repr(self.lines)}, "
            f"words={repr(self.words)}, selection_marks={repr(self.selection_marks)}, "
            f"spans={repr(self.spans)})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentPage.

        :return: dict
        :rtype: dict
        """
        return {
            "kind": self.kind,
            "page_number": self.page_number,
            "angle": self.angle,
            "width": self.width,
            "height": self.height,
            "unit": self.unit,
            "lines": [f.to_dict() for f in self.lines]
            if self.lines
            else [],
            "words": [f.to_dict() for f in self.words]
            if self.words
            else [],
            "selection_marks": [f.to_dict() for f in self.selection_marks]
            if self.selection_marks
            else [],
            "spans": [f.to_dict() for f in self.spans]
            if self.spans
            else [],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentPage":
        """Converts a dict in the shape of a DocumentPage to the model itself.

        :param dict data: A dictionary in the shape of DocumentPage.
        :return: DocumentPage
        :rtype: DocumentPage
        """
        return cls(
            kind=data.get("kind", None),
            page_number=data.get("page_number", None),
            angle=data.get("angle", None),
            width=data.get("width", None),
            height=data.get("height", None),
            unit=data.get("unit", None),
            lines=[DocumentLine.from_dict(v) for v in data.get("lines")]  # type: ignore
            if len(data.get("lines", [])) > 0
            else [],
            words=[DocumentWord.from_dict(v) for v in data.get("words")]  # type: ignore
            if len(data.get("words", [])) > 0
            else [],
            selection_marks=[DocumentSelectionMark.from_dict(v) for v in data.get("selection_marks")]  # type: ignore
            if len(data.get("selection_marks", [])) > 0
            else [],
            spans=[DocumentSpan.from_dict(v) for v in data.get("spans")]  # type: ignore
            if len(data.get("spans", [])) > 0
            else [],
        )


class DocumentSelectionMark(DocumentContentElement):
    """A selection mark object representing check boxes, radio buttons, and other elements indicating a selection.

    :ivar state: State of the selection mark. Possible values include: "selected",
     "unselected".
    :vartype state: str
    :ivar content: The text content - not returned for DocumentSelectionMark.
    :vartype content: str
    :ivar polygon: Bounding polygon of the selection mark.
    :vartype polygon: Optional[list[~azure.ai.formrecognizer.Point]]
    :ivar span: Location of the selection mark in the reading order concatenated
     content.
    :vartype span: ~azure.ai.formrecognizer.DocumentSpan
    :ivar confidence: Confidence of correctly extracting the selection mark.
    :vartype confidence: float
    :ivar str kind: For DocumentSelectionMark, this is "selectionMark".
    """

    def __init__(self, **kwargs):
        super().__init__(kind="selectionMark", **kwargs)
        self.state = kwargs.get("state", None)

    @classmethod
    def _from_generated(cls, mark):
        return cls(
            state=mark.state,
            polygon=get_polygon(mark),
            span=DocumentSpan._from_generated(mark.span)
            if mark.span
            else None,
            confidence=mark.confidence,
        )

    def __repr__(self):
        return (
            f"DocumentSelectionMark(state={self.state}, content={self.content}, span={repr(self.span)}, "
            f"confidence={self.confidence}, polygon={self.polygon}, kind={self.kind})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentSelectionMark.

        :return: dict
        :rtype: dict
        """
        return {
            "state": self.state,
            "content": self.content,
            "polygon": [f.to_dict() for f in self.polygon]
            if self.polygon
            else [],
            "span": self.span.to_dict() if self.span else None,
            "confidence": self.confidence,
            "kind": self.kind,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentSelectionMark":
        """Converts a dict in the shape of a DocumentSelectionMark to the model itself.

        :param dict data: A dictionary in the shape of DocumentSelectionMark.
        :return: DocumentSelectionMark
        :rtype: DocumentSelectionMark
        """
        return cls(
            state=data.get("state", None),
            content=data.get("content", None),
            polygon=[Point.from_dict(v) for v in data.get("polygon")]  # type: ignore
            if len(data.get("polygon", [])) > 0
            else [],
            span=DocumentSpan.from_dict(data.get("span")) if data.get("span") else None,  # type: ignore
            confidence=data.get("confidence", None),
        )


class DocumentStyle:
    """An object representing observed text styles.

    :ivar is_handwritten: Is content handwritten?.
    :vartype is_handwritten: Optional[bool]
    :ivar spans: Location of the text elements in the concatenated content the style
     applies to.
    :vartype spans: list[~azure.ai.formrecognizer.DocumentSpan]
    :ivar confidence: Confidence of correctly identifying the style.
    :vartype confidence: float
    """

    def __init__(self, **kwargs):
        self.is_handwritten = kwargs.get("is_handwritten", None)
        self.spans = kwargs.get("spans", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, style):
        return cls(
            is_handwritten=style.is_handwritten,
            spans=[DocumentSpan._from_generated(span) for span in style.spans]
            if style.spans
            else [],
            confidence=style.confidence,
        )

    def __repr__(self):
        return (
            f"DocumentStyle(is_handwritten={self.is_handwritten}, spans={repr(self.spans)}, "
            f"confidence={self.confidence})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentStyle.

        :return: dict
        :rtype: dict
        """
        return {
            "is_handwritten": self.is_handwritten,
            "spans": [f.to_dict() for f in self.spans]
            if self.spans
            else [],
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentStyle":
        """Converts a dict in the shape of a DocumentStyle to the model itself.

        :param dict data: A dictionary in the shape of DocumentStyle.
        :return: DocumentStyle
        :rtype: DocumentStyle
        """
        return cls(
            is_handwritten=data.get("is_handwritten", None),
            spans=[DocumentSpan.from_dict(v) for v in data.get("spans")]  # type: ignore
            if len(data.get("spans", [])) > 0
            else [],
            confidence=data.get("confidence", None),
        )


class DocumentTable:
    """A table object consisting table cells arranged in a rectangular layout.

    :ivar row_count: Number of rows in the table.
    :vartype row_count: int
    :ivar column_count: Number of columns in the table.
    :vartype column_count: int
    :ivar cells: Cells contained within the table.
    :vartype cells: list[~azure.ai.formrecognizer.DocumentTableCell]
    :ivar bounding_regions: Bounding regions covering the table.
    :vartype bounding_regions: Optional[list[~azure.ai.formrecognizer.BoundingRegion]]
    :ivar spans: Location of the table in the reading order concatenated content.
    :vartype spans: list[~azure.ai.formrecognizer.DocumentSpan]
    """

    def __init__(self, **kwargs):
        self.row_count = kwargs.get("row_count", None)
        self.column_count = kwargs.get("column_count", None)
        self.cells = kwargs.get("cells", None)
        self.bounding_regions = kwargs.get("bounding_regions", None)
        self.spans = kwargs.get("spans", None)

    @classmethod
    def _from_generated(cls, table):
        return cls(
            row_count=table.row_count,
            column_count=table.column_count,
            cells=[DocumentTableCell._from_generated(cell) for cell in table.cells]
            if table.cells
            else [],
            bounding_regions=prepare_bounding_regions(table.bounding_regions),
            spans=prepare_document_spans(table.spans),
        )

    def __repr__(self):
        return (
            f"DocumentTable(row_count={self.row_count}, column_count={self.column_count}, "
            f"cells={repr(self.cells)}, bounding_regions={repr(self.bounding_regions)}, "
            f"spans={repr(self.spans)})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentTable.

        :return: dict
        :rtype: dict
        """
        return {
            "row_count": self.row_count,
            "column_count": self.column_count,
            "cells": [f.to_dict() for f in self.cells]
            if self.cells
            else [],
            "bounding_regions": [f.to_dict() for f in self.bounding_regions]
            if self.bounding_regions
            else [],
            "spans": [f.to_dict() for f in self.spans]
            if self.spans
            else [],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentTable":
        """Converts a dict in the shape of a DocumentTable to the model itself.

        :param dict data: A dictionary in the shape of DocumentTable.
        :return: DocumentTable
        :rtype: DocumentTable
        """
        return cls(
            row_count=data.get("row_count", None),
            column_count=data.get("column_count", None),
            cells=[DocumentTableCell.from_dict(v) for v in data.get("cells")]  # type: ignore
            if len(data.get("cells", [])) > 0
            else [],
            bounding_regions=[BoundingRegion.from_dict(v) for v in data.get("bounding_regions")]  # type: ignore
            if len(data.get("bounding_regions", [])) > 0
            else [],
            spans=[DocumentSpan.from_dict(v) for v in data.get("spans")]  # type: ignore
            if len(data.get("spans", [])) > 0
            else [],
        )


class DocumentTableCell:
    """An object representing the location and content of a table cell.

    :ivar kind: Table cell kind. Possible values include: "content", "rowHeader", "columnHeader",
     "stubHead", "description". Default value: "content".
    :vartype kind: Optional[str]
    :ivar row_index: Row index of the cell.
    :vartype row_index: int
    :ivar column_index: Column index of the cell.
    :vartype column_index: int
    :ivar row_span: Number of rows spanned by this cell.
    :vartype row_span: Optional[int]
    :ivar column_span: Number of columns spanned by this cell.
    :vartype column_span: Optional[int]
    :ivar content: Concatenated content of the table cell in reading order.
    :vartype content: str
    :ivar bounding_regions: Bounding regions covering the table cell.
    :vartype bounding_regions: Optional[list[~azure.ai.formrecognizer.BoundingRegion]]
    :ivar spans: Location of the table cell in the reading order concatenated content.
    :vartype spans: list[~azure.ai.formrecognizer.DocumentSpan]
    """

    def __init__(self, **kwargs):
        self.kind = kwargs.get("kind", "content")
        self.row_index = kwargs.get("row_index", None)
        self.column_index = kwargs.get("column_index", None)
        self.row_span = kwargs.get("row_span", 1)
        self.column_span = kwargs.get("column_span", 1)
        self.content = kwargs.get("content", None)
        self.bounding_regions = kwargs.get("bounding_regions", None)
        self.spans = kwargs.get("spans", None)

    @classmethod
    def _from_generated(cls, cell):
        return cls(
            kind=cell.kind if cell.kind else "content",
            row_index=cell.row_index,
            column_index=cell.column_index,
            row_span=cell.row_span if cell.row_span else 1,
            column_span=cell.column_span if cell.column_span else 1,
            content=cell.content,
            bounding_regions=[
                BoundingRegion._from_generated(region)
                for region in cell.bounding_regions
            ]
            if cell.bounding_regions
            else [],
            spans=[DocumentSpan._from_generated(span) for span in cell.spans]
            if cell.spans
            else [],
        )

    def __repr__(self):
        return (
            f"DocumentTableCell(kind={self.kind}, row_index={self.row_index}, "
            f"column_index={self.column_index}, row_span={self.row_span}, "
            f"column_span={self.column_span}, content={self.content}, "
            f"bounding_regions={repr(self.bounding_regions)}, spans={repr(self.spans)})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentTableCell.

        :return: dict
        :rtype: dict
        """
        return {
            "kind": self.kind,
            "row_index": self.row_index,
            "column_index": self.column_index,
            "row_span": self.row_span,
            "column_span": self.column_span,
            "content": self.content,
            "bounding_regions": [f.to_dict() for f in self.bounding_regions]
            if self.bounding_regions
            else [],
            "spans": [f.to_dict() for f in self.spans]
            if self.spans
            else [],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentTableCell":
        """Converts a dict in the shape of a DocumentTableCell to the model itself.

        :param dict data: A dictionary in the shape of DocumentTableCell.
        :return: DocumentTableCell
        :rtype: DocumentTableCell
        """
        return cls(
            kind=data.get("kind", "content"),
            row_index=data.get("row_index", None),
            column_index=data.get("column_index", None),
            row_span=data.get("row_span", 1),
            column_span=data.get("column_span", 1),
            content=data.get("content", None),
            bounding_regions=[BoundingRegion.from_dict(v) for v in data.get("bounding_regions")]  # type: ignore
            if len(data.get("bounding_regions", [])) > 0
            else [],
            spans=[DocumentSpan.from_dict(v) for v in data.get("spans")]  # type: ignore
            if len(data.get("spans", [])) > 0
            else [],
        )


class ModelOperationInfo:
    """Model operation information, including the kind and status of the operation, when it was
    created, and more.

    Note that operation information only persists for 24 hours. If the operation was successful,
    the model can be accessed using the :func:`~get_model` or :func:`~list_models` APIs.
    To find out why an operation failed, use :func:`~get_operation` and provide the `operation_id`.

    :ivar operation_id: Operation ID.
    :vartype operation_id: str
    :ivar status: Operation status. Possible values include: "notStarted", "running",
        "failed", "succeeded", "canceled".
    :vartype status: str
    :ivar percent_completed: Operation progress (0-100).
    :vartype percent_completed: Optional[int]
    :ivar created_on: Date and time (UTC) when the operation was created.
    :vartype created_on: ~datetime.datetime
    :ivar last_updated_on: Date and time (UTC) when the operation was last updated.
    :vartype last_updated_on: ~datetime.datetime
    :ivar kind: Type of operation. Possible values include: "documentModelBuild",
        "documentModelCompose", "documentModelCopyTo".
    :vartype kind: str
    :ivar resource_location: URL of the resource targeted by this operation.
    :vartype resource_location: str
    :ivar api_version: API version used to create this operation.
    :vartype api_version: Optional[str]
    :ivar tags: List of user defined key-value tag attributes associated with the model.
    :vartype tags: Optional[dict[str, str]]

    .. versionadded:: v2022-01-30-preview
        The *api_version* and *tags* properties
    """

    def __init__(self, **kwargs):
        self.operation_id = kwargs.get("operation_id", None)
        self.status = kwargs.get("status", None)
        self.percent_completed = kwargs.get("percent_completed", 0)
        self.created_on = kwargs.get("created_on", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.kind = kwargs.get("kind", None)
        self.resource_location = kwargs.get("resource_location", None)
        self.api_version = kwargs.get("api_version", None)
        self.tags = kwargs.get("tags", None)

    def __repr__(self):
        return (
            f"ModelOperationInfo(operation_id={self.operation_id}, status={self.status}, "
            f"percent_completed={self.percent_completed}, created_on={self.created_on}, "
            f"last_updated_on={self.last_updated_on}, kind={self.kind}, "
            f"resource_location={self.resource_location}, api_version={self.api_version}, tags={self.tags})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of ModelOperationInfo.

        :return: dict
        :rtype: dict
        """
        return {
            "operation_id": self.operation_id,
            "status": self.status,
            "percent_completed": self.percent_completed,
            "created_on": self.created_on,
            "last_updated_on": self.last_updated_on,
            "kind": self.kind,
            "resource_location": self.resource_location,
            "api_version": self.api_version,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ModelOperationInfo":
        """Converts a dict in the shape of a ModelOperationInfo to the model itself.

        :param dict data: A dictionary in the shape of ModelOperationInfo.
        :return: ModelOperationInfo
        :rtype: ModelOperationInfo
        """
        return cls(
            operation_id=data.get("operation_id", None),
            status=data.get("status", None),
            percent_completed=data.get("percent_completed", None),
            created_on=data.get("created_on", None),
            last_updated_on=data.get("last_updated_on", None),
            kind=data.get("kind", None),
            resource_location=data.get("resource_location", None),
            api_version=data.get("api_version", None),
            tags=data.get("tags", {}),
        )

    @classmethod
    def _from_generated(cls, op):
        return cls(
            operation_id=op.operation_id,
            status=op.status,
            percent_completed=op.percent_completed if op.percent_completed else 0,
            created_on=op.created_date_time,
            last_updated_on=op.last_updated_date_time,
            kind=op.kind,
            resource_location=op.resource_location,
            api_version=op.api_version,
            tags=op.tags if op.tags else {},
        )


class ModelOperation(ModelOperationInfo):
    """ModelOperation consists of information about the model operation, including the result or
    error of the operation if it has completed.

    Note that operation information only persists for 24 hours. If the operation was successful,
    the model can also be accessed using the :func:`~get_model` or :func:`~list_models` APIs.

    :ivar operation_id: Operation ID.
    :vartype operation_id: str
    :ivar status: Operation status. Possible values include: "notStarted", "running",
        "failed", "succeeded", "canceled".
    :vartype status: str
    :ivar percent_completed: Operation progress (0-100).
    :vartype percent_completed: int
    :ivar created_on: Date and time (UTC) when the operation was created.
    :vartype created_on: ~datetime.datetime
    :ivar last_updated_on: Date and time (UTC) when the operation was last updated.
    :vartype last_updated_on: ~datetime.datetime
    :ivar kind: Type of operation. Possible values include: "documentModelBuild",
        "documentModelCompose", "documentModelCopyTo".
    :vartype kind: str
    :ivar resource_location: URL of the resource targeted by this operation.
    :vartype resource_location: str
    :ivar error: Encountered error, includes the error code, message, and details for why
        the operation failed.
    :vartype error: Optional[~azure.ai.formrecognizer.DocumentAnalysisError]
    :ivar result: Operation result upon success. Returns a DocumentModelDetails which contains
        all information about the model including the doc types
        and fields it can analyze from documents.
    :vartype result: Optional[~azure.ai.formrecognizer.DocumentModelDetails]
    :ivar api_version: API version used to create this operation.
    :vartype api_version: Optional[str]
    :ivar tags: List of user defined key-value tag attributes associated with the model.
    :vartype tags: Optional[dict[str, str]]

    .. versionadded:: v2022-01-30-preview
        The *api_version* and *tags* properties
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.error = kwargs.get("error", None)
        self.result = kwargs.get("result", None)

    def __repr__(self):
        return (
            f"ModelOperation(operation_id={self.operation_id}, status={self.status}, "
            f"percent_completed={self.percent_completed}, created_on={self.created_on}, "
            f"last_updated_on={self.last_updated_on}, kind={self.kind}, "
            f"resource_location={self.resource_location}, result={repr(self.result)}, "
            f"error={repr(self.error)}, api_version={self.api_version}, tags={self.tags})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of ModelOperation.

        :return: dict
        :rtype: dict
        """
        return {
            "operation_id": self.operation_id,
            "status": self.status,
            "percent_completed": self.percent_completed,
            "created_on": self.created_on,
            "last_updated_on": self.last_updated_on,
            "kind": self.kind,
            "resource_location": self.resource_location,
            "result": self.result.to_dict() if self.result else None,
            "error": self.error.to_dict() if self.error else None,
            "api_version": self.api_version,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ModelOperation":
        """Converts a dict in the shape of a ModelOperation to the model itself.

        :param dict data: A dictionary in the shape of ModelOperation.
        :return: ModelOperation
        :rtype: ModelOperation
        """
        return cls(
            operation_id=data.get("operation_id", None),
            status=data.get("status", None),
            percent_completed=data.get("percent_completed", None),
            created_on=data.get("created_on", None),
            last_updated_on=data.get("last_updated_on", None),
            kind=data.get("kind", None),
            resource_location=data.get("resource_location", None),
            result=DocumentModelDetails.from_dict(data.get("result")) if data.get("result") else None,  # type: ignore
            error=DocumentAnalysisError.from_dict(data.get("error")) if data.get("error") else None,  # type: ignore
            api_version=data.get("api_version", None),
            tags=data.get("tags", {}),
        )

    @classmethod
    def _from_generated(cls, op, api_version):  # pylint: disable=arguments-differ
        deserialize = _get_deserialize(api_version)
        return cls(
            operation_id=op.operation_id,
            status=op.status,
            percent_completed=op.percent_completed if op.percent_completed else 0,
            created_on=op.created_date_time,
            last_updated_on=op.last_updated_date_time,
            kind=op.kind,
            resource_location=op.resource_location,
            result=DocumentModelDetails._from_generated(deserialize(ModelInfo, op.result))
            if op.result else None,
            error=DocumentAnalysisError._from_generated(deserialize(Error, op.error))
            if op.error else None,
            api_version=op.api_version,
            tags=op.tags if op.tags else {},
        )


class DocumentWord(DocumentContentElement):
    """A word object consisting of a contiguous sequence of characters.  For non-space delimited languages,
    such as Chinese, Japanese, and Korean, each character is represented as its own word.

    :ivar content: Text content of the word.
    :vartype content: str
    :ivar polygon: Bounding polygon of the word.
    :vartype polygon: Optional[list[~azure.ai.formrecognizer.Point]]
    :ivar span: Location of the word in the reading order concatenated content.
    :vartype span: ~azure.ai.formrecognizer.DocumentSpan
    :ivar confidence: Confidence of correctly extracting the word.
    :vartype confidence: float
    :ivar str kind: For DocumentWord, this is "word".
    """

    def __init__(self, **kwargs):
        super().__init__(kind="word", **kwargs)

    @classmethod
    def _from_generated(cls, word):
        return cls(
            content=word.content,
            polygon=get_polygon(word),
            span=DocumentSpan._from_generated(word.span)
            if word.span
            else None,
            confidence=word.confidence,
        )

    def __repr__(self):
        return (
            f"DocumentWord(content={self.content}, polygon={self.polygon}, "
            f"span={repr(self.span)}, confidence={self.confidence}, kind={self.kind})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentWord.

        :return: dict
        :rtype: dict
        """
        return {
            "content": self.content,
            "polygon": [f.to_dict() for f in self.polygon]
            if self.polygon
            else [],
            "span": self.span.to_dict() if self.span else None,
            "confidence": self.confidence,
            "kind": self.kind,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentWord":
        """Converts a dict in the shape of a DocumentWord to the model itself.

        :param dict data: A dictionary in the shape of DocumentWord.
        :return: DocumentWord
        :rtype: DocumentWord
        """
        return cls(
            content=data.get("content", None),
            polygon=[Point.from_dict(v) for v in data.get("polygon")]  # type: ignore
            if len(data.get("polygon", [])) > 0
            else [],
            span=DocumentSpan.from_dict(data.get("span")) if data.get("span") else None,  # type: ignore
            confidence=data.get("confidence", None),
        )


class AnalyzeResult:  # pylint: disable=too-many-instance-attributes
    """Document analysis result.

    :ivar api_version: API version used to produce this result. Possible values include:
     "2022-06-30-preview".
    :vartype api_version: str
    :ivar model_id: Model ID used to produce this result.
    :vartype model_id: str
    :ivar content: Concatenate string representation of all textual and visual elements
     in reading order.
    :vartype content: str
    :ivar pages: Analyzed pages.
    :vartype pages: list[~azure.ai.formrecognizer.DocumentPage]
    :ivar languages: Detected languages in the document.
    :vartype languages: Optional[list[~azure.ai.formrecognizer.DocumentLanguage]]
    :ivar paragraphs: Extracted paragraphs.
    :vartype paragraphs: Optional[list[~azure.ai.formrecognizer.DocumentParagraph]]
    :ivar tables: Extracted tables.
    :vartype tables: Optional[list[~azure.ai.formrecognizer.DocumentTable]]
    :ivar key_value_pairs: Extracted key-value pairs.
    :vartype key_value_pairs:
     Optional[list[~azure.ai.formrecognizer.DocumentKeyValuePair]]
    :ivar styles: Extracted font styles.
    :vartype styles: Optional[list[~azure.ai.formrecognizer.DocumentStyle]]
    :ivar documents: Extracted documents.
    :vartype documents: Optional[list[~azure.ai.formrecognizer.AnalyzedDocument]]

    .. versionadded:: v2022-01-30-preview
        The *languages* property
    """

    def __init__(self, **kwargs):
        self.api_version = kwargs.get("api_version", None)
        self.model_id = kwargs.get("model_id", None)
        self.content = kwargs.get("content", None)
        self.languages = kwargs.get("languages", None)
        self.pages = kwargs.get("pages", None)
        self.paragraphs = kwargs.get("paragraphs", None)
        self.tables = kwargs.get("tables", None)
        self.key_value_pairs = kwargs.get("key_value_pairs", None)
        self.styles = kwargs.get("styles", None)
        self.documents = kwargs.get("documents", None)

    @classmethod
    def _from_generated(cls, response):
        return cls(
            api_version=response.api_version,
            model_id=response.model_id,
            content=response.content,
            languages=[DocumentLanguage._from_generated(lang) for lang in response.languages]
            if response.languages
            else [],
            pages=[DocumentPage._from_generated(page) for page in response.pages]
            if response.pages
            else [],
            paragraphs=[DocumentParagraph._from_generated(paragraph) for paragraph in response.paragraphs]
            if response.paragraphs
            else [],
            tables=[DocumentTable._from_generated(table) for table in response.tables]
            if response.tables
            else [],
            key_value_pairs=[
                DocumentKeyValuePair._from_generated(kv)
                for kv in response.key_value_pairs
            ]
            if response.key_value_pairs
            else [],
            styles=[DocumentStyle._from_generated(style) for style in response.styles]
            if response.styles
            else [],
            documents=[
                AnalyzedDocument._from_generated(document)
                for document in response.documents
            ]
            if response.documents
            else [],
        )

    def __repr__(self):
        return (
            f"AnalyzeResult(api_version={self.api_version}, model_id={self.model_id}, "
            f"content={self.content}, languages={repr(self.languages)}, "
            f"pages={repr(self.pages)}, paragraphs={repr(self.paragraphs)}, tables={repr(self.tables)}, "
            f"key_value_pairs={repr(self.key_value_pairs)}, "
            f"styles={repr(self.styles)}, documents={repr(self.documents)})"
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of AnalyzeResult.

        :return: dict
        :rtype: dict
        """
        return {
            "api_version": self.api_version,
            "model_id": self.model_id,
            "content": self.content,
            "languages": [f.to_dict() for f in self.languages]
            if self.languages
            else [],
            "pages": [f.to_dict() for f in self.pages]
            if self.pages
            else [],
            "paragraphs": [f.to_dict() for f in self.paragraphs]
            if self.paragraphs
            else [],
            "tables": [f.to_dict() for f in self.tables]
            if self.tables
            else [],
            "key_value_pairs": [f.to_dict() for f in self.key_value_pairs]
            if self.key_value_pairs
            else [],
            "styles": [f.to_dict() for f in self.styles]
            if self.styles
            else [],
            "documents": [f.to_dict() for f in self.documents]
            if self.documents
            else [],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "AnalyzeResult":
        """Converts a dict in the shape of a AnalyzeResult to the model itself.

        :param dict data: A dictionary in the shape of AnalyzeResult.
        :return: AnalyzeResult
        :rtype: AnalyzeResult
        """
        return cls(
            api_version=data.get("api_version", None),
            model_id=data.get("model_id", None),
            content=data.get("content", None),
            languages=[DocumentLanguage.from_dict(v) for v in data.get("languages")]  # type: ignore
            if len(data.get("languages", [])) > 0
            else [],
            pages=[DocumentPage.from_dict(v) for v in data.get("pages")]  # type: ignore
            if len(data.get("pages", [])) > 0
            else [],
            paragraphs=[DocumentParagraph.from_dict(v) for v in data.get("paragraphs")]  # type: ignore
            if len(data.get("paragraphs", [])) > 0
            else [],
            tables=[DocumentTable.from_dict(v) for v in data.get("tables")]  # type: ignore
            if len(data.get("tables", [])) > 0
            else [],
            key_value_pairs=[DocumentKeyValuePair.from_dict(v) for v in data.get("key_value_pairs")]  # type: ignore
            if len(data.get("key_value_pairs", [])) > 0
            else [],
            styles=[DocumentStyle.from_dict(v) for v in data.get("styles")]  # type: ignore
            if len(data.get("styles", [])) > 0
            else [],
            documents=[AnalyzedDocument.from_dict(v) for v in data.get("documents")]  # type: ignore
            if len(data.get("documents", [])) > 0
            else [],
        )


class DocumentModelSummary:
    """A summary of document model information including the model ID,
    its description, and when the model was created.

    :ivar str model_id: Unique model id.
    :ivar Optional[str] description: A description for the model.
    :ivar created_on: Date and time (UTC) when the model was created.
    :vartype created_on: ~datetime.datetime
    :ivar api_version: API version used to create this model.
    :vartype api_version: Optional[str]
    :ivar tags: List of user defined key-value tag attributes associated with the model.
    :vartype tags: Optional[dict[str, str]]

    .. versionadded:: v2022-01-30-preview
        The *api_version* and *tags* properties
    """

    def __init__(
        self,
        **kwargs
    ):
        self.model_id = kwargs.get("model_id", None)
        self.description = kwargs.get("description", None)
        self.created_on = kwargs.get("created_on", None)
        self.api_version = kwargs.get("api_version", None)
        self.tags = kwargs.get("tags", None)

    def __repr__(self):
        return (
            f"DocumentModelSummary(model_id={self.model_id}, description={self.description}, "
            f"created_on={self.created_on}, api_version={self.api_version}, tags={self.tags})"
        )

    @classmethod
    def _from_generated(cls, model):
        return cls(
            model_id=model.model_id,
            description=model.description,
            created_on=model.created_date_time,
            api_version=model.api_version,
            tags=model.tags,
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentModelSummary.

        :return: dict
        :rtype: dict
        """
        return {
            "model_id": self.model_id,
            "description": self.description,
            "created_on": self.created_on,
            "api_version": self.api_version,
            "tags": self.tags if self.tags else {},
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentModelSummary":
        """Converts a dict in the shape of a DocumentModelSummary to the model itself.

        :param dict data: A dictionary in the shape of DocumentModelSummary.
        :return: DocumentModelSummary
        :rtype: DocumentModelSummary
        """
        return cls(
            model_id=data.get("model_id", None),
            description=data.get("description", None),
            created_on=data.get("created_on", None),
            api_version=data.get("api_version", None),
            tags=data.get("tags", {})
        )


class DocumentModelDetails(DocumentModelSummary):
    """Document model information. Includes the doc types that the model can analyze.

    :ivar str model_id: Unique model id.
    :ivar Optional[str] description: A description for the model.
    :ivar created_on: Date and time (UTC) when the model was created.
    :vartype created_on: ~datetime.datetime
    :ivar api_version: API version used to create this model.
    :vartype api_version: Optional[str]
    :ivar tags: List of user defined key-value tag attributes associated with the model.
    :vartype tags: Optional[dict[str, str]]
    :ivar doc_types: Supported document types, including the fields for each document and their types.
    :vartype doc_types: Optional[dict[str, ~azure.ai.formrecognizer.DocTypeInfo]]

    .. versionadded:: v2022-01-30-preview
        The *api_version* and *tags* properties
    """

    def __init__(
        self,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.doc_types = kwargs.get("doc_types", None)

    def __repr__(self):
        return (
            f"DocumentModelDetails(model_id={self.model_id}, description={self.description}, "
            f"created_on={self.created_on}, api_version={self.api_version}, tags={self.tags}, "
            f"doc_types={repr(self.doc_types)})"
        )

    @classmethod
    def _from_generated(cls, model):
        return cls(
            model_id=model.model_id,
            description=model.description,
            created_on=model.created_date_time,
            api_version=model.api_version,
            tags=model.tags,
            doc_types={k: DocTypeInfo._from_generated(v) for k, v in model.doc_types.items()}
            if model.doc_types else {}
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentModelDetails.

        :return: dict
        :rtype: dict
        """
        return {
            "model_id": self.model_id,
            "description": self.description,
            "created_on": self.created_on,
            "api_version": self.api_version,
            "tags": self.tags if self.tags else {},
            "doc_types": {k: v.to_dict() for k, v in self.doc_types.items()} if self.doc_types else {}
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentModelDetails":
        """Converts a dict in the shape of a DocumentModelDetails to the model itself.

        :param dict data: A dictionary in the shape of DocumentModelDetails.
        :return: DocumentModelDetails
        :rtype: DocumentModelDetails
        """
        return cls(
            model_id=data.get("model_id", None),
            description=data.get("description", None),
            created_on=data.get("created_on", None),
            api_version=data.get("api_version", None),
            tags=data.get("tags", {}),
            doc_types={k: DocTypeInfo.from_dict(v) for k, v in data.get("doc_types").items()}  # type: ignore
            if data.get("doc_types")
            else {},
        )


class DocTypeInfo:
    """DocTypeInfo represents a document type that a model can recognize, including its
    fields and types, and the confidence for those fields.

    :ivar Optional[str] description: A description for the model.
    :ivar build_mode: The build mode used when building the custom model.
     Possible values include: "template", "neural".
    :vartype build_mode: Optional[str]
    :ivar field_schema: Description of the document semantic schema.
    :vartype field_schema: dict[str, Any]
    :ivar field_confidence: Estimated confidence for each field.
    :vartype field_confidence: Optional[dict[str, float]]

    .. versionadded:: v2022-01-30-preview
        The *build_mode* property
    """

    def __init__(
        self,
        **kwargs
    ):
        self.description = kwargs.get("description", None)
        self.build_mode = kwargs.get("build_mode", None)
        self.field_schema = kwargs.get("field_schema", None)
        self.field_confidence = kwargs.get("field_confidence", None)

    def __repr__(self):
        return (
            f"DocTypeInfo(description={self.description}, build_mode={self.build_mode}, "
            f"field_schema={self.field_schema}, field_confidence={self.field_confidence})"
        )

    @classmethod
    def _from_generated(cls, doc_type):
        return cls(
            description=doc_type.description,
            build_mode=doc_type.build_mode,
            field_schema={name: field.serialize() for name, field in doc_type.field_schema.items()}
            if doc_type.field_schema else {},
            field_confidence=doc_type.field_confidence,
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocTypeInfo.

        :return: dict
        :rtype: dict
        """
        return {
            "description": self.description,
            "build_mode": self.build_mode,
            "field_schema": self.field_schema,
            "field_confidence": self.field_confidence,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocTypeInfo":
        """Converts a dict in the shape of a DocTypeInfo to the model itself.

        :param dict data: A dictionary in the shape of DocTypeInfo.
        :return: DocTypeInfo
        :rtype: DocTypeInfo
        """
        return cls(
            description=data.get("description", None),
            build_mode=data.get("build_mode", None),
            field_schema=data.get("field_schema", {}),
            field_confidence=data.get("field_confidence", {}),
        )


class ResourceInfo:
    """Info regarding models under the Form Recognizer resource.

    :ivar int document_model_count: Number of custom models in the current resource.
    :ivar int document_model_limit: Maximum number of custom models supported in the current resource.
    """

    def __init__(
        self,
        **kwargs
    ):
        self.document_model_count = kwargs.get("document_model_count", None)
        self.document_model_limit = kwargs.get("document_model_limit", None)

    def __repr__(self):
        return (
            f"ResourceInfo(document_model_count={self.document_model_count}, "
            f"document_model_limit={self.document_model_limit})"
        )

    @classmethod
    def _from_generated(cls, info):
        return cls(
            document_model_count=info.count,
            document_model_limit=info.limit,
        )


    def to_dict(self) -> dict:
        """Returns a dict representation of ResourceInfo.

        :return: dict
        :rtype: dict
        """
        return {
            "document_model_count": self.document_model_count,
            "document_model_limit": self.document_model_limit,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "ResourceInfo":
        """Converts a dict in the shape of a ResourceInfo to the model itself.

        :param dict data: A dictionary in the shape of ResourceInfo.
        :return: ResourceInfo
        :rtype: ResourceInfo
        """
        return cls(
            document_model_count=data.get("document_model_count", None),
            document_model_limit=data.get("document_model_limit", None),
        )


class DocumentAnalysisError:
    """DocumentAnalysisError contains the details of the error returned by the service.

    :ivar code: Error code.
    :vartype code: str
    :ivar message: Error message.
    :vartype message: str
    :ivar target: Target of the error.
    :vartype target: Optional[str]
    :ivar details: List of detailed errors.
    :vartype details: Optional[list[~azure.ai.formrecognizer.DocumentAnalysisError]]
    :ivar innererror: Detailed error.
    :vartype innererror: Optional[~azure.ai.formrecognizer.DocumentAnalysisInnerError]
    """

    def __init__(
        self,
        **kwargs
    ):
        self.code = kwargs.get("code", None)
        self.message = kwargs.get("message", None)
        self.target = kwargs.get("target", None)
        self.details = kwargs.get("details", None)
        self.innererror = kwargs.get("innererror", None)

    def __repr__(self):
        return (
            f"DocumentAnalysisError(code={self.code}, message={self.message}, target={self.target}, "
            f"details={repr(self.details)}, innererror={repr(self.innererror)})"
        )

    @classmethod
    def _from_generated(cls, err):
        return cls(
            code=err.code,
            message=err.message,
            target=err.target,
            details=[DocumentAnalysisError._from_generated(e) for e in err.details] if err.details else [],
            innererror=DocumentAnalysisInnerError._from_generated(err.innererror) if err.innererror else None
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentAnalysisError.

        :return: dict
        :rtype: dict
        """
        return {
            "code": self.code,
            "message": self.message,
            "target": self.target,
            "details": [detail.to_dict() for detail in self.details] if self.details else [],
            "innererror": self.innererror.to_dict() if self.innererror else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentAnalysisError":
        """Converts a dict in the shape of a DocumentAnalysisError to the model itself.

        :param dict data: A dictionary in the shape of DocumentAnalysisError.
        :return: DocumentAnalysisError
        :rtype: DocumentAnalysisError
        """
        return cls(
            code=data.get("code", None),
            message=data.get("message", None),
            target=data.get("target", None),
            details=[DocumentAnalysisError.from_dict(e) for e in data.get("details")]  # type: ignore
            if data.get("details") else [],
            innererror=DocumentAnalysisInnerError.from_dict(data.get("innererror"))  # type: ignore
            if data.get("innererror") else None
        )


class DocumentAnalysisInnerError:
    """Inner error details for the DocumentAnalysisError.

    :ivar code: Error code.
    :vartype code: str
    :ivar Optional[str] message: Error message.
    :ivar innererror: Detailed error.
    :vartype innererror: Optional[~azure.ai.formrecognizer.DocumentAnalysisInnerError]
    """

    def __init__(
        self,
        **kwargs
    ):

        self.code = kwargs.get("code", None)
        self.message = kwargs.get("message", None)
        self.innererror = kwargs.get("innererror", None)

    def __repr__(self):
        return (
            f"DocumentAnalysisInnerError(code={self.code}, message={self.message}, "
            f"innererror={repr(self.innererror)})"
        )

    @classmethod
    def _from_generated(cls, ierr):
        return cls(
            code=ierr.code,
            message=ierr.message,
            innererror=DocumentAnalysisInnerError._from_generated(ierr.innererror) if ierr.innererror else None
        )

    def to_dict(self) -> dict:
        """Returns a dict representation of DocumentAnalysisInnerError.

        :return: dict
        :rtype: dict
        """
        return {
            "code": self.code,
            "message": self.message,
            "innererror": self.innererror.to_dict() if self.innererror else None
        }

    @classmethod
    def from_dict(cls, data: dict) -> "DocumentAnalysisInnerError":
        """Converts a dict in the shape of a DocumentAnalysisInnerError to the model itself.

        :param dict data: A dictionary in the shape of DocumentAnalysisInnerError.
        :return: DocumentAnalysisInnerError
        :rtype: DocumentAnalysisInnerError
        """
        return cls(
            code=data.get("code", None),
            message=data.get("message", None),
            innererror=DocumentAnalysisInnerError.from_dict(data.get("innererror"))  # type: ignore
            if data.get("innererror") else None
        )


def _in_span(element: DocumentWord, spans: List[DocumentSpan]) -> bool:
    for span in spans:
        if element.span.offset >= span.offset and (
            element.span.offset + element.span.length
        ) <= (span.offset + span.length):
            return True
    return False
