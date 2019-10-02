#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import os
import json
import random
try:
    # python <= 2.7
    TYPE_TEXT_STRING = (str, unicode)  
except NameError: 
    TYPE_TEXT_STRING = (str, )
try:
    from unittest import mock
    from unittest.mock import Mock
except ImportError:
    # python < 3.3
    import mock
    from mock import Mock

from azure.core.exceptions import (
    HttpResponseError,
    ResourceNotFoundError,
    ClientAuthenticationError,
    ServiceResponseError
)
from azure.cognitiveservices.inkrecognizer import (
    InkStrokeKind,
    InkRecognitionUnitKind,
    ShapeKind,
    InkPointUnit,
    ApplicationKind,
    ServiceVersion
)
from azure.cognitiveservices.inkrecognizer import InkRecognizerClient
from azure.cognitiveservices.inkrecognizer import (
    Point,
    Rectangle,
    InkRecognitionUnit,
    InkBullet,
    InkDrawing,
    Line,
    Paragraph,
    InkWord,
    WritingRegion,
    ListItem,
    InkRecognitionRoot
)


RAISE_ONLINE_TEST_ERRORS = False
URL = ""
CREDENTIAL = Mock(name="FakeCredential", get_token="token")


def online_test(func):
    def wrapper(*args, **kw):
        if URL == "" or isinstance(CREDENTIAL, Mock):
            if RAISE_ONLINE_TEST_ERRORS:
                raise ValueError("Please fill URL and CREDENTIAL before running online tests.")
            else:
                return
        return func(*args, **kw)
    return wrapper


def fake_run(self, request, **kwargs):
    return Mock(http_response=(json.loads(request.data), kwargs["headers"], kwargs))


def pass_response(response, config):
    return response


def parse_result(result_filename):
    json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data", result_filename)
    client = InkRecognizerClient(URL, CREDENTIAL)
    with open(json_path, "r") as f:
        raw_recognition_result = f.read()
    response = Mock(status_code=200, headers={}, body=lambda: raw_recognition_result.encode("utf-8"))
    with mock.patch.object(client, "_send_request", lambda *args, **kw: response):
        root = client.recognize_ink([])
    return root


