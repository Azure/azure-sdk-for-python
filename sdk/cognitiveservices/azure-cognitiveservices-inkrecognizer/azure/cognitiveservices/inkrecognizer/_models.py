#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

from collections import OrderedDict
from ._enums import InkRecognitionUnitKind, ShapeKind


_STR_MAX_LENGTH = 1024


def _truncate(string):
    if len(string) > _STR_MAX_LENGTH:
        return string[:_STR_MAX_LENGTH] + "..."
    return string


class Point(object):
    """
    The Point class, unlike the IInkPoint interface, represents a single
    geometric position on a plane. The point is used to specify the center
    point of the bounding rectangle of a recognition unit and the key points
    of a well-formed recognized shape, i.e a beautified shape from Ink
    Recognizer Service based on the ink shape sent to it.
    """

    def __init__(self, x, y):
        self._x = x
        self._y = y

    @property
    def x(self):
        """ X-axis coordinate of the point. """
        return self._x

    @property
    def y(self):
        """ X-axis coordinate of the point. """
        return self._y


class Rectangle(object):
    """
    The class represents a rectangle used to identify the boundary of the
    strokes in a recognition unit.
    """

    def __init__(self, rect_dict):
        self._x = rect_dict["topX"]
        self._y = rect_dict["topY"]
        self._width = rect_dict["width"]
        self._height = rect_dict["height"]

    @property
    def x(self):
        """ X-axis coordinate of upperleft vertex. """
        return self._x

    @property
    def y(self):
        """ Y-axis coordinate of upperleft vertex. """
        return self._y

    @property
    def width(self):
        """ Width of the rectangle. """
        return self._width

    @property
    def height(self):
        """ Height of the rectangle. """
        return self._height


class InkRecognitionUnit(object):
    """
    An InkRecognitionUnit instance represents a single entity recognized by
    the Ink Recognizer Service.
    """

    _ink_recognition_unit_kind = InkRecognitionUnitKind.UNKNOWN

    def __init__(self, json_object):
        self._id = json_object["id"]
        self._bounding_box = Rectangle(json_object["boundingRectangle"])
        self._rotated_bounding_box = [
            Point(point["x"], point["y"])
            for point in json_object["rotatedBoundingRectangle"]
        ]
        self._stroke_ids = json_object["strokeIds"]
        self._child_ids = json_object.get("childIds", [])
        self._parent_id = json_object["parentId"]
        self._children = []
        self._parent = None

    def __str__(self):
        return _truncate("%s id=%s strokes=%s" % (
            type(self), self._id, self._stroke_ids))

    __repr__ = __str__

    @property
    def bounding_box(self):
        # type: () -> Rectangle
        """
        The bounding box is the rectangular area that contains all the strokes
        in a recognition unit.

        :rtype: Rectangle
        """
        return self._bounding_box

    @property
    def rotated_bounding_box(self):
        # type () -> List[Point]
        """
        The rotated bounding box is the oriented rectangular area that
        contains all the strokes in a recognition unit.
        Its shape is influenced by the detected orientation of the ink in the
        recognition unit.
        It is represented by a list of Points which are the vertices of the
        rect, clockwise.

        :rtype: List[Point]
        """
        return self._rotated_bounding_box

    @property
    def id(self):
        # type: () -> int
        """
        Unique identifier for the recognition unit.

        rtype: int
        """
        return self._id

    @property
    def kind(self):
        # type: () -> InkRecognitionUnitKind
        """
        The kind of the current recognition unit.

        :rtype: InkRecognitionUnitKind
        """
        return self._ink_recognition_unit_kind

    @property
    def stroke_ids(self):
        # type: () -> List[int]
        """
        Id of strokes of this unit.

        :rtype: List[int]
        """
        return self._stroke_ids

    @property
    def children(self):
        # type: () -> List[InkRecognitionUnit]
        """
        The children of a recognition unit represent the units contained in a
        container unit.
        An example is the relationship between a line and the words on the
        line. The children of the line is a list of words. "Leaf" units like
        words which have no children will always return an empty list.

        :rtype: List[InkRecognitionUnit]
        """
        return self._children

    @property
    def parent(self):
        # type: () -> InkRecognitionUnit
        """
        The parent of a recognition unit represent the unit containing this
        unit.
        An example is the relationship between a line and the words on the
        line. The line is the parent of the words. The top level recognition
        unit will return None as the parent.

        :rtype: InkRecognitionUnit or None
        """
        return self._parent


