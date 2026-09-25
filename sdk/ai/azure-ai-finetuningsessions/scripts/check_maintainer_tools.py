# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Offline regressions for maintainer tools; runnable on Python 3.10 and later.

Run this script directly. It needs no captured comparison artifacts and writes
only temporary fixtures, never the package or the immutable reference oracle.
"""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import inspect
import json
from pathlib import Path
import sys
import tempfile
import typing
import unittest
from unittest.mock import patch

PACKAGE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PACKAGE))


def _load_tool(name):
    spec = importlib.util.spec_from_file_location(name, PACKAGE / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


surface_tool = _load_tool("verify_surface")
reference_tool = _load_tool("verify_reference_snapshot")


class OverloadFixture:
    @typing.overload
    def convert(self, value: str, /, *, mode: typing.Literal["text"] = "text") -> int: ...

    @typing.overload
    def convert(self, value: bytes, /, *, mode: typing.Literal["bytes"] = "bytes") -> bytes: ...

    def convert(self, value, /, *, mode="text"):
        raise AssertionError("The verifier must never run the original method body")

    @typing.overload
    async def read(self, value: str) -> int: ...

    @typing.overload
    async def read(self, value: bytes) -> bytes: ...

    async def read(self, value):
        raise AssertionError("The verifier must never run the original method body")


class InheritedFixture(OverloadFixture):
    pass


class SurfaceToolTests(unittest.TestCase):
    def test_forward_references_preserve_nested_nullable_types(self):
        namespace = {**vars(typing), "Item": str}
        annotation = "Optional[list[Optional[list[tuple[int, 'Item']]]]]"
        actual = surface_tool._resolve_annotation(annotation, namespace)
        self.assertEqual(actual, typing.Optional[list[typing.Optional[list[tuple[int, str]]]]])

    def test_literals_are_values_not_forward_references(self):
        actual = surface_tool._resolve_annotation(typing.Literal["future-tag", "text"], {})
        self.assertEqual(typing.get_args(actual), ("future-tag", "text"))

    def test_builtin_alias_forward_refs_resolve(self):
        actual = surface_tool._resolve_annotation(list["Item"], {"Item": int})
        self.assertEqual(typing.get_args(actual), (int,))

    def test_callable_and_annotated_forward_refs_resolve(self):
        namespace = {**vars(typing), "Item": int}
        actual = surface_tool._resolve_annotation(
            typing.Callable[[list["Item"]], typing.Annotated[list["Item"], "metadata"]], namespace
        )
        parameters, result = typing.get_args(actual)
        self.assertEqual(parameters, [list[int]])
        self.assertEqual(typing.get_args(result), (list[int], "metadata"))

    def test_missing_annotation_name_fails_closed(self):
        with self.assertRaises(NameError):
            surface_tool._resolve_annotation("UnknownType", {})

    def test_overload_fallback_retains_parameters_defaults_and_returns(self):
        with patch.object(typing, "get_overloads", None, create=True):
            overloads = surface_tool.declared_overloads(InheritedFixture.convert)
        self.assertEqual(len(overloads), 2)
        first, second = (inspect.signature(function) for function in overloads)
        self.assertEqual(first.parameters["value"].kind, inspect.Parameter.POSITIONAL_ONLY)
        self.assertEqual(first.parameters["mode"].kind, inspect.Parameter.KEYWORD_ONLY)
        self.assertEqual(first.parameters["mode"].default, "text")
        self.assertEqual(second.parameters["mode"].default, "bytes")
        self.assertEqual(first.return_annotation, "int")
        self.assertEqual(second.return_annotation, "bytes")

    def test_async_overloads_remain_async(self):
        overloads = surface_tool._source_overloads(InheritedFixture.read)
        self.assertEqual(len(overloads), 2)
        self.assertTrue(all(inspect.iscoroutinefunction(function) for function in overloads))

    def test_absent_python_source_is_not_silently_ignored(self):
        with patch.object(surface_tool.inspect, "getsourcefile", return_value=None):
            with self.assertRaisesRegex(ValueError, "Cannot inspect overload source"):
                surface_tool._source_overloads(OverloadFixture.convert)

    def test_complete_sdk_surface_keeps_overloads_in_fallback(self):
        native = surface_tool.surface(input_chunk_discriminator=True)
        with patch.object(typing, "get_overloads", None, create=True):
            fallback = surface_tool.surface(input_chunk_discriminator=True)
        self.assertEqual(fallback, native)
        self.assertEqual(len(fallback["models"]["ModelInput"]["overloads"]), 2)
        self.assertEqual(
            fallback["models"]["ModelInput"]["fields"]["chunks"]["type"],
            {"origin": "list", "args": ["InputChunk"]},
        )
        self.assertGreater(sum(len(model.get("overloads", [])) for model in fallback["models"].values()), 0)
        self.assertGreater(
            sum(len(method["overloads"]) for client in fallback["clients"].values() for method in client.values()), 0
        )


class ProvenanceLinkTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(prefix="loom-provenance-link-")
        self.addCleanup(directory.cleanup)
        self.package = Path(directory.name)
        self.record_dir = self.package / "eng/generation"
        self.record_dir.mkdir(parents=True)
        self.manifest = json.loads((PACKAGE / "eng/generation/reference.json").read_text(encoding="utf-8"))
        self.provenance = json.loads((PACKAGE / "eng/generation/provenance.json").read_text(encoding="utf-8"))
        self.write_records()

    def write_records(self):
        (self.record_dir / "reference.json").write_text(json.dumps(self.manifest), encoding="utf-8")
        (self.record_dir / "provenance.json").write_text(json.dumps(self.provenance), encoding="utf-8")

    def test_checked_in_reference_points_to_valid_provenance(self):
        result = reference_tool.load_manifest()
        self.assertEqual(result["generation_provenance"], "eng/generation/provenance.json")
        self.assertEqual(reference_tool.load_manifest(self.package), self.manifest)

    def test_missing_target_is_rejected_despite_stale_root_record(self):
        (self.package / "generation-provenance.json").write_text(json.dumps(self.provenance), encoding="utf-8")
        (self.record_dir / "provenance.json").unlink()
        with self.assertRaisesRegex(ValueError, "missing or outside"):
            reference_tool.load_manifest(self.package)

    def test_old_deleted_target_is_rejected(self):
        self.manifest["generation_provenance"] = "generation-provenance.json"
        self.write_records()
        with self.assertRaisesRegex(ValueError, "missing or outside"):
            reference_tool.load_manifest(self.package)

    def test_invalid_paths_are_rejected(self):
        for value in (None, "", 7, "../provenance.json", "/tmp/provenance.json", "C:/provenance.json", "eng\\generation\\provenance.json"):
            with self.subTest(path=value):
                self.manifest["generation_provenance"] = value
                self.write_records()
                with self.assertRaises(ValueError):
                    reference_tool.load_manifest(self.package)

    def test_malformed_and_nonobject_targets_are_rejected(self):
        for value in ("{broken", "[]", "null", '{"schema_version": 2}'):
            with self.subTest(value=value):
                (self.record_dir / "provenance.json").write_text(value, encoding="utf-8")
                with self.assertRaises(ValueError):
                    reference_tool.load_manifest(self.package)

    def test_wrong_package_or_reference_is_rejected(self):
        original = deepcopy(self.provenance)
        for field in ("namespace", "distribution", "repository", "commit", "manifest"):
            with self.subTest(field=field):
                self.provenance = deepcopy(original)
                record = self.provenance if field in ("namespace", "distribution") else self.provenance["reference"]
                record[field] = "wrong"
                self.write_records()
                with self.assertRaisesRegex(ValueError, "does not identify"):
                    reference_tool.load_manifest(self.package)


if __name__ == "__main__":
    unittest.main()