class TestClient:
    def test_set_azure_general_arguments(self):
        def pipeline_client_checker(base_url, transport, config):
            assert base_url == URL
            assert config.logging_policy.enable_http_logger is True
            assert config.retry_policy.total_retries == 3
            from azure.core.pipeline.transport import HttpTransport
            assert isinstance(transport, HttpTransport)

        def fake_pipeline_client_constructor(*args, **kw):
            pipeline_client_checker(kw["base_url"], kw["transport"], kw["config"])

        with mock.patch("azure.core.PipelineClient.__init__", fake_pipeline_client_constructor):
            InkRecognizerClient(URL, 
                                CREDENTIAL, 
                                logging_enable=True,
                                retry_total=3)


    def test_set_ink_recognizer_arguments(self):
        client = InkRecognizerClient(URL, 
                                     CREDENTIAL, 
                                     application_kind=ApplicationKind.DRAWING, 
                                     ink_point_unit=InkPointUnit.INCH,
                                     language="zh-cn",
                                     unit_multiple=2.5)

        with mock.patch.object(client, "_parse_result", pass_response):
            with mock.patch("azure.core.pipeline.Pipeline.run", fake_run):
                request_json, headers, kwargs = client.recognize_ink([])
                # check ink recognizer arguments
                assert request_json["applicationType"] == ApplicationKind.DRAWING.value
                assert request_json["unit"] == InkPointUnit.INCH.value
                assert request_json["language"] == "zh-cn"
                assert request_json["unitMultiple"] == 2.5

    def test_set_arguments_in_request(self):
        client = InkRecognizerClient(URL, 
                                     CREDENTIAL, 
                                     application_kind=ApplicationKind.DRAWING, 
                                     language="zh-cn")
        with mock.patch.object(client, "_parse_result", pass_response):
            with mock.patch("azure.core.pipeline.Pipeline.run", fake_run):
                request_json, headers, kwargs = client.recognize_ink(
                    [], 
                    application_kind=ApplicationKind.WRITING,
                    language = "en-gb",
                    client_request_id="random_id",
                    headers={"test_header": "test_header_result"},
                    timeout=10,
                    total_retries=5)
                
                # check ink recognizer arguments
                assert request_json["applicationType"] == ApplicationKind.WRITING.value
                assert request_json["language"] == "en-gb"
                # check azure general arguments
                assert headers["test_header"] == "test_header_result"
                assert headers["x-ms-client-request-id"] == "random_id"
                assert kwargs["connection_timeout"] == 10
                assert kwargs["total_retries"] == 5

    def test_consume_ink_stroke_list(self):
        point = Mock(x=0, y=0)
        stroke = Mock(id=0, points=[point], language="python", kind=InkStrokeKind.DRAWING)
        ink_stroke_list = [stroke] * 3
        client = InkRecognizerClient(URL, CREDENTIAL)
        with mock.patch.object(client, "_parse_result", pass_response):
            with mock.patch("azure.core.pipeline.Pipeline.run", fake_run):
                request_json, headers, kwargs = client.recognize_ink(ink_stroke_list)
                # check number of strokes, point values and other features
                assert len(request_json["strokes"]) == 3
                for s in request_json["strokes"]:
                    assert len(s["points"]) == 1
                    assert s["points"][0]["x"] == 0
                    assert s["points"][0]["y"] == 0
                    assert s["id"] == 0
                    assert s["language"] == "python"
                    assert s["kind"] == InkStrokeKind.DRAWING.value

    def test_parse_http_response(self):    
        client = InkRecognizerClient(URL, CREDENTIAL)

        # 401: ClientAuthenticationError
        response = Mock(status_code=401, headers={}, body=lambda: "HTTP STATUS: 401".encode("utf-8"))
        with mock.patch.object(client, "_send_request", lambda *args, **kw: response):
            try:
                root = client.recognize_ink([])
            except ClientAuthenticationError:
                pass  # expected
            else:
                raise AssertionError("Should raise ClientAuthenticationError here")

        # 404: ResourceNotFoundError
        response = Mock(status_code=404, headers={}, body=lambda: "HTTP STATUS: 404".encode("utf-8"))
        with mock.patch.object(client, "_send_request", lambda *args, **kw: response):
            try:
                root = client.recognize_ink([])
            except ResourceNotFoundError:
                pass  # expected
            else:
                raise AssertionError("Should raise ResourceNotFoundError here")

        # valid response from server
        json_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data", "hello_world_result.json")
        with open(json_path, "r") as f:
            recognition_json = f.read()

        response = Mock(status_code=200, headers={}, body=lambda: recognition_json.encode("utf-8"))
        with mock.patch.object(client, "_send_request", lambda *args, **kw: response):
            root = client.recognize_ink([])  # should pass. No need to check result.

        # invalid response from server
        jobj = json.loads(recognition_json)
        jobj["recognitionUnits"].append("random_string")
        invalid_recognition_json = json.dumps(jobj)
        response = Mock(status_code=200, headers={}, body=lambda: invalid_recognition_json.encode("utf-8"))
        with mock.patch.object(client, "_send_request", lambda *args, **kw: response):
            try:
                root = client.recognize_ink([])
            except ServiceResponseError:
                pass  # expected
            else:
                raise AssertionError("Should raise ServiceResponseError here")