class InkBullet(InkRecognitionUnit):
    """
    An InkBullet instance represents the collection of one or more ink strokes
    that were recognized as a bullet point on a line.
    """

    _ink_recognition_unit_kind = InkRecognitionUnitKind.INK_BULLET

    def __init__(self, json_object):
        InkRecognitionUnit.__init__(self, json_object)
        self._recognized_text = json_object.get("recognizedText", "")

    @property
    def recognized_text(self):
        # type: () -> str
        """
        The recognized string of the bullet, e.g. '*'. If the bullet isn't
        recognized as a string (e.g. when the bullet is a complex shape), an
        empty string is returned.

        :rtype: str
        """

        return self._recognized_text


class InkWord(InkRecognitionUnit):
    """
    An InkWord instance represents the collection of one or more ink strokes
    that were recognized as a word.
    """

    _ink_recognition_unit_kind = InkRecognitionUnitKind.INK_WORD

    def __init__(self, json_object):
        InkRecognitionUnit.__init__(self, json_object)
        self._recognized_text = json_object.get("recognizedText", "")
        self._alternates = self._parse_alternates(json_object)

    def __str__(self):
        return _truncate("%s id=%s text='%s' strokes=%s" % (
            type(self), self._id, self.recognized_text, self._stroke_ids))

    def _parse_alternates(self, json_object):  # pylint:disable=no-self-use
        return [json_alternate.get("recognizedString", "")
                for json_alternate in json_object.get("alternates", [])]

    @property
    def alternates(self):
        # type: () -> List[str]
        """
        A list of alternate strings reported by the service.

        :rtype: List[str]
        """

        return self._alternates

    @property
    def recognized_text(self):
        # type: () -> str
        """
        The recognized string of the word. If the word isn't
        recognized, an empty string is returned.

        :rtype: str
        """

        return self._recognized_text


