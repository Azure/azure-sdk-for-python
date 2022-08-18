# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

import re
from azure.core.credentials import AzureKeyCredential
from azure.core.pipeline.policies import AzureKeyCredentialPolicy, SansIOHTTPPolicy
from azure.core.pipeline.transport import HttpTransport
from azure.core.exceptions import HttpResponseError


POLLING_INTERVAL = 5
COGNITIVE_KEY_HEADER = "Ocp-Apim-Subscription-Key"


def _get_deserialize(api_version):
    if api_version == "2.0":
        from ._generated.v2_0 import FormRecognizerClient
    elif api_version == "2.1":
        from ._generated.v2_1 import FormRecognizerClient
    elif api_version == "2022-06-30-preview":
        from ._generated.v2022_06_30_preview import FormRecognizerClient
    return FormRecognizerClient("dummy", "dummy")._deserialize  # pylint: disable=protected-access


def get_element_type(element_pointer):
    word_ref = re.compile(r"/readResults/\d+/lines/\d+/words/\d+")
    if re.search(word_ref, element_pointer):
        return "word"

    line_ref = re.compile(r"/readResults/\d+/lines/\d+")
    if re.search(line_ref, element_pointer):
        return "line"

    selection_mark_ref = re.compile(r"/readResults/\d+/selectionMarks/\d+")
    if re.search(selection_mark_ref, element_pointer):
        return "selectionMark"

    return None


def get_element(element_pointer, read_result):
    indices = [int(s) for s in re.findall(r"\d+", element_pointer)]
    read = indices[0]

    if get_element_type(element_pointer) == "word":
        line = indices[1]
        word = indices[2]
        ocr_word = read_result[read].lines[line].words[word]
        return "word", ocr_word, read + 1

    if get_element_type(element_pointer) == "line":
        line = indices[1]
        ocr_line = read_result[read].lines[line]
        return "line", ocr_line, read + 1

    if get_element_type(element_pointer) == "selectionMark":
        mark = indices[1]
        selection_mark = read_result[read].selection_marks[mark]
        return "selectionMark", selection_mark, read + 1

    return None, None, None


def adjust_value_type(value_type):
    if value_type == "array":
        value_type = "list"
    if value_type == "number":
        value_type = "float"
    if value_type == "object":
        value_type = "dictionary"
    return value_type


def adjust_confidence(score):
    """Adjust confidence when not returned."""
    if score is None:
        return 1.0
    return score


def adjust_text_angle(text_angle):
    """Adjust to (-180, 180]"""
    if text_angle > 180:
        text_angle -= 360
    return text_angle


def get_authentication_policy(credential):
    authentication_policy = None
    if credential is None:
        raise ValueError("Parameter 'credential' must not be None.")
    if isinstance(credential, AzureKeyCredential):
        authentication_policy = AzureKeyCredentialPolicy(name=COGNITIVE_KEY_HEADER, credential=credential)
    elif credential is not None and not hasattr(credential, "get_token"):
        raise TypeError(
            "Unsupported credential: {}. Use an instance of AzureKeyCredential "
            "or a token credential from azure.identity".format(type(credential))
        )

    return authentication_policy


def get_content_type(form):
    """Source: https://en.wikipedia.org/wiki/Magic_number_(programming)#Magic_numbers_in_files"""

    if isinstance(form, bytes):
        return check_beginning_bytes(form)

    if hasattr(form, "read") and hasattr(form, "seek"):
        beginning_bytes = form.read(4)
        form.seek(0)
        return check_beginning_bytes(beginning_bytes)

    raise ValueError(
        "Content type could not be auto-detected because the stream was not readable/seekable. "
        "Please pass the content_type keyword argument."
    )


def check_beginning_bytes(form):

    if len(form) > 3:
        if form[:4] == b"\x25\x50\x44\x46":
            return "application/pdf"
        if form[:2] == b"\xff\xd8":
            return "image/jpeg"
        if form[:4] == b"\x89\x50\x4E\x47":
            return "image/png"
        if form[:4] == b"\x49\x49\x2A\x00":  # little-endian
            return "image/tiff"
        if form[:4] == b"\x4D\x4D\x00\x2A":  # big-endian
            return "image/tiff"
        if form[:2] == b"\x42\x4D":
            return "image/bmp"
    raise ValueError("Content type could not be auto-detected. Please pass the content_type keyword argument.")


class TransportWrapper(HttpTransport):
    """Wrapper class that ensures that an inner client created
    by a `get_client` method does not close the outer transport for the parent
    when used in a context manager.
    """

    def __init__(self, transport):
        self._transport = transport

    def send(self, request, **kwargs):
        return self._transport.send(request, **kwargs)

    def open(self):
        pass

    def close(self):
        pass

    def __enter__(self):
        pass

    def __exit__(self, *args):  # pylint: disable=arguments-differ
        pass


class QuotaExceededPolicy(SansIOHTTPPolicy):
    """Raises an exception immediately when the call quota volume has been exceeded in a F0
    tier form recognizer resource. This is to avoid waiting the Retry-After time returned in
    the response.
    """

    def on_response(self, request, response):
        """Is executed after the request comes back from the policy.

        :param request: Request to be modified after returning from the policy.
        :type request: ~azure.core.pipeline.PipelineRequest
        :param response: Pipeline response object
        :type response: ~azure.core.pipeline.PipelineResponse
        """
        http_response = response.http_response
        if (
            http_response.status_code in [403, 429]
            and "Out of call volume quota for FormRecognizer F0 pricing tier" in http_response.text()
        ):
            raise HttpResponseError(http_response.text(), response=http_response)
