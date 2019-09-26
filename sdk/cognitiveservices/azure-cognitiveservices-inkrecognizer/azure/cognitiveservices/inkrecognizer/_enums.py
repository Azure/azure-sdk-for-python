#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from enum import Enum


class ApplicationKind(Enum):
    """
    The ApplicationKind enum allows an application to identify its domain
    (when it has one). Specifying a domain allows the application to
    inform the service of its contents.
    This can facilitate faster processing as the service will skip some
    classification steps. Applications that don't have a specific domain
    can simply specify ApplicationKind.MIXED, which is the default.
    """

    MIXED = "mixed"
    """ The application can have strokes of different kinds. """

    DRAWING = "drawing"
    """ The application can only have drawing strokes. """

    WRITING = "writing"
    """ The application can only have writing strokes. """


class InkStrokeKind(Enum):
    """
    The InkStrokeKind enum represents the class a stroke belongs too.
    The user of the Ink recognizer service is expected to set this value
    when it is known with absolute certainly. The default value is
    InkStrokeKind.UNKNOWN.
    """

    DRAWING = "inkDrawing"
    """ Specify the stroke is a drawing stroke. """

    WRITING = "inkWriting"
    """ Specify the stroke is a writing stroke. """

    UNKNOWN = "unknown"
    """ Use default stroke kind in ApplicationKind. If ApplicationKind set to
    Unknown, server will recognize the stroke kind. """


class InkPointUnit(Enum):
    """ The length unit passes to InkPoint. Default is InkPointUnit.MM. """

    MM = "mm"
    """"""

    CM = "cm"
    """"""

    INCH = "in"
    """"""


class InkRecognitionUnitKind(Enum):
    """
    The InkRecognitionUnitKind has all the different categories of recognition
    units available from the service.
    """

    UNKNOWN = "unknown"
    """
    Some stroke can't recognized by Ink Recognizer service.
    """

    INK_BULLET = "inkBullet"
    """
    A bullet on a line of text. The bullet can be associated with more than
    one line.
    """

    INK_WORD = "inkWord"
    """ A word which may have alternates, or an alternate of a word. """

    INK_DRAWING = "inkDrawing"
    """ A drawing which may have alternates, or an alternate of a drawing. """

    PARAGRAPH = "paragraph"
    """ A paragraph that contains multiple lines and / or lists. """

    LINE = "line"
    """
    A line, that contains a list of words, and may contain a bullet if it
    inside a list.
    """

    WRITING_REGION = "writingRegion"
    """
    A writing region is a part of the writing surface that contains words.
    """

    LIST_ITEM = "listItem"
    """
    One item of a list. It has only a line as its child, where a bullet should
    at the begining of that line.
    """


class ShapeKind(Enum):
    """
    The Shape enum represents different shapes that can be reported by the ink
    recognizer service. Any unrecognized shpae will be reported as
    ShapeKind.DRAWING.
    """

    BLOCK_ARROW = "blockArrow"
    """"""

    CIRCLE = "circle"
    """"""

    CLOUD = "cloud"
    """"""

    CURVE = "curve"
    """"""

    DIAMOND = "diamond"
    """"""

    DRAWING = "drawing"
    """"""

    ELLIPSE = "ellipse"
    """"""

    EQUILATERAL_TRIANGLE = "equilateralTriangle"
    """"""

    HEART = "heart"
    """"""

    HEXAGON = "hexagon"
    """"""

    ISOSCELES_TRIANGLE = "isoscelesTriangle"
    """"""

    LINE = "line"
    """"""

    PARALLELOGRAM = "parallelogram"
    """"""

    PENTAGON = "pentagon"
    """"""

    POLYLINE = "polyline"
    """"""

    QUADRILATERAL = "quadrilateral"
    """"""

    RECTANGLE = "rectangle"
    """"""

    RIGHT_TRIANGLE = "rightTriangle"
    """"""

    SQUARE = "square"
    """"""

    STAR_CROSSED = "starCrossed"
    """"""

    STAR_SIMPLE = "starSimple"
    """"""

    TRAPEZOID = "trapezoid"
    """"""

    TRIANGLE = "triangle"
    """"""


class ServiceVersion(Enum):
    """ Target version of Ink Recognizer service. """

    PREVIEW = "v1.0-preview"
    """ Preview service version. """

    def _to_string(self):
        _wrapper = {
            ServiceVersion.PREVIEW: "/v1.0-preview/recognize"
        }

        return _wrapper[self]