class InkDrawing(InkRecognitionUnit):
    """
    An InkDrawing instance represents the collection of one or more ink strokes
    that were recognized as a drawing/shape.
    """
    _ink_recognition_unit_kind = InkRecognitionUnitKind.INK_DRAWING

    def __init__(self, json_object):
        InkRecognitionUnit.__init__(self, json_object)
        self._center = self._parse_center(json_object.get("center", None))
        self._confidence = json_object["confidence"]
        self._recognized_shape = self._parse_shape(json_object["recognizedObject"])
        self._rotated_angle = json_object["rotationAngle"]
        self._points = self._parse_points(json_object.get("points", []))
        self._alternates = self._parse_alternates(json_object)

    def __str__(self):
        return _truncate("%s id=%s shape='%s' strokes=%s" % (
            type(self), self._id, self.recognized_shape, self._stroke_ids))

    def _parse_center(self, center):  # pylint:disable=no-self-use, inconsistent-return-statements
        if center is None:
            return
        return Point(center["x"], center["y"])

    def _parse_shape(self, shape_string):  # pylint:disable=no-self-use
        try:
            shape = ShapeKind(shape_string)
        except ValueError:
            raise ValueError("Unexpected shape from server: %s." % shape_string)
        return shape

    def _parse_points(self, points):  # pylint:disable=no-self-use
        return [Point(point["x"], point["y"]) for point in points]

    def _parse_one_alternate(self, json_object, json_alternate):  # pylint:disable=no-self-use
        kind = json_alternate.get("category")
        if kind != InkRecognitionUnitKind.INK_DRAWING.value:
            raise ValueError("Unexpected InkDrawing alternate kind: %s" % kind)
        json_object_alternate = json_object.copy()
        json_object_alternate["confidence"] = json_alternate["confidence"]
        json_object_alternate["recognizedObject"] = json_alternate["recognizedString"]
        json_object_alternate["rotationAngle"] = json_alternate["rotationAngle"]
        json_object_alternate["points"] = json_alternate.get("points", [])
        json_object_alternate["alternates"] = []
        return InkDrawing(json_object_alternate)


    def _parse_alternates(self, json_object):
        return [self._parse_one_alternate(json_object, json_alternate)
                for json_alternate in json_object.get("alternates", [])]

    @property
    def center(self):
        # type: () -> Point
        """
        The center point of the bounding box of the recognition
        unit as Point.

        :rtype: Point
        """

        return self._center

    @property
    def confidence(self):
        # type: () -> float
        """
        A number between 0 and 1 which indicates the confidence level
        in the result.

        :rtype: float
        """

        return self._confidence

    @property
    def recognized_shape(self):
        # type: () -> ShapeKind
        """
        The ShapeKind enum representing the geometric shape that was
        recognized. If the drawing isn't one of the known geometric shapes,
        an ShapeKind.DRAWING is returned.

        :rtype: ShapeKind
        """

        return self._recognized_shape

    @property
    def rotated_angle(self):
        # type: () -> float
        """
        The angular orientation of an object relative to the horizontal axis.

        :rtype: float
        """

        return self._rotated_angle

    @property
    def points(self):
        # type: () -> List[Point]
        """
        A list of Point instances that represent points that are relevant to
        the type of recognition unit. For example, for a leaf node of inkDrawing
        kind that represents a triangle, points would include the x,y
        coordinates of the vertices of the recognized triangle. The points
        represent the coordinates of points used to create the perfectly drawn
        shape that is closest to the original input. They may not exactly match.

        :rtype: List[Point]
        """

        return self._points

    @property
    def alternates(self):
        # type: () -> List[InkDrawing]
        """
        A list of alternate InkDrawings when the confidence isn't 1.
        If this InkDrawing is an alternate, returns None.

        :rtype: List[InkDrawing] or None
        """

        return self._alternates


class Line(InkRecognitionUnit):
    """
    A Line instance represents the collection of one or more ink strokes that
    were recognized as a line.
    """
    _ink_recognition_unit_kind = InkRecognitionUnitKind.LINE

    def __init__(self, json_object):
        InkRecognitionUnit.__init__(self, json_object)
        self._recognized_text = json_object.get("recognizedText", "")
        self._alternates = self._parse_alternates(json_object.get("alternates", []))

    def _parse_alternates(self, alternates):  # pylint:disable=no-self-use
        return [alternate["recognizedString"] for alternate in alternates]

    @property
    def alternates(self):
        # type: () -> List[str]
        """
        A list of alternate strings reported by the service.

        :rtype: List[str]
        """
        return self._alternates

    @property
    def recognized_text(self):
        # type: () -> str
        """
        The recognized string of the line. If the words in the line are not
        recognized, an empty string is returned.

        :rtype: str
        """
        return self._recognized_text

    @property
    def bullet(self):
        # type: () -> Optional[InkBullet, None]
        """
        If the line has a bullet, return it as InkBullet. Otherwise, return None.
        One line can have at most one bullet.

        :rtype: InkBullet or None
        """

        for unit in self.children:
            if unit.kind == InkRecognitionUnitKind.INK_BULLET:
                return unit
        return None

    @property
    def words(self):
        # type: () -> List[InkWord]
        """ All the words in this line.

        :rtype: List[InkWord]
        """
        return [unit for unit in self.children if unit.kind == InkRecognitionUnitKind.INK_WORD]


