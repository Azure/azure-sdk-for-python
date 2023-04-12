# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

# pylint: disable=protected-access, too-many-lines

import datetime
from typing import Dict, Iterable, List, NewType, Any, Union, Sequence, Optional
from enum import Enum
from collections import namedtuple
from azure.core import CaseInsensitiveEnumMeta
from ._generated.v2023_02_28_preview.models import (
    DocumentModelDetails as ModelDetails,
    DocumentClassifierDetails as ClassifierDetails,
    Error
)
from ._generated.models import ClassifierDocumentTypeDetails
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
        else []
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
        return (
            CurrencyValue._from_generated(value.value_currency)
            if value.value_currency
            else None
        )
    if value.type == "address":
        return (
            AddressValue._from_generated(value.value_address)
            if value.value_address
            else None
        )
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
    if value.type == "boolean":
        return value.value_boolean
    return None


class AnalysisFeature(str, Enum, metaclass=CaseInsensitiveEnumMeta):
    """Document analysis features to enable."""

    #: Perform OCR at a higher resolution to handle documents with fine print.
    OCR_HIGH_RESOLUTION = "ocr.highResolution"
    #: Enable the detection of mathematical expressions the document.
    OCR_FORMULA = "ocr.formula"
    #: Enable the recognition of various font styles.
    OCR_FONT = "ocr.font"
    #: Enable extraction of additional fields via the queryFields query parameter.
    QUERY_FIELDS_PREMIUM = "queryFields.premium"


class ModelBuildMode(str, Enum, metaclass=CaseInsensitiveEnumMeta):
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
    """The x, y coordinate of a point on a bounding box or polygon.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """
    x: float
    """x-coordinate"""
    y: float
    """y-coordinate"""


    __slots__ = ()

    def __new__(cls, x: float, y: float) -> "Point":
        return super().__new__(cls, x, y)

    def to_dict(self) -> Dict:
        """Returns a dict representation of Point."""
        return {"x": self.x, "y": self.y}

    @classmethod
    def from_dict(cls, data: Dict) -> "Point":
        """Converts a dict in the shape of a Point to the model itself.

        :param Dict data: A dictionary in the shape of Point.
        :return: Point
        :rtype: Point
        """
        return cls(x=data.get("x", None), y=data.get("y", None))


