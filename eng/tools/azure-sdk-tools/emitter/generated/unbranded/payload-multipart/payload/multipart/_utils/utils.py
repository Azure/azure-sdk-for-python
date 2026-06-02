import json
import os
from typing import Any, IO, Mapping, Optional, Union

from .._utils.model_base import Model, SdkJSONEncoder


# file-like tuple could be `(filename, IO (or bytes))` or `(filename, IO (or bytes), content_type)`
FileContent = Union[str, bytes, IO[str], IO[bytes]]

FileType = Union[
    # file (or bytes)
    FileContent,
    # (filename, file (or bytes))
    tuple[Optional[str], FileContent],
    # (filename, file (or bytes), content_type)
    tuple[Optional[str], FileContent, Optional[str]],
]


def serialize_multipart_data_entry(data_entry: Any) -> Any:
    if isinstance(data_entry, (list, tuple, dict, Model)):
        return json.dumps(data_entry, cls=SdkJSONEncoder, exclude_readonly=True)
    return data_entry


def _normalize_multipart_file_entry(field_name: str, entry: Any, index: int) -> Any:
    """Ensure a multipart file entry carries a filename for Content-Disposition.

    Servers distinguish file parts from plain form fields by the presence of
    ``filename=`` in the ``Content-Disposition`` header.  When callers pass
    bare bytes/str/IO the HTTP client omits the filename and the server may
    reject the upload.  This helper wraps bare values into a (filename, content)
    tuple, deriving the name from IO.name when available.

    :param str field_name: The multipart field name used as a filename fallback.
    :param entry: The user-provided file entry (tuple, bytes, str, or IO).
    :type entry: any
    :param int index: The positional index of the entry within the field, used
        to disambiguate fallback filenames when multiple entries are provided.
    :return: Either the original tuple entry, or a ``(filename, content)`` tuple
        wrapping the bare value.
    :rtype: any
    """
    if isinstance(entry, tuple):
        return entry
    filename: Optional[str] = None
    name_attr = getattr(entry, "name", None)
    if isinstance(name_attr, str) and name_attr:
        filename = os.path.basename(name_attr)
    if not filename:
        filename = f"{field_name}_{index}" if index else field_name

    # Return a 3-tuple with an explicit "application/octet-stream" content type.
    # A 2-tuple (filename, content) would leave the part's Content-Type unset, and
    # the sdk core library only defaults to "application/octet-stream" for bare
    # (non-tuple) values - a tuple bypasses that default and falls back to the
    # HTTP "text/plain" default instead. Setting it explicitly preserves the
    # pre-existing behavior for bare bytes/IO across all transports.
    return (filename, entry, "application/octet-stream")


def prepare_multipart_form_data(
    body: Mapping[str, Any], multipart_fields: list[str], data_fields: list[str]
) -> list[FileType]:
    files: list[FileType] = []

    # Data fields first so streaming server-side parsers see metadata before
    # binary file parts.
    for data_field in data_fields:
        data_entry = body.get(data_field)
        if data_entry:
            files.append((data_field, str(serialize_multipart_data_entry(data_entry))))

    for multipart_field in multipart_fields:
        multipart_entry = body.get(multipart_field)
        if isinstance(multipart_entry, list):
            for idx, e in enumerate(multipart_entry):
                files.append((multipart_field, _normalize_multipart_file_entry(multipart_field, e, idx)))
        elif multipart_entry is not None:
            files.append((multipart_field, _normalize_multipart_file_entry(multipart_field, multipart_entry, 0)))

    return files
