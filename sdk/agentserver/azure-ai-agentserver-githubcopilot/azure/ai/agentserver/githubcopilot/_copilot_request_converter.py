# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import base64
import mimetypes
import os
import tempfile
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple, Union

from azure.ai.agentserver.core.models import CreateResponse

# MIME type -> preferred file extension (mimetypes can return unusual choices)
_MIME_EXT_OVERRIDES: Dict[str, str] = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
    "image/bmp": ".bmp",
    "image/tiff": ".tiff",
    "text/plain": ".txt",
    "text/csv": ".csv",
    "application/pdf": ".pdf",
    "application/json": ".json",
}


@dataclass
class ConvertedAttachments:
    """Attachments ready to pass to ``MessageOptions``, plus temporary files.

    Pass :attr:`attachments` directly to ``MessageOptions(attachments=...)``.
    Call :meth:`cleanup` (ideally in a ``finally`` block) to delete any
    temporary files that were created while materialising base64-encoded
    content parts onto disk.

    Usage::

        converted = converter.convert_attachments()
        try:
            await session.send(MessageOptions(prompt=prompt, attachments=converted.attachments))
        finally:
            converted.cleanup()
    """

    attachments: List[Any]
    _temp_paths: List[str] = field(default_factory=list)

    def cleanup(self) -> None:
        """Delete any temporary files created for this set of attachments."""
        for p in list(self._temp_paths):
            try:
                os.unlink(p)
            except OSError:
                pass
        self._temp_paths.clear()

    def __bool__(self) -> bool:
        return bool(self.attachments)