class TextAppearance:
    """An object representing the appearance of the text line.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """
    style_name: str
    """The text line style name.
        Possible values include: "other", "handwriting"."""
    style_confidence: float
    """The confidence of text line style."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return f"TextAppearance(style_name={self.style_name}, style_confidence={self.style_confidence})"

    def to_dict(self) -> Dict:
        """Returns a dict representation of TextAppearance."""
        return {
            "style_name": self.style_name,
            "style_confidence": self.style_confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "TextAppearance":
        """Converts a dict in the shape of a TextAppearance to the model itself.

        :param Dict data: A dictionary in the shape of TextAppearance.
        :return: TextAppearance
        :rtype: TextAppearance
        """
        return cls(
            style_name=data.get("style_name", None),
            style_confidence=data.get("style_confidence", None),
        )


class FormPageRange(namedtuple("FormPageRange", "first_page_number last_page_number")):
    """The 1-based page range of the form.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """
    first_page_number: int
    """The first page number of the form."""
    last_page_number: int
    """The last page number of the form."""

    __slots__ = ()

    def __new__(cls, first_page_number: int, last_page_number: int) -> "FormPageRange":
        return super().__new__(
            cls, first_page_number, last_page_number
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of FormPageRange."""
        return {
            "first_page_number": self.first_page_number,
            "last_page_number": self.last_page_number,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "FormPageRange":
        """Converts a dict in the shape of a FormPageRange to the model itself.

        :param Dict data: A dictionary in the shape of FormPageRange.
        :return: FormPageRange
        :rtype: FormPageRange
        """
        return cls(
            first_page_number=data.get("first_page_number", None),
            last_page_number=data.get("last_page_number", None),
        )


class FormElement:
    """Base type which includes properties for a form element.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """
    text: str
    """The text content of the element."""
    bounding_box: List[Point]
    """A list of 4 points representing the quadrilateral bounding box
        that outlines the text. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF."""
    page_number: int
    """The 1-based number of the page in which this content is present."""
    kind: str
    """The kind of form element. Possible kinds are "word", "line", or "selectionMark" which
        correspond to a :class:`~azure.ai.formrecognizer.FormWord` :class:`~azure.ai.formrecognizer.FormLine`,
        or :class:`~azure.ai.formrecognizer.FormSelectionMark`, respectively."""


    def __init__(self, **kwargs: Any) -> None:
        self.bounding_box = kwargs.get("bounding_box", None)
        self.page_number = kwargs.get("page_number", None)
        self.text = kwargs.get("text", None)
        self.kind = kwargs.get("kind", None)

    def to_dict(self) -> Dict:
        """Returns a dict representation of FormElement."""
        return {
            "text": self.text,
            "bounding_box": [f.to_dict() for f in self.bounding_box]
            if self.bounding_box
            else [],
            "page_number": self.page_number,
            "kind": self.kind,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "FormElement":
        """Converts a dict in the shape of a FormElement to the model itself.

        :param Dict data: A dictionary in the shape of FormElement.
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


class FormWord(FormElement):
    """Represents a word recognized from the input document.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """
    text: str
    """The text content of the word."""
    bounding_box: List[Point]
    """A list of 4 points representing the quadrilateral bounding box
        that outlines the text. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF."""
    confidence: float
    """Measures the degree of certainty of the recognition result. Value is between [0.0, 1.0]."""
    page_number: int
    """The 1-based number of the page in which this content is present."""
    kind: str
    """For FormWord, this is "word"."""


    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"FormWord(text={self.text}, bounding_box={self.bounding_box}, confidence={self.confidence}, "
            f"page_number={self.page_number}, kind={self.kind})"
        )[:1024]

    def to_dict(self) -> Dict:
        """Returns a dict representation of FormWord."""
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
    def from_dict(cls, data: Dict) -> "FormWord":
        """Converts a dict in the shape of a FormWord to the model itself.

        :param Dict data: A dictionary in the shape of FormWord.
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

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """
    text: str
    """The text content - not returned for FormSelectionMark."""
    bounding_box: List[Point]
    """A list of 4 points representing the quadrilateral bounding box
        that outlines the text. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF."""
    confidence: float
    """Measures the degree of certainty of the recognition result. Value is between [0.0, 1.0]."""
    state: str
    """State of the selection mark. Possible values include: "selected",
     "unselected"."""
    page_number: int
    """The 1-based number of the page in which this content is present."""
    kind: str
    """For FormSelectionMark, this is "selectionMark"."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"FormSelectionMark(text={self.text}, bounding_box={self.bounding_box}, confidence={self.confidence}, "
            f"page_number={self.page_number}, state={self.state}, kind={self.kind})"
        )[:1024]

    def to_dict(self) -> Dict:
        """Returns a dict representation of FormSelectionMark."""
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
    def from_dict(cls, data: Dict) -> "FormSelectionMark":
        """Converts a dict in the shape of a FormSelectionMark to the model itself.

        :param Dict data: A dictionary in the shape of FormSelectionMark.
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


class FormLine(FormElement):
    """An object representing an extracted line of text.

    .. versionadded:: v2.1
        *appearance* property, support for *to_dict* and *from_dict* methods
    """
    text: str
    """The text content of the line."""
    bounding_box: List[Point]
    """A list of 4 points representing the quadrilateral bounding box
        that outlines the text. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF."""
    words: List[FormWord]
    """A list of the words that make up the line."""
    page_number: int
    """The 1-based number of the page in which this content is present."""
    kind: str
    """For FormLine, this is "line"."""
    appearance: TextAppearance
    """An object representing the appearance of the line."""


    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"FormLine(text={self.text}, bounding_box={self.bounding_box}, words={repr(self.words)}, "
            f"page_number={self.page_number}, kind={self.kind}, appearance={self.appearance})"
        )[:1024]

    def to_dict(self) -> Dict:
        """Returns a dict representation of FormLine."""
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
    def from_dict(cls, data: Dict) -> "FormLine":
        """Converts a dict in the shape of a FormLine to the model itself.

        :param Dict data: A dictionary in the shape of FormLine.
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


class FormTableCell:  # pylint:disable=too-many-instance-attributes
    """Represents a cell contained in a table recognized from the input document.

    .. versionadded:: v2.1
        *FormSelectionMark* is added to the types returned in the list of field_elements, support for
        *to_dict* and *from_dict* methods
    """
    text: str
    """Text content of the cell."""
    row_index: int
    """Row index of the cell."""
    column_index: int
    """Column index of the cell."""
    row_span: int
    """Number of rows spanned by this cell."""
    column_span: int
    """Number of columns spanned by this cell."""
    bounding_box: List[Point]
    """A list of 4 points representing the quadrilateral bounding box
        that outlines the text. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF."""
    confidence: float
    """Measures the degree of certainty of the recognition result. Value is between [0.0, 1.0]."""
    is_header: bool
    """Whether the current cell is a header cell."""
    is_footer: bool
    """Whether the current cell is a footer cell."""
    page_number: int
    """The 1-based number of the page in which this content is present."""
    field_elements: List[Union[FormElement, FormWord, FormLine, FormSelectionMark]]
    """When `include_field_elements` is set to true, a list of
        elements constituting this cell is returned. The list
        constitutes of elements such as lines, words, and selection marks.
        For calls to begin_recognize_content(), this list is always populated."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"FormTableCell(text={self.text}, row_index={self.row_index}, column_index={self.column_index}, "
            f"row_span={self.row_span}, column_span={self.column_span}, bounding_box={self.bounding_box}, "
            f"confidence={self.confidence}, is_header={self.is_header}, is_footer={self.is_footer}, "
            f"page_number={self.page_number}, field_elements={repr(self.field_elements)})"
        )[:1024]

    def to_dict(self) -> Dict:
        """Returns a dict representation of FormTableCell."""
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
    def from_dict(cls, data: Dict) -> "FormTableCell":
        """Converts a dict in the shape of a FormTableCell to the model itself.

        :param Dict data: A dictionary in the shape of FormTableCell.
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


class FormTable:
    """Information about the extracted table contained on a page.

    .. versionadded:: v2.1
        The *bounding_box* property, support for *to_dict* and *from_dict* methods
    """
    page_number: int
    """The 1-based number of the page in which this table is present."""
    cells: List[FormTableCell]
    """List of cells contained in the table."""
    row_count: int
    """Number of rows in table."""
    column_count: int
    """Number of columns in table."""
    bounding_box: List[Point]
    """A list of 4 points representing the quadrilateral bounding box
        that outlines the table. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF."""

    def __init__(self, **kwargs: Any) -> None:
        self.page_number = kwargs.get("page_number", None)
        self.cells = kwargs.get("cells", None)
        self.row_count = kwargs.get("row_count", None)
        self.column_count = kwargs.get("column_count", None)
        self.bounding_box = kwargs.get("bounding_box", None)

    def __repr__(self) -> str:
        return (
            f"FormTable(page_number={self.page_number}, cells={repr(self.cells)}, row_count={self.row_count}, "
            f"column_count={self.column_count}, bounding_box={self.bounding_box})"
        )[:1024]

    def to_dict(self) -> Dict:
        """Returns a dict representation of FormTable."""
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
    def from_dict(cls, data: Dict) -> "FormTable":
        """Converts a dict in the shape of a FormTable to the model itself.

        :param Dict data: A dictionary in the shape of FormTable.
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


class FormPage:
    """Represents a page recognized from the input document. Contains lines,
    words, selection marks, tables and page metadata.

    .. versionadded:: v2.1
        *selection_marks* property, support for *to_dict* and *from_dict* methods
    """
    page_number: int
    """The 1-based number of the page in which this content is present."""
    text_angle: float
    """The general orientation of the text in clockwise direction, measured in
        degrees between (-180, 180]."""
    width: float
    """The width of the image/PDF in pixels/inches, respectively."""
    height: float
    """The height of the image/PDF in pixels/inches, respectively."""
    unit: str
    """The :class:`~azure.ai.formrecognizer.LengthUnit` used by the width,
        height, and bounding box properties. For images, the unit is "pixel".
        For PDF, the unit is "inch"."""
    tables: List[FormTable]
    """A list of extracted tables contained in a page."""
    lines: List[FormLine]
    """When `include_field_elements` is set to true, a list of recognized text lines is returned.
        For calls to recognize content, this list is always populated. The maximum number of lines
        returned is 300 per page. The lines are sorted top to bottom, left to right, although in
        certain cases proximity is treated with higher priority. As the sorting order depends on
        the detected text, it may change across images and OCR version updates. Thus, business
        logic should be built upon the actual line location instead of order. The reading order
        of lines can be specified by the `reading_order` keyword argument (Note: `reading_order`
        only supported in `begin_recognize_content` and `begin_recognize_content_from_url`)."""
    selection_marks: List[FormSelectionMark]
    """List of selection marks extracted from the page."""


    def __init__(self, **kwargs: Any) -> None:
        self.page_number = kwargs.get("page_number", None)
        self.text_angle = kwargs.get("text_angle", None)
        self.width = kwargs.get("width", None)
        self.height = kwargs.get("height", None)
        self.unit = kwargs.get("unit", None)
        self.tables = kwargs.get("tables", None)
        self.lines = kwargs.get("lines", None)
        self.selection_marks = kwargs.get("selection_marks", None)

    def __repr__(self) -> str:
        return (
            f"FormPage(page_number={self.page_number}, text_angle={self.text_angle}, "
            f"width={self.width}, height={self.height}, unit={self.unit}, tables={repr(self.tables)}, "
            f"lines={repr(self.lines)}, selection_marks={repr(self.selection_marks)})"
        )[:1024]

    def to_dict(self) -> Dict:
        """Returns a dict representation of FormPage."""
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
    def from_dict(cls, data: Dict) -> "FormPage":
        """Converts a dict in the shape of a FormPage to the model itself.

        :param Dict data: A dictionary in the shape of FormPage.
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


class FieldData:
    """Contains the data for the form field. This includes the text,
    location of the text on the form, and a collection of the
    elements that make up the text.

    .. versionadded:: v2.1
        *FormSelectionMark* is added to the types returned in the list of field_elements, support for
        *to_dict* and *from_dict* methods
    """
    page_number: int
    """The 1-based number of the page in which this content is present."""
    text: str
    """The string representation of the field or value."""
    bounding_box: List[Point]
    """A list of 4 points representing the quadrilateral bounding box
        that outlines the text. The points are listed in clockwise
        order: top-left, top-right, bottom-right, bottom-left.
        Units are in pixels for images and inches for PDF."""
    field_elements: List[Union[FormElement, FormWord,
        FormLine, FormSelectionMark]]
    """When `include_field_elements` is set to true, a list of
        elements constituting this field or value is returned. The list
        constitutes of elements such as lines, words, and selection marks."""


    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"FieldData(page_number={self.page_number}, text={self.text}, bounding_box={self.bounding_box}, "
            f"field_elements={repr(self.field_elements)})"
        )[:1024]

    def to_dict(self) -> Dict:
        """Returns a dict representation of FieldData."""
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
    def from_dict(cls, data: Dict) -> "FieldData":
        """Converts a dict in the shape of a FieldData to the model itself.

        :param Dict data: A dictionary in the shape of FieldData.
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


class FormField:
    """Represents a field recognized in an input form.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """
    value_type:  str
    """The type of `value` found on FormField. Described in
        :class:`~azure.ai.formrecognizer.FieldValueType`, possible types include: 'string',
        'date', 'time', 'phoneNumber', 'float', 'integer', 'dictionary', 'list', 'selectionMark',
        or 'countryRegion'."""
    label_data: FieldData
    """Contains the text, bounding box, and field elements for the field label.
        Note that this is not returned for forms analyzed by models trained with labels."""
    value_data: FieldData
    """Contains the text, bounding box, and field elements for the field value."""
    name: str
    """The unique name of the field or the training-time label if
        analyzed from a custom model that was trained with labels."""
    value: Union[str, int, float, datetime.date, datetime.time,
        Dict[str, "FormField"], List["FormField"]]
    """The value for the recognized field. Its semantic data type is described by `value_type`.
        If the value is extracted from the form, but cannot be normalized to its type,
        then access the `value_data.text` property for a textual representation of the value."""
    confidence: float
    """Measures the degree of certainty of the recognition result. Value is between [0.0, 1.0]."""


    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
                f"FormField(value_type={self.value_type}, label_data={repr(self.label_data)}, "
                f"value_data={repr(self.value_data)}, name={self.name}, value={repr(self.value)}, "
                f"confidence={self.confidence})"
            )[:1024]

    def to_dict(self) -> Dict:
        """Returns a dict representation of FormField."""
        value = self.value
        if isinstance(self.value, dict):
            value = {k: v.to_dict() for k, v in self.value.items()}  # type: ignore
        elif isinstance(self.value, list):
            value = [v.to_dict() for v in self.value]  # type: ignore
        return {
            "value_type": self.value_type,
            "name": self.name,
            "value": value,
            "confidence": self.confidence,
            "label_data": self.label_data.to_dict() if self.label_data else None,
            "value_data": self.value_data.to_dict() if self.value_data else None,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "FormField":
        """Converts a dict in the shape of a FormField to the model itself.

        :param Dict data: A dictionary in the shape of FormField.
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


class RecognizedForm:
    """Represents a form that has been recognized by a trained or prebuilt model.
    The `fields` property contains the form fields that were extracted from the
    form. Tables, text lines/words, and selection marks are extracted per page
    and found in the `pages` property.

    .. versionadded:: v2.1
        The *form_type_confidence* and *model_id* properties, support for
        *to_dict* and *from_dict* methods
    """
    form_type: str
    """The type of form the model identified the submitted form to be."""
    form_type_confidence: int
    """Confidence of the type of form the model identified the submitted form to be."""
    model_id: str
    """Model identifier of model used to analyze form if not using a prebuilt
        model."""
    fields: Dict[str, FormField]
    """A dictionary of the fields found on the form. The fields dictionary
        keys are the `name` of the field. For models trained with labels,
        this is the training-time label of the field. For models trained
        without labels, a unique name is generated for each field."""
    page_range: FormPageRange
    """The first and last page number of the input form."""
    pages: List[FormPage]
    """A list of pages recognized from the input document. Contains lines,
        words, selection marks, tables and page metadata."""


    def __init__(self, **kwargs: Any) -> None:
        self.fields = kwargs.get("fields", None)
        self.form_type = kwargs.get("form_type", None)
        self.page_range = kwargs.get("page_range", None)
        self.pages = kwargs.get("pages", None)
        self.model_id = kwargs.get("model_id", None)
        self.form_type_confidence = kwargs.get("form_type_confidence", None)

    def __repr__(self) -> str:
        return (
            f"RecognizedForm(form_type={self.form_type}, fields={repr(self.fields)}, "
            f"page_range={repr(self.page_range)}, pages={repr(self.pages)}, "
            f"form_type_confidence={self.form_type_confidence}, model_id={self.model_id})"
            )[:1024]

    def to_dict(self) -> Dict:
        """Returns a dict representation of RecognizedForm."""
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
    def from_dict(cls, data: Dict) -> "RecognizedForm":
        """Converts a dict in the shape of a RecognizedForm to the model itself.

        :param Dict data: A dictionary in the shape of RecognizedForm.
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


class FormRecognizerError:
    """Represents an error that occurred while training.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """
    code: str
    """Error code."""
    message: str
    """Error message."""

    def __init__(self, **kwargs: Any) -> None:
        self.code = kwargs.get("code", None)
        self.message = kwargs.get("message", None)

    @classmethod
    def _from_generated(cls, err):
        return (
            [cls(code=error.code, message=error.message) for error in err]
            if err
            else []
        )

    def __repr__(self) -> str:
        return f"FormRecognizerError(code={self.code}, message={self.message})"[:1024]

    def to_dict(self) -> Dict:
        """Returns a dict representation of FormRecognizerError."""
        return {"code": self.code, "message": self.message}

    @classmethod
    def from_dict(cls, data: Dict) -> "FormRecognizerError":
        """Converts a dict in the shape of a FormRecognizerError to the model itself.

        :param Dict data: A dictionary in the shape of FormRecognizerError.
        :return: FormRecognizerError
        :rtype: FormRecognizerError
        """
        return cls(
            code=data.get("code", None),
            message=data.get("message", None),
        )


class CustomFormModelField:
    """A field that the model will extract from forms it analyzes.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """
    label: str
    """The form fields label on the form."""
    name: str
    """Canonical name; uniquely identifies a field within the form."""
    accuracy: float
    """The estimated recognition accuracy for this field."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return f"CustomFormModelField(label={self.label}, name={self.name}, accuracy={self.accuracy})"[:1024]

    def to_dict(self) -> Dict:
        """Returns a dict representation of CustomFormModelField."""
        return {"label": self.label, "accuracy": self.accuracy, "name": self.name}

    @classmethod
    def from_dict(cls, data: Dict) -> "CustomFormModelField":
        """Converts a dict in the shape of a CustomFormModelField to the model itself.

        :param Dict data: A dictionary in the shape of CustomFormModelField.
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

    .. versionadded:: v2.1
        The *model_id* property, support for *to_dict* and *from_dict* methods
    """
    name: str
    """The name of the document."""
    status: str
    """The :class:`~azure.ai.formrecognizer.TrainingStatus`
        of the training operation. Possible values include:
        'succeeded', 'partiallySucceeded', 'failed'."""
    page_count: int
    """Total number of pages trained."""
    errors: List[FormRecognizerError]
    """List of any errors for document."""
    model_id: str
    """The model ID that used the document to train."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"TrainingDocumentInfo(name={self.name}, status={self.status}, page_count={self.page_count}, "
            f"errors={repr(self.errors)}, model_id={self.model_id})"[:1024]
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of TrainingDocumentInfo."""
        return {
            "name": self.name,
            "status": self.status,
            "page_count": self.page_count,
            "errors": [err.to_dict() for err in self.errors] if self.errors else [],
            "model_id": self.model_id,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "TrainingDocumentInfo":
        """Converts a dict in the shape of a TrainingDocumentInfo to the model itself.

        :param Dict data: A dictionary in the shape of TrainingDocumentInfo.
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


class AccountProperties:
    """Summary of all the custom models on the account.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """
    custom_model_count: int
    """Current count of trained custom models."""
    custom_model_limit: int
    """Max number of models that can be trained for this account."""

    def __init__(self, **kwargs: Any) -> None:
        self.custom_model_count = kwargs.get("custom_model_count", None)
        self.custom_model_limit = kwargs.get("custom_model_limit", None)

    @classmethod
    def _from_generated(cls, model):
        return cls(
            custom_model_count=model.count,
            custom_model_limit=model.limit,
        )

    def __repr__(self) -> str:
        return (
            f"AccountProperties(custom_model_count={self.custom_model_count}, "
            f"custom_model_limit={self.custom_model_limit})"
        )[:1024]

    def to_dict(self) -> Dict:
        """Returns a dict representation of AccountProperties."""
        return {
            "custom_model_count": self.custom_model_count,
            "custom_model_limit": self.custom_model_limit,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "AccountProperties":
        """Converts a dict in the shape of a AccountProperties to the model itself.

        :param Dict data: A dictionary in the shape of AccountProperties.
        :return: AccountProperties
        :rtype: AccountProperties
        """
        return cls(
            custom_model_count=data.get("custom_model_count", None),
            custom_model_limit=data.get("custom_model_limit", None),
        )


class CustomFormModelProperties:
    """Optional model properties.

    .. versionadded:: v2.1
        Support for *to_dict* and *from_dict* methods
    """
    is_composed_model: bool
    """Is this model composed? (default: false)."""

    def __init__(self, **kwargs: Any) -> None:
        self.is_composed_model = kwargs.get("is_composed_model", False)

    @classmethod
    def _from_generated(cls, model_info):
        if model_info.attributes:
            return cls(is_composed_model=model_info.attributes.is_composed)
        return cls(is_composed_model=False)

    def __repr__(self) -> str:
        return f"CustomFormModelProperties(is_composed_model={self.is_composed_model})"

    def to_dict(self) -> Dict:
        """Returns a dict representation of CustomFormModelProperties."""
        return {"is_composed_model": self.is_composed_model}

    @classmethod
    def from_dict(cls, data: Dict) -> "CustomFormModelProperties":
        """Converts a dict in the shape of a CustomFormModelProperties to the model itself.

        :param Dict data: A dictionary in the shape of CustomFormModelProperties.
        :return: CustomFormModelProperties
        :rtype: CustomFormModelProperties
        """
        return cls(
            is_composed_model=data.get("is_composed_model", None),
        )


class CustomFormModelInfo:
    """Custom model information.

    .. versionadded:: v2.1
        The *model_name* and *properties* properties, support for *to_dict* and *from_dict* methods
    """
    model_id: str
    """The unique identifier of the model."""
    status: str
    """The status of the model, :class:`~azure.ai.formrecognizer.CustomFormModelStatus`.
        Possible values include: 'creating', 'ready', 'invalid'."""
    training_started_on: datetime.datetime
    """Date and time (UTC) when model training was started."""
    training_completed_on: datetime.datetime
    """Date and time (UTC) when model training completed."""
    model_name: str
    """Optional user defined model name."""
    properties: CustomFormModelProperties
    """Optional model properties."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"CustomFormModelInfo(model_id={self.model_id}, status={self.status}, "
            f"training_started_on={self.training_started_on}, training_completed_on={self.training_completed_on}, "
            f"properties={repr(self.properties)}, model_name={self.model_name})"
        )[:1024]

    def to_dict(self) -> Dict:
        """Returns a dict representation of CustomFormModelInfo."""
        return {
            "model_id": self.model_id,
            "status": self.status,
            "training_started_on": self.training_started_on,
            "training_completed_on": self.training_completed_on,
            "model_name": self.model_name,
            "properties": self.properties.to_dict() if self.properties else None,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CustomFormModelInfo":
        """Converts a dict in the shape of a CustomFormModelInfo to the model itself.

        :param Dict data: A dictionary in the shape of CustomFormModelInfo.
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


class CustomFormSubmodel:
    """Represents a submodel that extracts fields from a specific type of form.

    .. versionadded:: v2.1
        The *model_id* property, support for *to_dict* and *from_dict* methods
    """
    model_id: str
    """Model identifier of the submodel."""
    accuracy: float
    """The mean of the model's field accuracies."""
    fields: Dict[str, CustomFormModelField]
    """A dictionary of the fields that this submodel will recognize
        from the input document. The fields dictionary keys are the `name` of
        the field. For models trained with labels, this is the training-time
        label of the field. For models trained without labels, a unique name
        is generated for each field."""
    form_type: str
    """Type of form this submodel recognizes."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"CustomFormSubmodel(accuracy={self.accuracy}, model_id={self.model_id}, "
            f"fields={repr(self.fields)}, form_type={self.form_type})"
        )[:1024]

    def to_dict(self) -> Dict:
        """Returns a dict representation of CustomFormSubmodel."""
        return {
            "model_id": self.model_id,
            "accuracy": self.accuracy,
            "fields": {k: v.to_dict() for k, v in self.fields.items()}
            if self.fields
            else {},
            "form_type": self.form_type,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CustomFormSubmodel":
        """Converts a dict in the shape of a CustomFormSubmodel to the model itself.

        :param Dict data: A dictionary in the shape of CustomFormSubmodel.
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


class CustomFormModel:
    """Represents a trained model.

    .. versionadded:: v2.1
        The *model_name* and *properties* properties, support for *to_dict* and *from_dict* methods
    """
    model_id: str
    """The unique identifier of this model."""
    status: str
    """Status indicating the model's readiness for use,
        :class:`~azure.ai.formrecognizer.CustomFormModelStatus`.
        Possible values include: 'creating', 'ready', 'invalid'."""
    training_started_on: datetime.datetime
    """The date and time (UTC) when model training was started."""
    training_completed_on: datetime.datetime
    """Date and time (UTC) when model training completed."""
    submodels: List[CustomFormSubmodel]
    """A list of submodels that are part of this model, each of
        which can recognize and extract fields from a different type of form."""
    errors: List[FormRecognizerError]
    """List of any training errors."""
    training_documents: List[TrainingDocumentInfo]
    """Metadata about each of the documents used to train the model."""
    model_name: str
    """Optional user defined model name."""
    properties: CustomFormModelProperties
    """Optional model properties."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"CustomFormModel(model_id={self.model_id}, status={self.status}, "
            f"training_started_on={self.training_started_on}, training_completed_on={self.training_completed_on}, "
            f"submodels={repr(self.submodels)}, errors={repr(self.errors)}, "
            f"training_documents={repr(self.training_documents)}, model_name={self.model_name}, "
            f"properties={repr(self.properties)})"
        )[:1024]

    def to_dict(self) -> Dict:
        """Returns a dict representation of CustomFormModel."""
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
    def from_dict(cls, data: Dict) -> "CustomFormModel":
        """Converts a dict in the shape of a CustomFormModel to the model itself.

        :param Dict data: A dictionary in the shape of CustomFormModel.
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


class DocumentSpan:
    """Contiguous region of the content of the property, specified as an offset and length."""

    offset: int
    """Zero-based index of the content represented by the span."""
    length: int
    """Number of characters in the content represented by the span."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return f"DocumentSpan(offset={self.offset}, length={self.length})"

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentSpan."""
        return {
            "offset": self.offset,
            "length": self.length,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "DocumentSpan":
        """Converts a dict in the shape of a DocumentSpan to the model itself.

        :param Dict data: A dictionary in the shape of DocumentSpan.
        :return: DocumentSpan
        :rtype: DocumentSpan
        """
        return cls(
            offset=data.get("offset", None),
            length=data.get("length", None),
        )


class BoundingRegion:
    """The bounding region corresponding to a page."""

    polygon: Sequence[Point]
    """A list of points representing the bounding polygon
        that outlines the document component. The points are listed in
        clockwise order relative to the document component orientation
        starting from the top-left.
        Units are in pixels for images and inches for PDF."""
    page_number: int
    """The 1-based number of the page in which this content is present."""

    def __init__(self, **kwargs: Any) -> None:
        self.page_number = kwargs.get("page_number", None)
        self.polygon = kwargs.get("polygon", None)

    def __repr__(self) -> str:
        return f"BoundingRegion(page_number={self.page_number}, polygon={self.polygon})"

    @classmethod
    def _from_generated(cls, region):
        return cls(
            page_number=region.page_number,
            polygon=get_polygon(region),
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of BoundingRegion."""
        return {
            "page_number": self.page_number,
            "polygon": [f.to_dict() for f in self.polygon]
            if self.polygon
            else [],
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "BoundingRegion":
        """Converts a dict in the shape of a BoundingRegion to the model itself.

        :param Dict data: A dictionary in the shape of BoundingRegion.
        :return: BoundingRegion
        :rtype: BoundingRegion
        """
        return cls(
            page_number=data.get("page_number", None),
            polygon=[Point.from_dict(v) for v in data.get("polygon")]  # type: ignore
            if len(data.get("polygon", [])) > 0
            else [],
        )


class AddressValue:  # pylint: disable=too-many-instance-attributes
    """An address field value.

    .. versionadded:: 2023-02-28-preview
        The *unit*, *city_district*, *state_district*, *suburb*, *house*,
        and *level*  properties.
    """

    house_number: Optional[str]
    """House or building number."""
    po_box: Optional[str]
    """Post office box number."""
    road: Optional[str]
    """Street name."""
    city: Optional[str]
    """Name of city, town, village, etc."""
    state: Optional[str]
    """First-level administrative division."""
    postal_code: Optional[str]
    """Postal code used for mail sorting."""
    country_region: Optional[str]
    """Country/region."""
    street_address: Optional[str]
    """Street-level address, excluding city, state, countryRegion, and
     postalCode."""
    unit: Optional[str]
    """Apartment or office number."""
    city_district: Optional[str]
    """Districts or boroughs within a city, such as Brooklyn in New York City or City
    of Westminster in London."""
    state_district: Optional[str]
    """Second-level administrative division used in certain locales."""
    suburb: Optional[str]
    """Unofficial neighborhood name, like Chinatown."""
    house: Optional[str]
    """Building name, such as World Trade Center."""
    level: Optional[str]
    """Floor number, such as 3F."""

    def __init__(self, **kwargs: Any) -> None:
        self.house_number = kwargs.get("house_number", None)
        self.po_box = kwargs.get("po_box", None)
        self.road = kwargs.get("road", None)
        self.city = kwargs.get("city", None)
        self.state = kwargs.get("state", None)
        self.postal_code = kwargs.get("postal_code", None)
        self.country_region = kwargs.get("country_region", None)
        self.street_address = kwargs.get("street_address", None)
        self.unit = kwargs.get("unit", None)
        self.city_district = kwargs.get("city_district", None)
        self.state_district = kwargs.get("state_district", None)
        self.suburb = kwargs.get("suburb", None)
        self.house = kwargs.get("house", None)
        self.level = kwargs.get("level", None)

    @classmethod
    def _from_generated(cls, data):
        unit = data.unit if hasattr(data, "unit") else None
        city_district = data.city_district if hasattr(data, "city_district") else None
        state_district = data.state_district if hasattr(data, "state_district") else None
        suburb = data.suburb if hasattr(data, "suburb") else None
        house = data.house if hasattr(data, "house") else None
        level = data.level if hasattr(data, "level") else None
        return cls(
            house_number=data.house_number,
            po_box=data.po_box,
            road=data.road,
            city=data.city,
            state=data.state,
            postal_code=data.postal_code,
            country_region=data.country_region,
            street_address=data.street_address,
            unit=unit,
            city_district=city_district,
            state_district=state_district,
            suburb=suburb,
            house=house,
            level=level
        )

    def __repr__(self) -> str:
        return (
            f"AddressValue(house_number={self.house_number}, po_box={self.po_box}, road={self.road}, "
            f"city={self.city}, state={self.state}, postal_code={self.postal_code}, "
            f"country_region={self.country_region}, street_address={self.street_address}, "
            f"unit={self.unit}, city_district={self.city_district}, state_district={self.state_district}, "
            f"suburb={self.suburb}, house={self.house}, level={self.level})"
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of AddressValue."""
        return {
            "house_number": self.house_number,
            "po_box": self.po_box,
            "road": self.road,
            "city": self.city,
            "state": self.state,
            "postal_code": self.postal_code,
            "country_region": self.country_region,
            "street_address": self.street_address,
            "unit": self.unit,
            "city_district": self.city_district,
            "state_district": self.state_district,
            "suburb": self.suburb,
            "house": self.house,
            "level": self.level,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "AddressValue":
        """Converts a dict in the shape of a AddressValue to the model itself.

        :param Dict data: A dictionary in the shape of AddressValue.
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
            unit=data.get("unit", None),
            city_district=data.get("city_district", None),
            state_district=data.get("state_district", None),
            suburb=data.get("suburb", None),
            house=data.get("house", None),
            level=data.get("level", None)
        )


class CurrencyValue:
    """A currency value element.

    .. versionadded:: 2023-02-28-preview
        The *code*  property.
    """

    amount: float
    """The currency amount."""
    symbol: Optional[str]
    """The currency symbol, if found."""
    code: Optional[str]
    """Resolved currency code (ISO 4217), if any."""

    def __init__(self, **kwargs: Any) -> None:
        self.amount = kwargs.get("amount", None)
        self.symbol = kwargs.get("symbol", None)
        self.code = kwargs.get("code", None)

    @classmethod
    def _from_generated(cls, data):
        currency_code = data.currency_code if hasattr(data, "currency_code") else None
        return cls(
            amount=data.amount,
            symbol=data.currency_symbol,
            code=currency_code
        )

    def __str__(self):
        if self.symbol is not None:
            return f"{self.symbol}{self.amount}"
        return f"{self.amount}"

    def __repr__(self) -> str:
        return f"CurrencyValue(amount={self.amount}, symbol={self.symbol}, code={self.code})"

    def to_dict(self) -> Dict:
        """Returns a dict representation of CurrencyValue."""
        return {
            "amount": self.amount,
            "symbol": self.symbol,
            "code": self.code,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CurrencyValue":
        """Converts a dict in the shape of a CurrencyValue to the model itself.

        :param Dict data: A dictionary in the shape of CurrencyValue.
        :return: CurrencyValue
        :rtype: CurrencyValue
        """
        return cls(
            amount=data.get("amount", None),
            symbol=data.get("symbol", None),
            code=data.get("code", None),
        )


class DocumentLanguage:
    """An object representing the detected language for a given text span."""

    locale: str
    """Detected language code. Value may be an ISO 639-1 language code (ex.
     "en", "fr") or a BCP 47 language tag (ex. "zh-Hans")."""
    spans: List[DocumentSpan]
    """Location of the text elements in the concatenated content that the language
     applies to."""
    confidence: float
    """Confidence of correctly identifying the language."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return f"DocumentLanguage(locale={self.locale}, spans={repr(self.spans)}, confidence={self.confidence})"

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentLanguage."""
        return {
            "locale": self.locale,
            "spans": [f.to_dict() for f in self.spans]
            if self.spans
            else [],
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "DocumentLanguage":
        """Converts a dict in the shape of a DocumentLanguage to the model itself.

        :param Dict data: A dictionary in the shape of DocumentLanguage.
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


class DocumentField:
    """An object representing the content and location of a document field value.

    .. versionadded:: 2023-02-28-preview
        The `boolean` value_type and `bool` value
    """

    value_type: str
    """The type of `value` found on DocumentField. Possible types include:
     "string", "date", "time", "phoneNumber", "float", "integer", "selectionMark", "countryRegion",
     "signature", "currency", "address", "boolean", "list", "dictionary"."""
    value: Optional[Union[str, int, float, bool, datetime.date, datetime.time,
        CurrencyValue, AddressValue, Dict[str, "DocumentField"], List["DocumentField"]]]
    """The value for the recognized field. Its semantic data type is described by `value_type`.
        If the value is extracted from the document, but cannot be normalized to its type,
        then access the `content` property for a textual representation of the value."""
    content: Optional[str]
    """The field's content."""
    bounding_regions: Optional[List[BoundingRegion]]
    """Bounding regions covering the field."""
    spans: Optional[List[DocumentSpan]]
    """Location of the field in the reading order concatenated content."""
    confidence: float
    """The confidence of correctly extracting the field."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"DocumentField(value_type={self.value_type}, value={repr(self.value)}, content={self.content}, "
            f"bounding_regions={repr(self.bounding_regions)}, spans={repr(self.spans)}, "
            f"confidence={self.confidence})"
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentField."""
        value = self.value
        # CurrencyValue objects are interpreted as dict, therefore need to be processed first
        # to call the proper to_dict() method.
        if self.value_type == "currency":
            value = self.value.to_dict() if self.value else None  # type: ignore
        # AddressValue objects are interpreted as dict, therefore need to be processed first
        # to call the proper to_dict() method.
        elif self.value_type == "address":
            value = self.value.to_dict() if self.value else None  # type: ignore
        elif isinstance(self.value, dict):
            value = {k: v.to_dict() for k, v in self.value.items()} if self.value else {}  # type: ignore
        elif isinstance(self.value, list):
            value = [v.to_dict() for v in self.value] if self.value else []  # type: ignore
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
    def from_dict(cls, data: Dict) -> "DocumentField":
        """Converts a dict in the shape of a DocumentField to the model itself.

        :param Dict data: A dictionary in the shape of DocumentField.
        :return: DocumentField
        :rtype: DocumentField
        """

        value = data.get("value", None)
        # CurrencyValue objects are interpreted as dict, therefore need to be processed first
        # to call the proper from_dict() method.
        if data.get("value_type", None) == "currency":
            if value is not None:
                value = CurrencyValue.from_dict(data.get("value"))  #type: ignore
        # AddressValue objects are interpreted as dict, therefore need to be processed first
        # to call the proper from_dict() method.
        elif data.get("value_type", None) == "address":
            if value is not None:
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


class AnalyzedDocument:
    """An object describing the location and semantic content of a document."""

    doc_type: str
    """The type of document that was analyzed."""
    bounding_regions: Optional[List[BoundingRegion]]
    """Bounding regions covering the document."""
    spans: List[DocumentSpan]
    """The location of the document in the reading order concatenated content."""
    fields: Optional[Dict[str, DocumentField]]
    """A dictionary of named field values."""
    confidence: float
    """Confidence of correctly extracting the document."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"AnalyzedDocument(doc_type={self.doc_type}, bounding_regions={repr(self.bounding_regions)}, "
            f"spans={repr(self.spans)}, fields={repr(self.fields)}, confidence={self.confidence})"
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of AnalyzedDocument."""
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
    def from_dict(cls, data: Dict) -> "AnalyzedDocument":
        """Converts a dict in the shape of a AnalyzedDocument to the model itself.

        :param Dict data: A dictionary in the shape of AnalyzedDocument.
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


class DocumentKeyValueElement:
    """An object representing the field key or value in a key-value pair."""

    content: str
    """Concatenated content of the key-value element in reading order."""
    bounding_regions: Optional[List[BoundingRegion]]
    """Bounding regions covering the key-value element."""
    spans: List[DocumentSpan]
    """Location of the key-value element in the reading order of the concatenated
     content."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"DocumentKeyValueElement(content={self.content}, bounding_regions={repr(self.bounding_regions)}, "
            f"spans={repr(self.spans)})"
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentKeyValueElement."""
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
    def from_dict(cls, data: Dict) -> "DocumentKeyValueElement":
        """Converts a dict in the shape of a DocumentKeyValueElement to the model itself.

        :param Dict data: A dictionary in the shape of DocumentKeyValueElement.
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

    .. versionadded:: 2023-02-28-preview
        The *common_name*  property.
    """

    key: DocumentKeyValueElement
    """Field label of the key-value pair."""
    value: Optional[DocumentKeyValueElement]
    """Field value of the key-value pair."""
    confidence: float
    """Confidence of correctly extracting the key-value pair."""
    common_name: Optional[str]
    """Common name of the key-value pair."""

    def __init__(self, **kwargs: Any) -> None:
        self.key = kwargs.get("key", None)
        self.value = kwargs.get("value", None)
        self.confidence = kwargs.get("confidence", None)
        self.common_name = kwargs.get("common_name", None)

    @classmethod
    def _from_generated(cls, key_value_pair):
        common_name = key_value_pair.common_name if hasattr(key_value_pair, "common_name") else None
        return cls(
            key=DocumentKeyValueElement._from_generated(key_value_pair.key)
            if key_value_pair.key
            else None,
            value=DocumentKeyValueElement._from_generated(key_value_pair.value)
            if key_value_pair.value
            else None,
            confidence=key_value_pair.confidence,
            common_name=common_name
        )

    def __repr__(self) -> str:
        return (
            f"DocumentKeyValuePair(key={repr(self.key)}, value={repr(self.value)}, "
            f"confidence={self.confidence}, common_name={self.common_name})"
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentKeyValuePair."""
        return {
            "key": self.key.to_dict() if self.key else None,
            "value": self.value.to_dict() if self.value else None,
            "confidence": self.confidence,
            "common_name": self.common_name,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "DocumentKeyValuePair":
        """Converts a dict in the shape of a DocumentKeyValuePair to the model itself.

        :param Dict data: A dictionary in the shape of DocumentKeyValuePair.
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
            common_name=data.get("common_name", None),
        )


class DocumentWord:
    """A word object consisting of a contiguous sequence of characters.  For non-space delimited languages,
    such as Chinese, Japanese, and Korean, each character is represented as its own word.
    """
    content: str
    """Text content of the word."""
    polygon: Optional[Sequence[Point]]
    """Bounding polygon of the word."""
    span: DocumentSpan
    """Location of the word in the reading order concatenated content."""
    confidence: float
    """Confidence of correctly extracting the word."""

    def __init__(self, **kwargs: Any) -> None:
        self.content = kwargs.get("content", None)
        self.polygon = kwargs.get("polygon", None)
        self.span = kwargs.get("span", None)
        self.confidence = kwargs.get("confidence", None)

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

    def __repr__(self) -> str:
        return (
            f"DocumentWord(content={self.content}, polygon={self.polygon}, "
            f"span={repr(self.span)}, confidence={self.confidence})"
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentWord."""
        return {
            "content": self.content,
            "polygon": [f.to_dict() for f in self.polygon]
            if self.polygon
            else [],
            "span": self.span.to_dict() if self.span else None,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "DocumentWord":
        """Converts a dict in the shape of a DocumentWord to the model itself.

        :param Dict data: A dictionary in the shape of DocumentWord.
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


class DocumentSelectionMark:
    """A selection mark object representing check boxes, radio buttons, and other elements indicating a selection."""

    state: str
    """State of the selection mark. Possible values include: "selected",
     "unselected"."""
    polygon: Optional[Sequence[Point]]
    """Bounding polygon of the selection mark."""
    span: DocumentSpan
    """Location of the selection mark in the reading order concatenated
     content."""
    confidence: float
    """Confidence of correctly extracting the selection mark."""

    def __init__(self, **kwargs: Any) -> None:
        self.polygon = kwargs.get("polygon", None)
        self.span = kwargs.get("span", None)
        self.confidence = kwargs.get("confidence", None)
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

    def __repr__(self) -> str:
        return (
            f"DocumentSelectionMark(state={self.state}, span={repr(self.span)}, "
            f"confidence={self.confidence}, polygon={self.polygon})"
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentSelectionMark."""
        return {
            "state": self.state,
            "polygon": [f.to_dict() for f in self.polygon]
            if self.polygon
            else [],
            "span": self.span.to_dict() if self.span else None,
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "DocumentSelectionMark":
        """Converts a dict in the shape of a DocumentSelectionMark to the model itself.

        :param Dict data: A dictionary in the shape of DocumentSelectionMark.
        :return: DocumentSelectionMark
        :rtype: DocumentSelectionMark
        """
        return cls(
            state=data.get("state", None),
            polygon=[Point.from_dict(v) for v in data.get("polygon")]  # type: ignore
            if len(data.get("polygon", [])) > 0
            else [],
            span=DocumentSpan.from_dict(data.get("span")) if data.get("span") else None,  # type: ignore
            confidence=data.get("confidence", None),
        )


class DocumentLine:
    """A content line object representing the content found on a single line of the document."""

    content: str
    """Concatenated content of the contained elements in reading order."""
    polygon: Optional[Sequence[Point]]
    """Bounding polygon of the line."""
    spans: List[DocumentSpan]
    """Location of the line in the reading order concatenated content."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return f"DocumentLine(content={self.content}, polygon={self.polygon}, spans={repr(self.spans)})"

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentLine."""
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
    def from_dict(cls, data: Dict) -> "DocumentLine":
        """Converts a dict in the shape of a DocumentLine to the model itself.

        :param Dict data: A dictionary in the shape of DocumentLine.
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

    def get_words(self) -> Iterable["DocumentWord"]:
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

    .. versionadded:: 2023-02-28-preview
        The `formulaBlock` role.
    """

    role: Optional[str]
    """Semantic role of the paragraph. Known values are: "pageHeader", "pageFooter",
     "pageNumber", "title", "sectionHeading", "footnote", "formulaBlock"."""
    content: str
    """Concatenated content of the paragraph in reading order."""
    bounding_regions: Optional[List[BoundingRegion]]
    """Bounding regions covering the paragraph."""
    spans: List[DocumentSpan]
    """Location of the paragraph in the reading order concatenated content."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"DocumentParagraph(role={self.role}, content={self.content}, "
            f"bounding_regions={repr(self.bounding_regions)}, spans={repr(self.spans)})"
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentParagraph."""
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
    def from_dict(cls, data: Dict) -> "DocumentParagraph":
        """Converts a dict in the shape of a DocumentParagraph to the model itself.

        :param Dict data: A dictionary in the shape of DocumentParagraph.
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


class DocumentAnnotation:
    """An annotation object that represents a visual annotation in the document,
    such as checks ✓ and crosses X.
    """

    kind: str
    """Annotation kind. Known values are: "check", "cross"."""
    polygon: Sequence[Point]
    """Bounding polygon of the annotation."""
    confidence: float
    """Confidence of correctly extracting the annotation."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        self.kind = kwargs.get("kind", None)
        self.polygon = kwargs.get("polygon", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, annotation):
        return cls(
            kind=annotation.kind,
            polygon=get_polygon(annotation),
            confidence=annotation.confidence
        )

    def __repr__(self) -> str:
        return (
            f"DocumentAnnotation(kind={self.kind}, polygon={self.polygon}, confidence={self.confidence})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dict representation of DocumentAnnotation."""
        return {
            "kind": self.kind,
            "polygon": [f.to_dict() for f in self.polygon]
            if self.polygon
            else [],
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentAnnotation":
        """Converts a dict in the shape of a DocumentAnnotation to the model itself.

        :param Dict data: A dictionary in the shape of DocumentAnnotation.
        :return: DocumentAnnotation
        :rtype: DocumentAnnotation
        """
        return cls(
            kind=data.get("kind", None),
            polygon=[Point.from_dict(v) for v in data.get("polygon")]  # type: ignore
            if len(data.get("polygon", [])) > 0
            else [],
            confidence=data.get("confidence", None),
        )


class DocumentBarcode:
    """A barcode object."""

    kind: str
    """Barcode kind. Known values are "QRCode", "PDF417", "UPCA", "UPCE",
     "Code39", "Code128", "EAN8", "EAN13", "DataBar", "Code93", "Codabar", "DataBarExpanded", "ITF",
     "MicroQRCode", "Aztec", "DataMatrix", "MaxiCode"."""
    value: str
    """Barcode value."""
    polygon: Sequence[Point]
    """Bounding polygon of the barcode."""
    span: DocumentSpan
    """Location of the barcode in the reading order concatenated content."""
    confidence: float
    """Confidence of correctly extracting the barcode."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        self.kind = kwargs.get("kind", None)
        self.value = kwargs.get("value", None)
        self.polygon = kwargs.get("polygon", None)
        self.span = kwargs.get("span", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, barcode):
        return cls(
            kind=barcode.kind,
            value=barcode.value,
            span=DocumentSpan._from_generated(barcode.span)
            if barcode.span
            else None,
            polygon=get_polygon(barcode) if barcode.polygon else [],
            confidence=barcode.confidence
        )

    def __repr__(self) -> str:
        return (
            f"DocumentBarcode(kind={self.kind}, polygon={self.polygon}, confidence={self.confidence}, "
            f"value={self.value}, span={repr(self.span)})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dict representation of DocumentBarcode."""
        return {
            "kind": self.kind,
            "polygon": [f.to_dict() for f in self.polygon]
            if self.polygon
            else [],
            "confidence": self.confidence,
            "span": self.span.to_dict() if self.span else None,
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentBarcode":
        """Converts a dict in the shape of a DocumentBarcode to the model itself.

        :param Dict data: A dictionary in the shape of DocumentBarcode.
        :return: DocumentBarcode
        :rtype: DocumentBarcode
        """
        return cls(
            kind=data.get("kind", None),
            polygon=[Point.from_dict(v) for v in data.get("polygon")]  # type: ignore
            if len(data.get("polygon", [])) > 0
            else [],
            confidence=data.get("confidence", None),
            span=DocumentSpan.from_dict(data.get("span")) if data.get("span") else None,  # type: ignore
            value=data.get("value", None),
        )


class DocumentFormula:
    """A formula object."""

    kind: str
    """Formula kind. Known values are "inline", "display"."""
    value: str
    """LaTex expression describing the formula."""
    polygon: Sequence[Point]
    """Bounding polygon of the formula."""
    span: DocumentSpan
    """Location of the formula in the reading order concatenated content."""
    confidence: float
    """Confidence of correctly extracting the formula."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        self.kind = kwargs.get("kind", None)
        self.value = kwargs.get("value", None)
        self.polygon = kwargs.get("polygon", None)
        self.span = kwargs.get("span", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, formula):
        return cls(
            kind=formula.kind,
            value=formula.value,
            span=DocumentSpan._from_generated(formula.span)
            if formula.span
            else None,
            polygon=get_polygon(formula) if formula.polygon else [],
            confidence=formula.confidence
        )

    def __repr__(self) -> str:
        return (
            f"DocumentFormula(kind={self.kind}, polygon={self.polygon}, confidence={self.confidence}, "
            f"value={self.value}, span={repr(self.span)})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dict representation of DocumentFormula."""
        return {
            "kind": self.kind,
            "polygon": [f.to_dict() for f in self.polygon]
            if self.polygon
            else [],
            "confidence": self.confidence,
            "span": self.span.to_dict() if self.span else None,
            "value": self.value,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentFormula":
        """Converts a dict in the shape of a DocumentFormula to the model itself.

        :param Dict data: A dictionary in the shape of DocumentFormula.
        :return: DocumentFormula
        :rtype: DocumentFormula
        """
        return cls(
            kind=data.get("kind", None),
            polygon=[Point.from_dict(v) for v in data.get("polygon")]  # type: ignore
            if len(data.get("polygon", [])) > 0
            else [],
            confidence=data.get("confidence", None),
            span=DocumentSpan.from_dict(data.get("span")) if data.get("span") else None,  # type: ignore
            value=data.get("value", None),
        )


class DocumentImage:
    """An image object detected in the page."""

    page_number: int
    """1-based page number of the page that contains the image."""
    polygon: Sequence[Point]
    """Bounding polygon of the image."""
    span: DocumentSpan
    """Location of the image in the reading order concatenated content."""
    confidence: float
    """Confidence of correctly identifying the image."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        self.page_number = kwargs.get("page_number", None)
        self.polygon = kwargs.get("polygon", None)
        self.span = kwargs.get("span", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, image):
        return cls(
            page_number=image.page_number,
            span=DocumentSpan._from_generated(image.span)
            if image.span
            else None,
            polygon=get_polygon(image) if image.polygon else [],
            confidence=image.confidence
        )

    def __repr__(self) -> str:
        return (
            f"DocumentImage(page_number={self.page_number}, polygon={self.polygon}, confidence={self.confidence}, "
            f"span={repr(self.span)})"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dict representation of DocumentImage."""
        return {
            "page_number": self.page_number,
            "polygon": [f.to_dict() for f in self.polygon]
            if self.polygon
            else [],
            "confidence": self.confidence,
            "span": self.span.to_dict() if self.span else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentImage":
        """Converts a dict in the shape of a DocumentImage to the model itself.

        :param Dict data: A dictionary in the shape of DocumentImage.
        :return: DocumentImage
        :rtype: DocumentImage
        """
        return cls(
            page_number=data.get("page_number", None),
            polygon=[Point.from_dict(v) for v in data.get("polygon")]  # type: ignore
            if len(data.get("polygon", [])) > 0
            else [],
            confidence=data.get("confidence", None),
            span=DocumentSpan.from_dict(data.get("span")) if data.get("span") else None,  # type: ignore
        )


class DocumentPage:  # pylint: disable=too-many-instance-attributes
    """Content and layout elements extracted from a page of the input.

    .. versionadded:: 2023-02-28-preview
        The *kind*, *annotations*, *barcodes*, *formulas*, and *images* properties.
    """

    page_number: int
    """1-based page number in the input document."""
    angle: Optional[float]
    """The general orientation of the content in clockwise direction, measured
     in degrees between (-180, 180]."""
    width: Optional[float]
    """The width of the image/PDF in pixels/inches, respectively."""
    height: Optional[float]
    """The height of the image/PDF in pixels/inches, respectively."""
    unit: Optional[str]
    """The unit used by the width, height, and bounding polygon properties. For
     images, the unit is "pixel". For PDF, the unit is "inch". Possible values include: "pixel",
     "inch"."""
    spans: List[DocumentSpan]
    """Location of the page in the reading order concatenated content."""
    words: Optional[List[DocumentWord]]
    """Extracted words from the page."""
    selection_marks: Optional[List[DocumentSelectionMark]]
    """Extracted selection marks from the page."""
    lines: Optional[List[DocumentLine]]
    """Extracted lines from the page, potentially containing both textual and
     visual elements."""
    kind: str
    """Kind of document page. Known values are: "document", "sheet", "slide",
     "image"."""
    annotations: List[DocumentAnnotation]
    """Extracted annotations from the page."""
    barcodes: List[DocumentBarcode]
    """Extracted barcodes from the page."""
    formulas: List[DocumentFormula]
    """Extracted formulas from the page"""
    images: List[DocumentImage]
    """Extracted images from the page."""

    def __init__(self, **kwargs: Any) -> None:
        self.page_number = kwargs.get("page_number", None)
        self.angle = kwargs.get("angle", None)
        self.width = kwargs.get("width", None)
        self.height = kwargs.get("height", None)
        self.unit = kwargs.get("unit", None)
        self.spans = kwargs.get("spans", None)
        self.words = kwargs.get("words", None)
        self.selection_marks = kwargs.get("selection_marks", None)
        self.lines = kwargs.get("lines", None)
        self.kind = kwargs.get("kind", None)
        self.annotations = kwargs.get("annotations", None)
        self.barcodes = kwargs.get("barcodes", None)
        self.formulas = kwargs.get("formulas", None)
        self.images = kwargs.get("images", None)

    @classmethod
    def _from_generated(cls, page):
        kind = page.kind if hasattr(page, "kind") else None
        annotations = page.annotations if hasattr(page, "annotations") else None
        barcodes = page.barcodes if hasattr(page, "barcodes") else None
        formulas = page.formulas if hasattr(page, "formulas") else None
        images = page.images if hasattr(page, "images") else None

        return cls(
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
            kind=kind,
            annotations=[
                DocumentAnnotation._from_generated(annotation)
                for annotation in annotations
            ]
            if annotations
            else [],
            barcodes=[
                DocumentBarcode._from_generated(barcode)
                for barcode in barcodes
            ]
            if barcodes
            else [],
            formulas=[
                DocumentBarcode._from_generated(formula)
                for formula in formulas
            ]
            if formulas
            else [],
            images=[
                DocumentImage._from_generated(image)
                for image in images
            ]
            if images
            else [],
        )

    def __repr__(self) -> str:
        return (
            f"DocumentPage(page_number={self.page_number}, angle={self.angle}, "
            f"width={self.width}, height={self.height}, unit={self.unit}, lines={repr(self.lines)}, "
            f"words={repr(self.words)}, selection_marks={repr(self.selection_marks)}, "
            f"spans={repr(self.spans)}, kind={self.kind}, annotations={repr(self.annotations)}, "
            f"barcodes={repr(self.barcodes)}, formulas={repr(self.formulas)}, images={repr(self.images)})"
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentPage."""
        return {
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
            "kind": self.kind,
            "annotations": [f.to_dict() for f in self.annotations]
            if self.annotations
            else [],
            "barcodes": [f.to_dict() for f in self.barcodes]
            if self.barcodes
            else [],
            "formulas": [f.to_dict() for f in self.formulas]
            if self.formulas
            else [],
            "images": [f.to_dict() for f in self.images]
            if self.images
            else [],
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "DocumentPage":
        """Converts a dict in the shape of a DocumentPage to the model itself.

        :param Dict data: A dictionary in the shape of DocumentPage.
        :return: DocumentPage
        :rtype: DocumentPage
        """
        return cls(
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
            kind=data.get("kind", None),
            annotations=[DocumentAnnotation.from_dict(v) for v in data.get("annotations")]  # type: ignore
            if len(data.get("annotations", [])) > 0
            else [],
            barcodes=[DocumentBarcode.from_dict(v) for v in data.get("barcodes")]  # type: ignore
            if len(data.get("barcodes", [])) > 0
            else [],
            formulas=[DocumentFormula.from_dict(v) for v in data.get("formulas")]  # type: ignore
            if len(data.get("formulas", [])) > 0
            else [],
            images=[DocumentImage.from_dict(v) for v in data.get("images")]  # type: ignore
            if len(data.get("images", [])) > 0
            else [],
        )


class DocumentStyle:
    """An object representing observed text styles.

    .. versionadded:: 2023-02-28-preview
        The *similar_font_family*, *font_style*, *font_weight*, *color*, and *background_color* properties.
    """

    is_handwritten: Optional[bool]
    """Indicates if the content is handwritten."""
    similar_font_family: Optional[str]
    """Visually most similar font from among the set of supported font
    families, with fallback fonts following CSS convention (ex. 'Arial, sans-serif').
    """
    font_style: Optional[str]
    """Font style. Known values are: "normal", "italic"."""
    font_weight: Optional[str]
    """Font weight. Known values are: "normal", "bold"."""
    color: Optional[str]
    """Foreground color in #rrggbb hexadecimal format."""
    background_color: Optional[str]
    """Background color in #rrggbb hexadecimal format."""
    spans: List[DocumentSpan]
    """Location of the text elements in the concatenated content the style
     applies to."""
    confidence: float
    """Confidence of correctly identifying the style."""

    def __init__(self, **kwargs: Any) -> None:
        self.is_handwritten = kwargs.get("is_handwritten", None)
        self.similar_font_family = kwargs.get("similar_font_family", None)
        self.font_style = kwargs.get("font_style", None)
        self.font_weight = kwargs.get("font_weight", None)
        self.color = kwargs.get("color", None)
        self.background_color = kwargs.get("background_color", None)
        self.spans = kwargs.get("spans", None)
        self.confidence = kwargs.get("confidence", None)

    @classmethod
    def _from_generated(cls, style):
        # multi-api compatibility
        similar_font_family = style.similar_font_family if hasattr(style, "similar_font_family") else None
        font_style = style.font_style if hasattr(style, "font_style") else None
        font_weight = style.font_weight if hasattr(style, "font_weight") else None
        color = style.color if hasattr(style, "color") else None
        background_color = style.background_color if hasattr(style, "background_color") else None
        return cls(
            is_handwritten=style.is_handwritten,
            similar_font_family=similar_font_family,
            font_style=font_style,
            font_weight=font_weight,
            color=color,
            background_color=background_color,
            spans=[DocumentSpan._from_generated(span) for span in style.spans]
            if style.spans
            else [],
            confidence=style.confidence,
        )

    def __repr__(self) -> str:
        return (
            f"DocumentStyle(is_handwritten={self.is_handwritten}, spans={repr(self.spans)}, "
            f"confidence={self.confidence}, similar_font_family={self.similar_font_family}, "
            f"font_style={self.font_style}, font_weight={self.font_weight}, color={self.color}, "
            f"background_color={self.background_color})"
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentStyle."""
        return {
            "is_handwritten": self.is_handwritten,
            "similar_font_family": self.similar_font_family,
            "font_style": self.font_style,
            "font_weight": self.font_weight,
            "color": self.color,
            "background_color": self.background_color,
            "spans": [f.to_dict() for f in self.spans]
            if self.spans
            else [],
            "confidence": self.confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "DocumentStyle":
        """Converts a dict in the shape of a DocumentStyle to the model itself.

        :param Dict data: A dictionary in the shape of DocumentStyle.
        :return: DocumentStyle
        :rtype: DocumentStyle
        """
        return cls(
            is_handwritten=data.get("is_handwritten", None),
            similar_font_family=data.get("similar_font_family", None),
            font_style=data.get("font_style", None),
            font_weight=data.get("font_weight", None),
            color=data.get("color", None),
            background_color=data.get("background_color", None),
            spans=[DocumentSpan.from_dict(v) for v in data.get("spans")]  # type: ignore
            if len(data.get("spans", [])) > 0
            else [],
            confidence=data.get("confidence", None),
        )


class DocumentTableCell:
    """An object representing the location and content of a table cell."""

    kind: Optional[str]
    """Table cell kind. Possible values include: "content", "rowHeader", "columnHeader",
     "stubHead", "description". Default value: "content"."""
    row_index: int
    """Row index of the cell."""
    column_index: int
    """Column index of the cell."""
    row_span: Optional[int]
    """Number of rows spanned by this cell."""
    column_span: Optional[int]
    """Number of columns spanned by this cell."""
    content: str
    """Concatenated content of the table cell in reading order."""
    bounding_regions: Optional[List[BoundingRegion]]
    """Bounding regions covering the table cell."""
    spans: List[DocumentSpan]
    """Location of the table cell in the reading order concatenated content."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"DocumentTableCell(kind={self.kind}, row_index={self.row_index}, "
            f"column_index={self.column_index}, row_span={self.row_span}, "
            f"column_span={self.column_span}, content={self.content}, "
            f"bounding_regions={repr(self.bounding_regions)}, spans={repr(self.spans)})"
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentTableCell."""
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
    def from_dict(cls, data: Dict) -> "DocumentTableCell":
        """Converts a dict in the shape of a DocumentTableCell to the model itself.

        :param Dict data: A dictionary in the shape of DocumentTableCell.
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


class DocumentTable:
    """A table object consisting of table cells arranged in a rectangular layout."""

    row_count: int
    """Number of rows in the table."""
    column_count: int
    """Number of columns in the table."""
    cells: List[DocumentTableCell]
    """Cells contained within the table."""
    bounding_regions: Optional[List[BoundingRegion]]
    """Bounding regions covering the table."""
    spans: List[DocumentSpan]
    """Location of the table in the reading order concatenated content."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"DocumentTable(row_count={self.row_count}, column_count={self.column_count}, "
            f"cells={repr(self.cells)}, bounding_regions={repr(self.bounding_regions)}, "
            f"spans={repr(self.spans)})"
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentTable."""
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
    def from_dict(cls, data: Dict) -> "DocumentTable":
        """Converts a dict in the shape of a DocumentTable to the model itself.

        :param Dict data: A dictionary in the shape of DocumentTable.
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


class DocumentTypeDetails:
    """DocumentTypeDetails represents a document type that a model can recognize, including its
    fields and types, and the confidence for those fields.
    """
    description: Optional[str]
    """A description for the model."""
    build_mode: Optional[str]
    """The build mode used when building the custom model.
     Possible values include: "template", "neural"."""
    field_schema: Dict[str, Any]
    """Description of the document semantic schema."""
    field_confidence: Optional[Dict[str, float]]
    """Estimated confidence for each field."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        self.description = kwargs.get("description", None)
        self.build_mode = kwargs.get("build_mode", None)
        self.field_schema = kwargs.get("field_schema", None)
        self.field_confidence = kwargs.get("field_confidence", None)

    def __repr__(self) -> str:
        return (
            f"DocumentTypeDetails(description={self.description}, build_mode={self.build_mode}, "
            f"field_schema={self.field_schema}, field_confidence={self.field_confidence})"
        )

    @classmethod
    def _from_generated(cls, doc_type):
        return cls(
            description=doc_type.description,
            build_mode=doc_type.build_mode,
            field_schema={name: field.serialize() for name, field in doc_type.field_schema.items()}
            if doc_type.field_schema else {},
            field_confidence=doc_type.field_confidence
            if doc_type.field_confidence else {},
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentTypeDetails."""
        return {
            "description": self.description,
            "build_mode": self.build_mode,
            "field_schema": self.field_schema,
            "field_confidence": self.field_confidence,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "DocumentTypeDetails":
        """Converts a dict in the shape of a DocumentTypeDetails to the model itself.

        :param Dict data: A dictionary in the shape of DocumentTypeDetails.
        :return: DocumentTypeDetails
        :rtype: DocumentTypeDetails
        """
        return cls(
            description=data.get("description", None),
            build_mode=data.get("build_mode", None),
            field_schema=data.get("field_schema", {}),
            field_confidence=data.get("field_confidence", {}),
        )


class DocumentModelSummary:
    """A summary of document model information including the model ID,
    its description, and when the model was created.

    .. versionadded:: 2023-02-28-preview
        The *expires_on* property.
    """
    model_id: str
    """Unique model id."""
    description: Optional[str]
    """A description for the model."""
    created_on: datetime.datetime
    """Date and time (UTC) when the model was created."""
    expires_on: Optional[datetime.datetime]
    """Date and time (UTC) when the document model will expire."""
    api_version: Optional[str]
    """API version used to create this model."""
    tags: Optional[Dict[str, str]]
    """List of user defined key-value tag attributes associated with the model."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        self.model_id = kwargs.get("model_id", None)
        self.description = kwargs.get("description", None)
        self.created_on = kwargs.get("created_on", None)
        self.expires_on = kwargs.get("expires_on", None)
        self.api_version = kwargs.get("api_version", None)
        self.tags = kwargs.get("tags", None)

    def __repr__(self) -> str:
        return (
            f"DocumentModelSummary(model_id={self.model_id}, description={self.description}, "
            f"created_on={self.created_on}, api_version={self.api_version}, tags={self.tags}, "
            f"expires_on={self.expires_on})"
        )

    @classmethod
    def _from_generated(cls, model):
        expires_on = model.expiration_date_time if hasattr(model, "expiration_date_time") else None
        return cls(
            model_id=model.model_id,
            description=model.description,
            created_on=model.created_date_time,
            api_version=model.api_version,
            tags=model.tags if model.tags else {},
            expires_on=expires_on
        )

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dict representation of DocumentModelSummary."""
        return {
            "model_id": self.model_id,
            "description": self.description,
            "created_on": self.created_on,
            "api_version": self.api_version,
            "tags": self.tags if self.tags else {},
            "expires_on": self.expires_on,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentModelSummary":
        """Converts a dict in the shape of a DocumentModelSummary to the model itself.

        :param Dict data: A dictionary in the shape of DocumentModelSummary.
        :return: DocumentModelSummary
        :rtype: DocumentModelSummary
        """
        return cls(
            model_id=data.get("model_id", None),
            description=data.get("description", None),
            created_on=data.get("created_on", None),
            api_version=data.get("api_version", None),
            tags=data.get("tags", {}),
            expires_on=data.get("expires_on", None),
        )


class DocumentClassifierDetails:
    """Document classifier information. Includes the doc types that the model can classify."""

    classifier_id: str
    """Unique document classifier name."""
    description: Optional[str]
    """Document classifier description."""
    created_on: datetime.datetime
    """Date and time (UTC) when the document classifier was created."""
    expires_on: Optional[datetime.datetime]
    """Date and time (UTC) when the document classifier will expire."""
    api_version: str
    """API version used to create this document classifier."""
    doc_types: Dict[str, ClassifierDocumentTypeDetails]
    """List of document types to classify against."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        self.classifier_id = kwargs.get("classifier_id", None)
        self.description = kwargs.get("description", None)
        self.created_on = kwargs.get("created_on", None)
        self.expires_on = kwargs.get("expires_on", None)
        self.api_version = kwargs.get("api_version", None)
        self.doc_types = kwargs.get("doc_types", None)

    def __repr__(self) -> str:
        return (
            f"DocumentClassifierDetails(classifier_id={self.classifier_id}, description={self.description}, "
            f"created_on={self.created_on}, expires_on={self.expires_on}, "
            f"api_version={self.api_version}, doc_types={repr(self.doc_types)})"
        )

    @classmethod
    def _from_generated(cls, model):
        return cls(
            classifier_id=model.classifier_id,
            description=model.description,
            created_on=model.created_date_time,
            expires_on=model.expiration_date_time,
            api_version=model.api_version,
            doc_types={k: ClassifierDocumentTypeDetails._from_generated(v) for k, v in model.doc_types.items()}
            if model.doc_types else {}
        )

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dict representation of DocumentClassifierDetails."""
        return {
            "classifier_id": self.classifier_id,
            "description": self.description,
            "created_on": self.created_on,
            "expires_on": self.expires_on,
            "api_version": self.api_version,
            "doc_types": {k: v.to_dict() for k, v in self.doc_types.items()} if self.doc_types else {}  # type: ignore
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentClassifierDetails":
        """Converts a dict in the shape of a DocumentClassifierDetails to the model itself.

        :param Dict data: A dictionary in the shape of DocumentClassifierDetails.
        :return: DocumentClassifierDetails
        :rtype: DocumentClassifierDetails
        """
        return cls(
            classifier_id=data.get("classifier_id", None),
            description=data.get("description", None),
            created_on=data.get("created_on", None),
            expires_on=data.get("expires_on", None),
            api_version=data.get("api_version", None),
            doc_types={k: ClassifierDocumentTypeDetails.from_dict(v)
                       for k, v in data.get("doc_types").items()}  # type: ignore
            if data.get("doc_types")
            else {},
        )


class DocumentModelDetails(DocumentModelSummary):
    """Document model information. Includes the doc types that the model can analyze.

    .. versionadded:: 2023-02-28-preview
        The *expires_on* property.
    """

    model_id: str
    """Unique model id."""
    description: Optional[str]
    """A description for the model."""
    created_on: datetime.datetime
    """Date and time (UTC) when the model was created."""
    expires_on: Optional[datetime.datetime]
    """Date and time (UTC) when the document model will expire."""
    api_version: Optional[str]
    """API version used to create this model."""
    tags: Optional[Dict[str, str]]
    """List of user defined key-value tag attributes associated with the model."""
    doc_types: Optional[Dict[str, DocumentTypeDetails]]
    """Supported document types, including the fields for each document and their types."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        super().__init__(**kwargs)
        self.doc_types = kwargs.get("doc_types", None)

    def __repr__(self) -> str:
        return (
            f"DocumentModelDetails(model_id={self.model_id}, description={self.description}, "
            f"created_on={self.created_on}, api_version={self.api_version}, tags={self.tags}, "
            f"doc_types={repr(self.doc_types)}, expires_on={self.expires_on})"
        )

    @classmethod
    def _from_generated(cls, model):
        expires_on = model.expiration_date_time if hasattr(model, "expiration_date_time") else None
        return cls(
            model_id=model.model_id,
            description=model.description,
            created_on=model.created_date_time,
            api_version=model.api_version,
            tags=model.tags if model.tags else {},
            doc_types={k: DocumentTypeDetails._from_generated(v) for k, v in model.doc_types.items()}
            if model.doc_types else {},
            expires_on=expires_on
        )

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dict representation of DocumentModelDetails."""
        return {
            "model_id": self.model_id,
            "description": self.description,
            "created_on": self.created_on,
            "api_version": self.api_version,
            "tags": self.tags if self.tags else {},
            "doc_types": {k: v.to_dict() for k, v in self.doc_types.items()} if self.doc_types else {},
            "expires_on": self.expires_on,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentModelDetails":
        """Converts a dict in the shape of a DocumentModelDetails to the model itself.

        :param Dict data: A dictionary in the shape of DocumentModelDetails.
        :return: DocumentModelDetails
        :rtype: DocumentModelDetails
        """
        return cls(
            model_id=data.get("model_id", None),
            description=data.get("description", None),
            created_on=data.get("created_on", None),
            api_version=data.get("api_version", None),
            tags=data.get("tags", {}),
            doc_types={k: DocumentTypeDetails.from_dict(v) for k, v in data.get("doc_types").items()}  # type: ignore
            if data.get("doc_types")
            else {},
            expires_on=data.get("expires_on", None),
        )


class DocumentAnalysisInnerError:
    """Inner error details for the DocumentAnalysisError."""

    code: str
    """Error code."""
    message: Optional[str]
    """Error message."""
    innererror: Optional["DocumentAnalysisInnerError"]
    """Detailed error."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        self.code = kwargs.get("code", None)
        self.message = kwargs.get("message", None)
        self.innererror = kwargs.get("innererror", None)

    def __repr__(self) -> str:
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

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentAnalysisInnerError."""
        return {
            "code": self.code,
            "message": self.message,
            "innererror": self.innererror.to_dict() if self.innererror else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "DocumentAnalysisInnerError":
        """Converts a dict in the shape of a DocumentAnalysisInnerError to the model itself.

        :param Dict data: A dictionary in the shape of DocumentAnalysisInnerError.
        :return: DocumentAnalysisInnerError
        :rtype: DocumentAnalysisInnerError
        """
        return cls(
            code=data.get("code", None),
            message=data.get("message", None),
            innererror=DocumentAnalysisInnerError.from_dict(data.get("innererror"))  # type: ignore
            if data.get("innererror") else None
        )


class DocumentAnalysisError:
    """DocumentAnalysisError contains the details of the error returned by the service."""

    code: str
    """Error code."""
    message: str
    """Error message."""
    target: Optional[str]
    """Target of the error."""
    details: Optional[List["DocumentAnalysisError"]]
    """List of detailed errors."""
    innererror: Optional[DocumentAnalysisInnerError]
    """Detailed error."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        self.code = kwargs.get("code", None)
        self.message = kwargs.get("message", None)
        self.target = kwargs.get("target", None)
        self.details = kwargs.get("details", None)
        self.innererror = kwargs.get("innererror", None)

    def __repr__(self) -> str:
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

    def to_dict(self) -> Dict:
        """Returns a dict representation of DocumentAnalysisError."""
        return {
            "code": self.code,
            "message": self.message,
            "target": self.target,
            "details": [detail.to_dict() for detail in self.details] if self.details else [],
            "innererror": self.innererror.to_dict() if self.innererror else None
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "DocumentAnalysisError":
        """Converts a dict in the shape of a DocumentAnalysisError to the model itself.

        :param Dict data: A dictionary in the shape of DocumentAnalysisError.
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


class OperationSummary:
    """Model operation information, including the kind and status of the operation, when it was
    created, and more.

    Note that operation information only persists for 24 hours. If the operation was successful,
    the model can be accessed using the :func:`~get_document_model`, :func:`~list_document_models`,
    :func:`~get_document_classifier`, :func:`~list_document_classifiers` APIs.
    To find out why an operation failed, use :func:`~get_operation` and provide the `operation_id`.

    .. versionadded:: 2023-02-28-preview
        The `documentClassifierBuild` kind.
    """
    operation_id: str
    """Operation ID."""
    status: str
    """Operation status. Possible values include: "notStarted", "running",
        "failed", "succeeded", "canceled"."""
    percent_completed: Optional[int]
    """Operation progress (0-100)."""
    created_on: datetime.datetime
    """Date and time (UTC) when the operation was created."""
    last_updated_on: datetime.datetime
    """Date and time (UTC) when the operation was last updated."""
    kind: str
    """Type of operation. Possible values include: "documentModelBuild",
        "documentModelCompose", "documentModelCopyTo", "documentClassifierBuild"."""
    resource_location: str
    """URL of the resource targeted by this operation."""
    api_version: Optional[str]
    """API version used to create this operation."""
    tags: Optional[Dict[str, str]]
    """List of user defined key-value tag attributes associated with the model."""

    def __init__(self, **kwargs: Any) -> None:
        self.operation_id = kwargs.get("operation_id", None)
        self.status = kwargs.get("status", None)
        self.percent_completed = kwargs.get("percent_completed", 0)
        self.created_on = kwargs.get("created_on", None)
        self.last_updated_on = kwargs.get("last_updated_on", None)
        self.kind = kwargs.get("kind", None)
        self.resource_location = kwargs.get("resource_location", None)
        self.api_version = kwargs.get("api_version", None)
        self.tags = kwargs.get("tags", None)

    def __repr__(self) -> str:
        return (
            f"OperationSummary(operation_id={self.operation_id}, status={self.status}, "
            f"percent_completed={self.percent_completed}, created_on={self.created_on}, "
            f"last_updated_on={self.last_updated_on}, kind={self.kind}, "
            f"resource_location={self.resource_location}, api_version={self.api_version}, tags={self.tags})"
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of OperationSummary."""
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
    def from_dict(cls, data: Dict) -> "OperationSummary":
        """Converts a dict in the shape of a OperationSummary to the model itself.

        :param Dict data: A dictionary in the shape of OperationSummary.
        :return: OperationSummary
        :rtype: OperationSummary
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


class OperationDetails(OperationSummary):
    """OperationDetails consists of information about the model operation, including the result or
    error of the operation if it has completed.

    Note that operation information only persists for 24 hours. If the operation was successful,
    the model can also be accessed using the :func:`~get_document_model`, :func:`~list_document_models`,
    :func:`~get_document_classifier`, :func:`~list_document_classifiers` APIs.

    .. versionadded:: 2023-02-28-preview
        The `documentClassifierBuild` kind and `DocumentClassifierDetails` result.
    """
    operation_id: str
    """Operation ID."""
    status: str
    """Operation status. Possible values include: "notStarted", "running",
        "failed", "succeeded", "canceled"."""
    percent_completed: Optional[int]
    """Operation progress (0-100)."""
    created_on: datetime.datetime
    """Date and time (UTC) when the operation was created."""
    last_updated_on: datetime.datetime
    """Date and time (UTC) when the operation was last updated."""
    kind: str
    """Type of operation. Possible values include: "documentModelBuild",
        "documentModelCompose", "documentModelCopyTo", "documentClassifierBuild"."""
    resource_location: str
    """URL of the resource targeted by this operation."""
    error: Optional[DocumentAnalysisError]
    """Encountered error, includes the error code, message, and details for why
        the operation failed."""
    result: Optional[Union[DocumentModelDetails, DocumentClassifierDetails]]
    """Operation result upon success. Returns a DocumentModelDetails or DocumentClassifierDetails
        which contains all the information about the model."""
    api_version: Optional[str]
    """API version used to create this operation."""
    tags: Optional[Dict[str, str]]
    """List of user defined key-value tag attributes associated with the model."""

    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.error = kwargs.get("error", None)
        self.result = kwargs.get("result", None)

    def __repr__(self) -> str:
        return (
            f"OperationDetails(operation_id={self.operation_id}, status={self.status}, "
            f"percent_completed={self.percent_completed}, created_on={self.created_on}, "
            f"last_updated_on={self.last_updated_on}, kind={self.kind}, "
            f"resource_location={self.resource_location}, result={repr(self.result)}, "
            f"error={repr(self.error)}, api_version={self.api_version}, tags={self.tags})"
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of OperationDetails."""
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
    def from_dict(cls, data: Dict) -> "OperationDetails":
        """Converts a dict in the shape of a OperationDetails to the model itself.

        :param Dict data: A dictionary in the shape of OperationDetails.
        :return: OperationDetails
        :rtype: OperationDetails
        """

        kind = data.get("kind", None)
        if kind == "documentClassifierBuild":
            result = \
                DocumentClassifierDetails.from_dict(data.get("result")) if data.get("result") else None  # type: ignore
        else:
            result = \
                DocumentModelDetails.from_dict(data.get("result")) if data.get("result") else None  # type: ignore
        return cls(
            operation_id=data.get("operation_id", None),
            status=data.get("status", None),
            percent_completed=data.get("percent_completed", None),
            created_on=data.get("created_on", None),
            last_updated_on=data.get("last_updated_on", None),
            kind=data.get("kind", None),
            resource_location=data.get("resource_location", None),
            result=result,
            error=DocumentAnalysisError.from_dict(data.get("error")) if data.get("error") else None,  # type: ignore
            api_version=data.get("api_version", None),
            tags=data.get("tags", {}),
        )

    @classmethod
    def _from_generated(cls, op, api_version):  # pylint: disable=arguments-differ
        deserialize = _get_deserialize(api_version)
        if op.kind == "documentClassifierBuild":
            result = DocumentClassifierDetails._from_generated(deserialize(ClassifierDetails, op.result)) \
                if op.result else None
        else:
            result = DocumentModelDetails._from_generated(deserialize(ModelDetails, op.result)) \
                if op.result else None
        return cls(
            operation_id=op.operation_id,
            status=op.status,
            percent_completed=op.percent_completed if op.percent_completed else 0,
            created_on=op.created_date_time,
            last_updated_on=op.last_updated_date_time,
            kind=op.kind,
            resource_location=op.resource_location,
            result=result,
            error=DocumentAnalysisError._from_generated(deserialize(Error, op.error))
            if op.error else None,
            api_version=op.api_version,
            tags=op.tags if op.tags else {},
        )


class AnalyzeResult:  # pylint: disable=too-many-instance-attributes
    """Document analysis result."""

    api_version: str
    """API version used to produce this result."""
    model_id: str
    """Model ID used to produce this result."""
    content: str
    """Concatenate string representation of all textual and visual elements
     in reading order."""
    pages: List[DocumentPage]
    """Analyzed pages."""
    languages: Optional[List[DocumentLanguage]]
    """Detected languages in the document."""
    paragraphs: Optional[List[DocumentParagraph]]
    """Extracted paragraphs."""
    tables: Optional[List[DocumentTable]]
    """Extracted tables."""
    key_value_pairs: Optional[List[DocumentKeyValuePair]]
    """Extracted key-value pairs."""
    styles: Optional[List[DocumentStyle]]
    """Extracted font styles."""
    documents: Optional[List[AnalyzedDocument]]
    """Extracted documents."""

    def __init__(self, **kwargs: Any) -> None:
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

    def __repr__(self) -> str:
        return (
            f"AnalyzeResult(api_version={self.api_version}, model_id={self.model_id}, "
            f"content={self.content}, languages={repr(self.languages)}, "
            f"pages={repr(self.pages)}, paragraphs={repr(self.paragraphs)}, tables={repr(self.tables)}, "
            f"key_value_pairs={repr(self.key_value_pairs)}, "
            f"styles={repr(self.styles)}, documents={repr(self.documents)})"
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of AnalyzeResult."""
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
    def from_dict(cls, data: Dict) -> "AnalyzeResult":
        """Converts a dict in the shape of a AnalyzeResult to the model itself.

        :param Dict data: A dictionary in the shape of AnalyzeResult.
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


class CustomDocumentModelsDetails:
    """Details regarding the custom models under the Form Recognizer resource."""

    count: int
    """Number of custom models in the current resource."""
    limit: int
    """Maximum number of custom models supported in the current resource."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        self.count = kwargs.get("count", None)
        self.limit = kwargs.get("limit", None)

    def __repr__(self) -> str:
        return f"CustomDocumentModelsDetails(count={self.count}, limit={self.limit})"

    @classmethod
    def _from_generated(cls, info):
        return cls(
            count=info.count,
            limit=info.limit,
        )


    def to_dict(self) -> Dict:
        """Returns a dict representation of CustomDocumentModelsDetails."""
        return {
            "count": self.count,
            "limit": self.limit,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "CustomDocumentModelsDetails":
        """Converts a dict in the shape of a CustomDocumentModelsDetails to the model itself.

        :param Dict data: A dictionary in the shape of CustomDocumentModelsDetails.
        :return: CustomDocumentModelsDetails
        :rtype: CustomDocumentModelsDetails
        """
        return cls(
            count=data.get("count", None),
            limit=data.get("limit", None),
        )


class QuotaDetails:
    """Quota used, limit, and next reset date/time."""

    used: int
    """Amount of the resource quota used."""
    quota: int
    """Resource quota limit."""
    quota_resets_on: datetime.datetime
    """Date/time when the resource quota usage will be reset."""

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        self.used = kwargs.get("used", None)
        self.quota = kwargs.get("quota", None)
        self.quota_resets_on = kwargs.get("quota_resets_on", None)

    def __repr__(self) -> str:
        return f"QuotaDetails(used={self.used}, quota={self.quota}, quota_resets_on={self.quota_resets_on})"

    @classmethod
    def _from_generated(cls, info):
        return cls(
            used=info.used,
            quota=info.quota,
            quota_resets_on=info.quota_reset_date_time
        )

    def to_dict(self) -> Dict[str, Any]:
        """Returns a dict representation of QuotaDetails."""
        return {
                "used": self.used,
                "quota": self.quota,
                "quota_resets_on": self.quota_resets_on
            }

    @classmethod
    def from_dict(cls, data: Dict) -> "QuotaDetails":
        """Converts a dict in the shape of a QuotaDetails to the model itself.

        :param Dict data: A dictionary in the shape of QuotaDetails.
        :return: QuotaDetails
        :rtype: QuotaDetails
        """
        return cls(
            used=data.get("used", None),
            quota=data.get("quota", None),
            quota_resets_on=data.get("quota_resets_on", None)
        )


class ResourceDetails:
    """Details regarding the Form Recognizer resource.

    .. versionadded:: 2023-02-28-preview
        The *custom_neural_document_model_builds* property.
    """

    custom_document_models: CustomDocumentModelsDetails
    """Details regarding the custom models under the Form Recognizer resource."""
    custom_neural_document_model_builds: QuotaDetails

    def __init__(
        self,
        **kwargs: Any
    ) -> None:
        self.custom_document_models = kwargs.get("custom_document_models", None)
        self.custom_neural_document_model_builds = kwargs.get("custom_neural_document_model_builds", None)

    def __repr__(self) -> str:
        return f"ResourceDetails(custom_document_models={repr(self.custom_document_models)}, " \
               f"custom_neural_document_model_builds={repr(self.custom_neural_document_model_builds)})"

    @classmethod
    def _from_generated(cls, info):
        custom_neural_builds = info.custom_neural_document_model_builds \
            if hasattr(info, "custom_neural_document_model_builds") else None
        return cls(
            custom_document_models=CustomDocumentModelsDetails._from_generated(info.custom_document_models)
            if info.custom_document_models else None,
            custom_neural_document_model_builds=QuotaDetails._from_generated(custom_neural_builds)
            if custom_neural_builds else None,
        )

    def to_dict(self) -> Dict:
        """Returns a dict representation of ResourceDetails."""
        return {
                "custom_document_models": self.custom_document_models.to_dict()
                if self.custom_document_models
                else None,
                "custom_neural_document_model_builds": self.custom_neural_document_model_builds.to_dict()
                if self.custom_neural_document_model_builds
                else None,
            }

    @classmethod
    def from_dict(cls, data: Dict) -> "ResourceDetails":
        """Converts a dict in the shape of a ResourceDetails to the model itself.

        :param Dict data: A dictionary in the shape of ResourceDetails.
        :return: ResourceDetails
        :rtype: ResourceDetails
        """
        return cls(
            custom_document_models=CustomDocumentModelsDetails.from_dict(
                data.get("custom_document_models")  # type: ignore
            ) if data.get("custom_document_models") else None,
            custom_neural_document_model_builds=QuotaDetails.from_dict(
                data.get("custom_neural_document_model_builds")  # type: ignore
            ) if data.get("custom_neural_document_model_builds") else None,
        )


def _in_span(element: DocumentWord, spans: List[DocumentSpan]) -> bool:
    for span in spans:
        if element.span.offset >= span.offset and (
            element.span.offset + element.span.length
        ) <= (span.offset + span.length):
            return True
    return False