class Paragraph(InkRecognitionUnit):
    """
    A Paragraph instance represents the collection of one or more ink strokes
    that were recognized as a paragraph.
    """
    _ink_recognition_unit_kind = InkRecognitionUnitKind.PARAGRAPH

    @property
    def recognized_text(self):
        # type: () -> str
        """
        The recognized string of the paragraph. If the words in the paragraph
        are not recognized, an empty string is returned.

        :rtype: str
        """
        return "\n".join([child.recognized_text
                          for child in self.children])

    @property
    def lines(self):
        # type: () -> List[Line]
        """
        All the lines in the paragraph.

        :rtype: List[Line]
        """
        return [unit for unit in self.children
                if unit.kind == InkRecognitionUnitKind.LINE]

    @property
    def list_items(self):
        # type: () -> List[ListItem]
        """
        All the ListItems in the paragraph.
        """

        return [unit for unit in self.children
                if unit.kind == InkRecognitionUnitKind.LIST_ITEM]


class WritingRegion(InkRecognitionUnit):
    """
    A WritingRegion instance represents a certain part of a writing surface that the
    user has written at least one word on. WritingRegions are the top-level writing
    objects under an InkRecognitionRoot.
    """
    _ink_recognition_unit_kind = InkRecognitionUnitKind.WRITING_REGION

    @property
    def recognized_text(self):
        # type: () -> str
        """
        The recognized string of the writing region. If the words in the writing
        region are not recognized, an empty string is returned.

        :rtype: str
        """
        return "\n".join([child.recognized_text
                          for child in self.children])

    @property
    def paragraphs(self):
        # type: () -> List[Paragraph]
        """
        All paragraphs in the writing region.

        :rtype: List[Paragraph]
        """
        return self.children


class ListItem(InkRecognitionUnit):
    """
    A ListItem instance represents an item of a list. It has a line which has
    a bullet at the beginning of it.
    The list that this ListItem belongs to is not given by Ink Recognizer Service.
    """
    _ink_recognition_unit_kind = InkRecognitionUnitKind.LIST_ITEM

    @property
    def recognized_text(self):
        # type: () -> str
        """
        The recognized string of the list item. If the words in the list
        item are not recognized, an empty string is returned.

        :rtype: str
        """
        return "\n".join([child.recognized_text
                          for child in self.children])

    @property
    def lines(self):
        # type: () -> List[Line]
        """
        All the lines in the list item (Should be only one).

        :rtype: List[Line]
        """
        return self.children