class CopilotRequestConverter:
    """Converts an AgentRunContext request into a prompt string for the Copilot SDK."""

    def __init__(self, request: CreateResponse):
        self._request = request

    def convert(self) -> str:
        """Extract a prompt string from the incoming CreateResponse request.

        Handles several input shapes:

        - ``str``: returned as-is
        - ``list[dict]``: messages are concatenated in order
        - ``dict`` with ``content`` key: treated as a single implicit user message

        For ``input_image`` content parts that carry an external HTTP/HTTPS URL,
        a short ``[image: <url>]`` annotation is appended so the model at least
        knows an image was supplied.  Images sent as base64 data URIs, and files
        sent via ``file_data``, produce no annotation here -- their content is
        materialised onto disk by :meth:`convert_attachments` and passed as
        SDK ``FileAttachment`` objects instead.

        :return: The extracted prompt string.
        :rtype: str
        """
        raw_input = self._request.get("input")
        if raw_input is None:
            return ""
        if isinstance(raw_input, str):
            return raw_input
        if isinstance(raw_input, list):
            return self._convert_message_list(raw_input)
        if isinstance(raw_input, dict):
            return self._extract_content(raw_input)
        raise ValueError(f"Unsupported input type: {type(raw_input)}")

    def convert_attachments(self) -> ConvertedAttachments:
        """Extract file and image attachments from the request's content parts.

        Scans all messages in ``input`` for ``input_file`` and ``input_image``
        content parts and materialises their data onto disk as temporary files,
        returning :class:`ConvertedAttachments` with Copilot SDK
        ``FileAttachment`` dicts and a list of temp paths to clean up.

        Supported cases:

        ``input_file`` with ``file_data`` (base64)
            Decoded and written to a temp file.  The ``filename`` field is used
            to infer the file extension when present.

        ``input_image`` with a ``data:`` URI
            Decoded and written to a temp file with the appropriate image
            extension (e.g. ``.jpg``, ``.png``).

        ``input_file`` with only a ``file_id`` (no ``file_data``)
            Cannot be materialised here -- skipped.  The converter includes a
            ``[file: <id>]`` annotation in the text prompt instead.

        ``input_image`` with an external ``http``/``https`` URL
            Cannot be downloaded here -- skipped.  The URL is included as
            ``[image: <url>]`` in the text prompt by :meth:`convert`.

        :return: :class:`ConvertedAttachments` ready for ``MessageOptions``.
        :rtype: ConvertedAttachments
        """
        attachments: List[Any] = []
        temp_paths: List[str] = []

        raw_input = self._request.get("input")
        if not raw_input:
            return ConvertedAttachments(attachments=attachments)

        messages: List[Any] = [raw_input] if isinstance(raw_input, (str, dict)) else list(raw_input)

        for msg in messages:
            if isinstance(msg, str):
                continue
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue
            for part in content:
                if not isinstance(part, dict):
                    continue
                part_type = part.get("type")
                if part_type == "input_file":
                    att, tmp = self._handle_input_file(part)
                elif part_type == "input_image":
                    att, tmp = self._handle_input_image(part)
                else:
                    continue
                if att is not None:
                    attachments.append(att)
                if tmp is not None:
                    temp_paths.append(tmp)

        return ConvertedAttachments(attachments=attachments, _temp_paths=temp_paths)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _convert_message_list(self, messages: List[Dict[str, Any]]) -> str:
        """Flatten a list of message dicts into a single prompt string."""
        parts: List[str] = []
        for msg in messages:
            content = self._extract_content(msg)
            if content:
                parts.append(content)
        return "\n".join(parts)

    @staticmethod
    def _extract_content(msg: Union[Dict[str, Any], str]) -> str:
        """Pull the text content out of a single message dict or string.

        Non-text content parts are handled as follows:

        * ``input_text`` -- text extracted normally.
        * ``input_image`` with external URL -- annotated as ``[image: <url>]``.
        * ``input_image`` with data URI -- omitted (passed as attachment).
        * ``input_image`` with ``file_id`` -- annotated as ``[image file: <id>]``.
        * ``input_file`` with ``file_id`` only -- annotated as ``[file: <name>]``.
        * ``input_file`` with ``file_data`` -- omitted (passed as attachment).
        """
        if isinstance(msg, str):
            return msg
        content = msg.get("content", "")
        if isinstance(content, str):
            return content
        # content may be a list of content parts
        if isinstance(content, list):
            text_parts: List[str] = []
            for part in content:
                if isinstance(part, str):
                    text_parts.append(part)
                    continue
                if not isinstance(part, dict):
                    continue
                part_type = part.get("type")

                if part_type == "input_text" or part_type is None:
                    text = part.get("text")
                    if text:
                        text_parts.append(str(text))

                elif part_type == "input_image":
                    # Resolve URL -- may be nested dict or plain string
                    image_url_obj = part.get("image_url")
                    if isinstance(image_url_obj, dict):
                        url = image_url_obj.get("url", "")
                    elif isinstance(image_url_obj, str):
                        url = image_url_obj
                    else:
                        url = ""

                    if url and not url.startswith("data:"):
                        # External URL -- include as an annotation in the prompt
                        text_parts.append(f"[image: {url}]")
                    elif not url:
                        file_id = part.get("file_id")
                        if file_id:
                            text_parts.append(f"[image file: {file_id}]")
                    # data: URIs are skipped -- content materialised as attachment

                elif part_type == "input_file":
                    # Only annotate when there is no file_data (that gets materialised)
                    if not part.get("file_data"):
                        name = part.get("filename") or part.get("file_id") or "file"
                        text_parts.append(f"[file: {name}]")

            return " ".join(text_parts)
        return str(content) if content else ""

    # ------------------------------------------------------------------
    # Attachment materialisation helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _handle_input_file(part: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[str]]:
        """Materialise an ``input_file`` content part onto disk.

        Returns ``(FileAttachment | None, temp_path | None)``.
        """
        file_data: Optional[str] = part.get("file_data")
        filename: str = part.get("filename") or "attachment"

        if not file_data:
            # file_id only -- we cannot fetch the bytes here; annotate in text instead
            return None, None

        suffix = os.path.splitext(filename)[1] or ".bin"
        try:
            data = base64.b64decode(file_data)
        except Exception:
            return None, None

        fd, tmp_path = tempfile.mkstemp(suffix=suffix, prefix="copilot_file_")
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            return None, None

        att: Dict[str, Any] = {"type": "file", "path": tmp_path, "displayName": filename}
        return att, tmp_path

    @staticmethod
    def _handle_input_image(part: Dict[str, Any]) -> Tuple[Optional[Dict], Optional[str]]:
        """Materialise an ``input_image`` content part onto disk.

        Returns ``(FileAttachment | None, temp_path | None)``.
        Only base64 data URIs (``data:<mime>;base64,<data>``) are handled.
        External HTTP/HTTPS URLs cannot be fetched and are skipped.
        """
        image_url_obj = part.get("image_url")
        if isinstance(image_url_obj, dict):
            url: str = image_url_obj.get("url", "")
        elif isinstance(image_url_obj, str):
            url = image_url_obj
        else:
            return None, None

        if not url.startswith("data:"):
            # External URL -- cannot download here; annotated in prompt text instead
            return None, None

        # Parse: data:<mime>;base64,<encoded>
        try:
            header, encoded = url.split(",", 1)
            mime = header.split(":")[1].split(";")[0]
            ext = _MIME_EXT_OVERRIDES.get(mime) or (mimetypes.guess_extension(mime) or ".bin")
            data = base64.b64decode(encoded)
        except Exception:
            return None, None

        fd, tmp_path = tempfile.mkstemp(suffix=ext, prefix="copilot_img_")
        try:
            with os.fdopen(fd, "wb") as fh:
                fh.write(data)
        except Exception:
            try:
                os.unlink(tmp_path)
            except OSError:
                pass
            return None, None

        att: Dict[str, Any] = {"type": "file", "path": tmp_path, "displayName": f"image{ext}"}
        return att, tmp_path
