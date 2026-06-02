# pylint: disable=line-too-long,useless-suppression
# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
"""Offline unit tests for ``prepare_multipart_form_data``.

These tests verify that every concrete variant of the SDK's ``FileType``
union (as defined in ``azure.ai.projects._utils.utils``) produces a
multipart-equivalent normalized entry — i.e. the same field name, filename
and content payload, with ``content_type`` differing only when the caller
explicitly supplied it. They run entirely offline (no network, no
recordings) and operate directly on the helper.
"""

import io

import pytest

from azure.ai.projects._utils.utils import prepare_multipart_form_data

FILENAME = "canvas-design.zip"
CONTENT = b"PK\x03\x04 fake zip body"
FIELD = "files"


def _read(value):
    """Return raw bytes for a ``FileContent`` value (``bytes`` or ``IO[bytes]``)."""
    if hasattr(value, "read"):
        # Rewind first so we can compare regardless of prior position.
        try:
            value.seek(0)
        except Exception:  # pylint: disable=broad-except
            pass
        return value.read()
    return value


def _canonicalize(prepared):
    """Reduce the helper's output to ``(field, filename, content_bytes, content_type)``.

    ``content_type`` defaults to ``"application/zip"`` so that 2-tuple and
    3-tuple variants compare equal when the caller relied on the default.
    """
    assert len(prepared) == 1, f"expected a single multipart entry, got {prepared!r}"
    field, entry = prepared[0]
    assert isinstance(entry, tuple), f"helper must wrap entry as a tuple, got {entry!r}"
    if len(entry) == 2:
        filename, content = entry
        content_type = "application/zip"
    elif len(entry) == 3:
        filename, content, content_type = entry
        content_type = content_type or "application/zip"
    else:
        raise AssertionError(f"unexpected tuple arity: {entry!r}")
    return (field, filename, _read(content), content_type)


def _variant_io_bytes(tmp_path):
    p = tmp_path / FILENAME
    p.write_bytes(CONTENT)
    return p.open("rb")


def _variants(tmp_path):
    """Yield ``(label, files_value)`` for every supported ``FileType`` variant."""
    yield ("IO[bytes] (from open)", [_variant_io_bytes(tmp_path)])
    yield ("(filename, bytes)", [(FILENAME, CONTENT)])
    yield ("(filename, IO[bytes])", [(FILENAME, io.BytesIO(CONTENT))])
    yield ("(filename, bytes, content_type)", [(FILENAME, CONTENT, "application/zip")])


def test_filetype_variants_produce_equivalent_request_body(tmp_path):
    """All ``FileType`` variants must normalize to the same multipart entry."""
    canonical_by_variant = {}
    for label, files_value in _variants(tmp_path):
        prepared = prepare_multipart_form_data({"files": files_value}, ["files"], [])
        canonical_by_variant[label] = _canonicalize(prepared)

    expected = (FIELD, FILENAME, CONTENT, "application/zip")
    for label, canonical in canonical_by_variant.items():
        assert canonical == expected, f"variant {label!r} produced {canonical!r}, expected {expected!r}"


@pytest.mark.parametrize(
    "label,files_value_factory",
    [
        ("IO[bytes] (from open)", lambda tmp_path: [_variant_io_bytes(tmp_path)]),
        ("(filename, bytes)", lambda _tmp_path: [(FILENAME, CONTENT)]),
        ("(filename, IO[bytes])", lambda _tmp_path: [(FILENAME, io.BytesIO(CONTENT))]),
        ("(filename, bytes, content_type)", lambda _tmp_path: [(FILENAME, CONTENT, "application/zip")]),
    ],
)
def test_filetype_variant_normalized_entry(tmp_path, label, files_value_factory):
    """Per-variant sanity: the helper emits a single ``files`` part with the
    expected filename and content."""
    prepared = prepare_multipart_form_data({"files": files_value_factory(tmp_path)}, ["files"], [])
    field, filename, content, _content_type = _canonicalize(prepared)
    assert field == FIELD, label
    assert filename == FILENAME, label
    assert content == CONTENT, label


def test_data_field_precedes_file_parts(tmp_path):
    """Data fields must be appended before file parts so streaming server
    parsers see metadata before binary content."""
    prepared = prepare_multipart_form_data(
        {"files": [_variant_io_bytes(tmp_path)], "default": True},
        ["files"],
        ["default"],
    )
    assert [field for field, _ in prepared] == ["default", "files"]