class InkRecognitionRoot(object):
    """
    An InkRecognitionRoot instance is the return type from the recognize_ink method in
    InkRecognizerClient. It is the root of the of recognition unit tree.
    It also contains the HTTP request status code of the recognition request.
    WritingRegions and Shapes are the only top-level objects under an InkRecognitionRoot.
    """

    def __init__(self, units):
        self._units = units
        self._unit_kind_map = {}
        for unit in units:
            if unit.kind in [InkRecognitionUnitKind.INK_DRAWING,
                             InkRecognitionUnitKind.WRITING_REGION]:
                unit._parent = self  # pylint:disable=protected-access

    def _get_recognition_units(self, unit_kind):
        if unit_kind in self._unit_kind_map:
            return self._unit_kind_map[unit_kind]
        if not isinstance(unit_kind, InkRecognitionUnitKind):
            raise ValueError("Expected a InkRecognitionUnitKind instance, got %s" % type(unit_kind))

        self._unit_kind_map[unit_kind] = [unit for unit in self._units if unit.kind == unit_kind]
        return self._unit_kind_map[unit_kind]

    @property
    def ink_words(self):
        # type: () -> List[InkWord]
        """
        The list of all InkWord found in the tree returned by the Ink Recognizer Service.

        :rtype: List[InkWord]
        """

        return self._get_recognition_units(InkRecognitionUnitKind.INK_WORD)

    @property
    def ink_drawings(self):
        # type: () -> List[InkDrawing]
        """
        The list of all InkDrawing found in the tree returned by the Ink Recognizer Service.

        :rtype: List[InkDrawing]
        """

        return self._get_recognition_units(InkRecognitionUnitKind.INK_DRAWING)

    @property
    def lines(self):
        # type: () -> List[Line]
        """
        The list of all Lines found in the tree returned by the Ink Recognizer Service.

        :rtype: List[Line]
        """

        return self._get_recognition_units(InkRecognitionUnitKind.LINE)

    @property
    def ink_bullets(self):
        # type: () -> List[InkBullet]
        """
        The list of all InkBullets found in the tree returned by the Ink Recognizer Service.

        :rtype: List[InkBullet]
        """

        return self._get_recognition_units(InkRecognitionUnitKind.INK_BULLET)

    @property
    def paragraphs(self):
        # type: () -> List[Paragraph]
        """
        The list of all Paragraphs found in the tree returned by the Ink Recognizer Service.

        :rtype: List[Paragraph]
        """

        return self._get_recognition_units(InkRecognitionUnitKind.PARAGRAPH)

    @property
    def writing_regions(self):
        # type: () -> List[WritingRegion]
        """
        The list of all WritingRegions found in the tree returned by the Ink Recognizer Service.

        :rtype: List[WritingRegion]
        """

        return self._get_recognition_units(InkRecognitionUnitKind.WRITING_REGION)

    @property
    def list_items(self):
        # type: () -> List[ListItem]
        """
        The list of all ListItems found in the tree returned by the Ink Recognizer Service.

        :rtype: List[ListItem]
        """

        return self._get_recognition_units(InkRecognitionUnitKind.LIST_ITEM)

    def find_word(self, word):
        # type: (str) -> List[InkWord]
        """
        Returns all Inkwords returned by the Ink Recognizer Service whose
        recognized text is exactly the same as the given string. This is
        case insensitive.

        :param str word: word to find.

        :param bool case_sensitive: case sensitive or not. Default is True.

        :rtype: List[InkWord]
        """
        if not isinstance(word, str):
            raise ValueError("Expected a string, got %s" % type(word))

        word_lower = word.lower()
        return [ink_word for ink_word in self.ink_words
                if ink_word.recognized_text.lower() == word_lower]


_RECOGNITION_UNIT_MAP = {
    InkRecognitionUnitKind.UNKNOWN.value          : InkRecognitionUnit,
    InkRecognitionUnitKind.INK_BULLET.value       : InkBullet,
    InkRecognitionUnitKind.INK_WORD.value         : InkWord,
    InkRecognitionUnitKind.INK_DRAWING.value      : InkDrawing,
    InkRecognitionUnitKind.PARAGRAPH.value        : Paragraph,
    InkRecognitionUnitKind.LINE.value             : Line,
    InkRecognitionUnitKind.WRITING_REGION.value   : WritingRegion,
    InkRecognitionUnitKind.LIST_ITEM.value        : ListItem
}


def _parse_one_recognition_unit(json_object):
    # find the proper class for the unit and parse it.
    kind = json_object["category"]
    if kind in _RECOGNITION_UNIT_MAP:
        return _RECOGNITION_UNIT_MAP[kind](json_object)
    # return base class
    return InkRecognitionUnit(json_object)


def _parse_recognition_units(content_json):
    # parse raw result into InkRecognitionUnit tree
    units = OrderedDict()
    recognition_unit_list = content_json.get("recognitionUnits", [])
    # parse all units in json response into InkRecognitionUnit
    for json_object in recognition_unit_list:
        unit = _parse_one_recognition_unit(json_object)
        units[unit.id] = unit

    # set children and parent for each unit
    for unit in units.values():
        unit._children = [units[child_id] for child_id in unit._child_ids]  # pylint:disable=protected-access
        unit._parent = units.get(unit._parent_id, None)  # pylint:disable=protected-access

    root = InkRecognitionRoot(units.values())
    return root