class TestModels:
    def test_unit_ink_recognition_unit(self):
        root = parse_result("hello_world_result.json")
        units = root._units
        assert len(units) > 0 
        for unit in units:
            assert isinstance(unit.id, int)
            assert isinstance(unit.bounding_box, Rectangle)
            assert isinstance(unit.rotated_bounding_box, list)
            assert isinstance(unit.stroke_ids, list)
            assert isinstance(unit.children, list)
            assert isinstance(unit.parent, (InkRecognitionUnit, InkRecognitionRoot))
            for point in unit.rotated_bounding_box:
                assert isinstance(point, Point)
            for stroke_id in unit.stroke_ids:
                assert isinstance(stroke_id, int)
            for child in unit.children:
                assert isinstance(child, InkRecognitionUnit) 

    def test_unit_ink_bullet(self):
        root = parse_result("list_result.json")
        bullets = root.ink_bullets
        assert len(bullets) > 0
        for bullet in bullets:
            assert bullet.kind == InkRecognitionUnitKind.INK_BULLET
            assert isinstance(bullet.recognized_text, TYPE_TEXT_STRING)
            assert isinstance(bullet.parent, Line)
            assert len(bullet.children) == 0

    def test_unit_ink_drawing(self):
        root = parse_result("drawings_result.json")
        drawings = root.ink_drawings
        assert len(drawings) > 0 
        for drawing in drawings:
            assert drawing.kind == InkRecognitionUnitKind.INK_DRAWING
            assert isinstance(drawing.center, Point)
            assert isinstance(drawing.confidence, (int, float))
            assert isinstance(drawing.recognized_shape, ShapeKind)
            assert isinstance(drawing.rotated_angle, (int, float))
            assert isinstance(drawing.points, list)
            assert isinstance(drawing.alternates, list)
            for point in drawing.points:
                assert isinstance(point, Point)
            for alt in drawing.alternates:
                assert isinstance(alt, InkDrawing)
                assert alt.alternates == []
            assert isinstance(drawing.parent, InkRecognitionRoot)
            assert len(drawing.children) == 0
            
    def test_unit_line(self):
        root = parse_result("hello_world_result.json")
        lines = root.lines
        assert len(lines) > 0
        for line in lines:
            assert line.kind == InkRecognitionUnitKind.LINE
            assert isinstance(line.recognized_text, TYPE_TEXT_STRING)
            assert isinstance(line.alternates, list)
            for alt in line.alternates:
                assert isinstance(alt, TYPE_TEXT_STRING)
            assert isinstance(line.parent, (Paragraph, ListItem))
            for child in line.children:
                assert isinstance(child, (InkBullet, InkWord))

    def test_unit_paragraph(self):
        root = parse_result("list_result.json")
        paragraphs = root.paragraphs
        assert len(paragraphs) > 0
        for paragraph in paragraphs:
            assert paragraph.kind == InkRecognitionUnitKind.PARAGRAPH
            assert isinstance(paragraph.recognized_text, TYPE_TEXT_STRING)
            assert isinstance(paragraph.parent, WritingRegion)
            for child in paragraph.children:
                assert isinstance(child, (Line, ListItem))

    def test_unit_ink_word(self):
        root = parse_result("hello_world_result.json")
        words = root.ink_words
        assert len(words) > 0
        for word in words:
            assert word.kind == InkRecognitionUnitKind.INK_WORD
            assert isinstance(word.recognized_text, TYPE_TEXT_STRING)
            assert isinstance(word.alternates, list)
            for alt in word.alternates:
                assert isinstance(alt, TYPE_TEXT_STRING)
            assert isinstance(word.parent, Line)
            assert len(word.children) == 0

    def test_unit_writing_region(self):
        root = parse_result("list_result.json")
        writing_regions = root.writing_regions
        assert len(writing_regions) > 0
        for writing_region in writing_regions:
            assert writing_region.kind == InkRecognitionUnitKind.WRITING_REGION
            assert isinstance(writing_region.recognized_text, TYPE_TEXT_STRING)
            assert isinstance(writing_region.parent, InkRecognitionRoot)
            for child in writing_region.children:
                assert isinstance(child, Paragraph)

    def test_unit_list_item(self):
        root = parse_result("list_result.json")
        list_items = root.list_items
        assert len(list_items) > 0
        for list_item in list_items:
            assert list_item.kind == InkRecognitionUnitKind.LIST_ITEM
            assert isinstance(list_item.recognized_text, TYPE_TEXT_STRING)
            assert isinstance(list_item.parent, Paragraph)
            for child in list_item.children:
                assert isinstance(child, Line)


class TestSendRequests:
    @online_test
    def test_recognize_ink_with_empty_ink_stroke_list(self):
        client = InkRecognizerClient(URL, CREDENTIAL)
        root = client.recognize_ink([])

        words = root.ink_words
        assert not words
        drawings = root.ink_drawings
        assert not drawings
        bullets = root.ink_bullets
        assert not bullets

    @online_test
    def test_recognize_ink(self):
        points = []
        for i in range(10):
            points.append(Mock(x=i, y=i))
        stroke = Mock(id=i, points=points, language="en-US")
        ink_stroke_list = [stroke]
        client = InkRecognizerClient(URL, CREDENTIAL)
        root = client.recognize_ink(ink_stroke_list)

        words = root.ink_words
        drawings = root.ink_drawings
        bullets = root.ink_bullets
        assert len(words) + len(drawings) + len(bullets) > 0
