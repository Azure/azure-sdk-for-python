# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Generate migrated Rust test copies from a compact per-file spec.

The parity workflow copies each in-scope v4 test into a
``tests/<op>/<surface>/`` folder, pins the client to ``_backend="rust"``,
and adds a ``# Source:`` comment to every method;
``tests/common/test_legacy_migration_enforcer_unit.py`` (the enforcer) checks
their shape. There are ~80 operations across a sync and an async surface, so
writing all the copies by hand is repetitive and error-prone (a forgotten
``_backend="rust"`` pin, a broken ``# Source:`` line, a missing ``__init__.py``).

This module generates them. A file is described by a small
:class:`LegacyFileSpec`; the generator renders the rest -- the license header,
the imports, the ``HOST`` / ``KEY`` block, the rust-pinned fixture, the
per-method ``# Source:`` line, and the package ``__init__.py``. The pin, the
lineage, and the package marker are always emitted, so generated copies pass
the enforcer.

The existing hand-written folders vary in a few structural ways, captured as
spec fields; the generator reproduces the cleanest example of each
byte-for-byte (checked by ``tests/common/test_legacy_copy_generator_unit.py``):

* ``surface`` -- ``"sync"`` (``unittest.TestCase``, ``setUp`` with registered cleanup)
  or ``"aio"`` (``unittest.IsolatedAsyncioTestCase``, ``asyncSetUp`` /
  ``asyncTearDown``, ``async def`` tests).
* ``fixture`` -- ``"instance"`` (``setUp``) or ``"class"`` (``setUpClass``).
  Async always uses an instance fixture.
* ``license_style`` -- ``"licensed"`` or ``"mit"`` (the two header styles).
* ``module_code`` -- module-level helpers / constants (e.g. a response hook).
* per-method ``decorators`` -- e.g. ``@pytest.mark.parametrize(...)``.

Lane markers (``cosmosEmulator``, ``cosmosLong``, ``cosmosCircuitBreaker``...)
are not hand-written: unless a spec sets ``class_markers``, they are read from
each method's ``# Source:`` original so the copy runs in the same pipeline
lanes. When the originals disagree, each method gets its own markers.

Other variation (docstrings, ``db_id`` prefixes) is supplied by the spec.

Usage::

    from legacy_copy_generator import render_legacy_file, write_legacy_family
    text = render_legacy_file(spec)
    write_legacy_family(spec, tests_root="tests")

CLI -- prints the example file, or writes the bundled specs to a directory you
choose (do not point ``--out-dir`` at a family that already has hand-written
copies)::

    python scripts/v5/legacy_copy_generator.py
    python scripts/v5/legacy_copy_generator.py --out-dir /tmp/generated
"""
from __future__ import annotations

import argparse
import ast
import pathlib
from dataclasses import dataclass
from typing import List, Optional, Tuple


# scripts/v5/<this file> -> parents[2] is the azure-cosmos package root that
# ``# Source: tests/...`` paths are relative to.
_PKG_ROOT = pathlib.Path(__file__).resolve().parents[2]


# The emulator master key the legacy copies fall back to when ``ACCOUNT_KEY``
# is unset. Identical to the constant the hand-written copies use, so the
# generated ``KEY`` line is byte-identical.
_EMULATOR_KEY = "C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw=="


# ---------------------------------------------------------------------------
# Spec model
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class LegacyMethod:
    """One copied test method.

    The generator owns the method's ``def`` line (``async def`` for the aio
    surface) and the ``# Source:`` comment; the spec supplies the name, the
    lineage, and the body.
    """

    #: The original test method name. Rendering appends the migration-suite
    #: suffix; Source references keep the original name.
    name: str

    #: ``# Source:`` value -- ``"tests/<file>.py::Class.method"`` for a copy
    #: with a v4 ancestor, or a string starting with ``"(new)"`` for a test
    #: with none. The enforcer resolves the former against the real tree.
    source: str

    #: The method body as source text, indented to its in-method column
    #: (8 spaces for the first statement level). Inserted verbatim after the
    #: ``# Source:`` line, so a body can be copy-pasted from the source.
    body: str

    #: Optional method decorators (e.g. ``"@pytest.mark.parametrize(...)"``),
    #: rendered above the ``def`` in order.
    decorators: Tuple[str, ...] = ()

    #: Optional one-line method docstring (no surrounding quotes).
    docstring: str = ""


@dataclass(frozen=True)
class LegacyFileSpec:
    """One generated test file for a single operation and surface."""

    #: Operation family folder, e.g. ``"create_item"``.
    op: str

    #: Surface folder, ``"sync"`` or ``"aio"``.
    surface: str

    #: Output file name, e.g. ``"test_none_options.py"``.
    filename: str

    #: Test class name. Matches the source class.
    class_name: str

    #: Prefix for the per-test database id (a uuid suffix is appended), e.g.
    #: ``"legacy_none_options"``.
    db_id_prefix: str

    #: The module docstring text (no surrounding quotes). Use
    #: :func:`build_docstring` for the canonical single-method wording.
    docstring: str

    #: The copied test methods.
    methods: Tuple[LegacyMethod, ...]

    #: Names imported from ``azure.cosmos`` (NOT including ``CosmosClient``,
    #: which the generator imports per surface).
    cosmos_imports: Tuple[str, ...] = ("PartitionKey",)

    #: Extra import lines appended after the cosmos imports.
    extra_imports: Tuple[str, ...] = ()

    #: Optional module-level code (helpers / constants) rendered between the
    #: ``HOST`` / ``KEY`` block and the class. Indentation is removed to column 0.
    module_code: str = ""

    #: Class-level pytest markers (without the ``@pytest.mark.`` prefix).
    #: ``None`` (the default) copies the ``cosmos*`` lane markers from each
    #: method's ``# Source:`` original, so the copy runs in the same pipeline
    #: lanes. Set it explicitly only for files whose methods are all ``(new)``.
    class_markers: Optional[Tuple[str, ...]] = None

    #: Keep key-owned resources separate from configured key/AAD data operations.
    configured_data_auth: bool = False

    #: ``"instance"`` (``setUp``) or ``"class"`` (``setUpClass``). Ignored for
    #: the aio surface, which always uses an instance fixture.
    fixture: str = "instance"

    #: ``"licensed"`` or ``"mit"`` -- which two-line license header to emit.
    license_style: str = "licensed"


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

def build_docstring(surface: str, method_name: str, source_file: str, out_path: str) -> str:
    """Return the module-docstring text for a single-method copy.

    Reproduces the wording of the existing copies so a spec need not
    hand-write the docstring. ``surface`` is ``"sync"`` or ``"aio"``.
    """
    if surface == "aio":
        return (
            "Async ``{method}`` test against the\n"
            '``_backend="rust"`` path.\n'
            "\n"
            "Self-contained: builds its own database + container in ``asyncSetUp``\n"
            "and deletes them in ``asyncTearDown``. The class name matches\n"
            "``{src}``; copied method names add ``_rust``.\n"
            "\n"
            "Run with::\n"
            "\n"
            "    pytest --noconftest {out} -v"
        ).format(method=method_name, src=source_file, out=out_path)
    return (
        "Sync ``{method}`` test against the\n"
        '``_backend="rust"`` path.\n'
        "\n"
        "Self-contained: builds its own database + container in ``setUp`` and\n"
        "registers cleanup after acquisition, including on setup failure.\n"
        "The class name and method name match the\n"
        "source (apart from the method's ``_rust`` suffix) at ``{src}`` so\n"
        "test IDs differ by path and method suffix.\n"
        "\n"
        "Run with::\n"
        "\n"
        "    pytest --noconftest {out} -v"
    ).format(method=method_name, src=source_file, out=out_path)


def render_init_py() -> str:
    """Return the canonical package ``__init__.py`` contents."""
    return (
        "# Copyright (c) Microsoft Corporation. All rights reserved.\n"
        "# Licensed under the MIT License.\n"
    )


def _license_header(style: str) -> List[str]:
    if style == "mit":
        return [
            "# The MIT License (MIT)",
            "# Copyright (c) Microsoft Corporation. All rights reserved.",
        ]
    return [
        "# Copyright (c) Microsoft Corporation. All rights reserved.",
        "# Licensed under the MIT License.",
    ]


def _import_block(spec: LegacyFileSpec) -> List[str]:
    lines = ["import os", "import unittest", "import uuid", "", "import pytest", ""]
    cosmos_names = ", ".join(spec.cosmos_imports)
    if spec.surface == "aio":
        if cosmos_names:
            lines.append("from azure.cosmos import " + cosmos_names)
        lines.append("from azure.cosmos.aio import CosmosClient")
    else:
        joined = "CosmosClient" + (", " + cosmos_names if cosmos_names else "")
        lines.append("from azure.cosmos import " + joined)
    lines.extend(spec.extra_imports)
    return lines


def _class_base(surface: str) -> str:
    return "unittest.IsolatedAsyncioTestCase" if surface == "aio" else "unittest.TestCase"


def _fixture_block(spec: LegacyFileSpec) -> List[str]:
    """Render setup and cleanup; the ``_backend="rust"`` pin is always included."""
    db_id = '"' + spec.db_id_prefix + '_" + uuid.uuid4().hex[:8]'

    if spec.configured_data_auth:
        if spec.surface == "aio":
            return [
                "    async def asyncSetUp(self):",
                '        self.key_client = CosmosClient(HOST, KEY, _backend="rust")',
                "        self.addAsyncCleanup(self.key_client.close)",
                "        await self.key_client.__aenter__()",
                "        self._db_id = " + db_id,
                '        self._container_id = "c_" + uuid.uuid4().hex[:8]',
                "        key_database = await self.key_client.create_database(self._db_id)",
                "        self.addAsyncCleanup(self.key_client.delete_database, self._db_id)",
                "        await key_database.create_container(",
                '            id=self._container_id, partition_key=PartitionKey(path="/pk"),',
                "        )",
                '        self.client = clients.create_data_client_async(_backend="rust")',
                "        self.addAsyncCleanup(self.client.close)",
                "        await self.client.__aenter__()",
                "        self.database = self.client.get_database_client(self._db_id)",
                "        self.container = self.database.get_container_client(self._container_id)",
            ]
        if spec.fixture != "class":
            raise ValueError("Configured data authentication requires a sync class or async instance fixture")
        return [
            "    @classmethod",
            "    def setUpClass(cls):",
            '        cls.key_client = CosmosClient(HOST, KEY, _backend="rust")',
            "        cls.addClassCleanup(cls.key_client.close)",
            "        cls._db_id = " + db_id,
            '        cls._container_id = "c_" + uuid.uuid4().hex[:8]',
            "        key_database = cls.key_client.create_database(cls._db_id)",
            "        cls.addClassCleanup(cls.key_client.delete_database, cls._db_id)",
            "        key_database.create_container(",
            '            id=cls._container_id, partition_key=PartitionKey(path="/pk"),',
            "        )",
            '        cls.client = clients.create_data_client(_backend="rust")',
            "        cls.addClassCleanup(cls.client.close)",
            "        cls.database = cls.client.get_database_client(cls._db_id)",
            "        cls.container = cls.database.get_container_client(cls._container_id)",
        ]

    if spec.surface == "aio":
        return [
            "    async def asyncSetUp(self):",
            '        self.client = CosmosClient(HOST, KEY, _backend="rust")',
            "        await self.client.__aenter__()",
            "        self._db_id = " + db_id,
            '        self._container_id = "c_" + uuid.uuid4().hex[:8]',
            "        self.database = await self.client.create_database(self._db_id)",
            "        self.container = await self.database.create_container(",
            "            id=self._container_id,",
            '            partition_key=PartitionKey(path="/pk"),',
            "        )",
            "",
            "    async def asyncTearDown(self):",
            "        try:",
            "            await self.client.delete_database(self._db_id)",
            "        except Exception:  # pylint: disable=broad-except",
            "            pass",
            "        await self.client.close()",
        ]

    if spec.fixture == "class":
        return [
            "    @classmethod",
            "    def setUpClass(cls):",
            '        cls.client = CosmosClient(HOST, KEY, _backend="rust")',
            "        cls._db_id = " + db_id,
            '        cls._container_id = "c_" + uuid.uuid4().hex[:8]',
            "        cls.database = cls.client.create_database(cls._db_id)",
            "        cls.container = cls.database.create_container(",
            "            id=cls._container_id,",
            '            partition_key=PartitionKey(path="/pk"),',
            "        )",
            "",
            "    @classmethod",
            "    def tearDownClass(cls):",
            "        try:",
            "            cls.client.delete_database(cls._db_id)",
            "        except Exception:  # pylint: disable=broad-except",
            "            pass",
        ]

    return [
        "    def setUp(self) -> None:",
        '        self.client = CosmosClient(HOST, KEY, _backend="rust")',
        "        self.addCleanup(self.client.close)",
        '        self._db_id = "' + spec.db_id_prefix + '_" + uuid.uuid4().hex',
        '        self._container_id = "c_" + uuid.uuid4().hex[:8]',
        "        self.database = self.client.create_database(self._db_id)",
        "        self.addCleanup(self.client.delete_database, self._db_id)",
        "        self.container = self.database.create_container(",
        "            id=self._container_id,",
        '            partition_key=PartitionKey(path="/pk"),',
        "        )",
    ]


def _lane_markers_in(decorators) -> List[str]:
    """``cosmos*`` names from ``pytest.mark.<name>`` expressions, in order."""
    names: List[str] = []
    for dec in decorators:
        target = dec.func if isinstance(dec, ast.Call) else dec
        if (isinstance(target, ast.Attribute) and target.attr.startswith("cosmos")
                and isinstance(target.value, ast.Attribute) and target.value.attr == "mark"
                and target.attr not in names):
            names.append(target.attr)
    return names


def source_lane_markers(source: str, source_root=None) -> Tuple[str, ...]:
    """Return the ``cosmos*`` markers that apply to a ``# Source:`` original.

    Combines module ``pytestmark``, class decorators and method decorators in
    that order. Raises ``ValueError`` if the original can't be found, so a
    copy never silently falls back to a lane its original doesn't run in.
    """
    root = pathlib.Path(source_root) if source_root is not None else _PKG_ROOT
    path_part, _, qualified = source.partition("::")
    class_name, _, method_name = qualified.rpartition(".")
    path = root / path_part
    if not path.is_file():
        raise ValueError("cannot derive markers: source file not found for " + source)
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    markers: List[str] = []
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "pytestmark" for t in node.targets):
            value = node.value
            markers += _lane_markers_in(value.elts if isinstance(value, (ast.List, ast.Tuple)) else [value])
    scopes = [(None, tree.body)]
    if class_name:
        scopes = [(n, n.body) for n in tree.body if isinstance(n, ast.ClassDef) and n.name == class_name]
    for cls, body in scopes:
        for func in body:
            if isinstance(func, (ast.FunctionDef, ast.AsyncFunctionDef)) and func.name == method_name:
                if cls is not None:
                    markers += _lane_markers_in(cls.decorator_list)
                markers += _lane_markers_in(func.decorator_list)
                return tuple(dict.fromkeys(markers))
    raise ValueError("cannot derive markers: {} not found in {}".format(qualified, path_part))


def resolve_markers(spec: "LegacyFileSpec", source_root=None):
    """Return ``(class_markers, {method_name: method_markers})`` for ``spec``.

    Explicit ``spec.class_markers`` win. Otherwise markers come from the
    originals: on the class when every copied method agrees, else per method.
    """
    if spec.class_markers is not None:
        return tuple(spec.class_markers), {}
    derived = {m.name: source_lane_markers(m.source, source_root)
               for m in spec.methods if not m.source.startswith("(new)")}
    if not derived:
        raise ValueError(spec.filename + ": all methods are (new); set class_markers explicitly")
    if any(m.source.startswith("(new)") for m in spec.methods) or len(
            {frozenset(v) for v in derived.values()}) > 1:
        return (), derived
    return next(iter(derived.values())), {}


def _method_block(spec: LegacyFileSpec, method: LegacyMethod,
                  method_markers: Tuple[str, ...] = ()) -> List[str]:
    lines: List[str] = []
    for marker in method_markers:
        lines.append("    @pytest.mark." + marker)
    for decorator in method.decorators:
        lines.append("    " + decorator)
    def_keyword = "    async def " if spec.surface == "aio" else "    def "
    name = method.name if method.name.endswith("_rust") else method.name + "_rust"
    lines.append(def_keyword + name + "(self):")
    if method.docstring:
        lines.append('        """' + method.docstring + '"""')
    lines.append("        # Source: " + method.source)
    # The body is inserted verbatim (already indented to the method's column).
    lines.extend(method.body.strip("\n").split("\n"))
    return lines


def render_legacy_file(spec: LegacyFileSpec, source_root=None) -> str:
    """Render the full text of a migrated test file from ``spec``.

    ``source_root`` is where ``# Source: tests/...`` paths resolve when lane
    markers are derived; it defaults to this package's root.
    """
    class_markers, method_markers = resolve_markers(spec, source_root)
    lines: List[str] = []

    # 1. License header.
    lines.extend(_license_header(spec.license_style))

    # 2. Module docstring.
    lines.append('"""' + spec.docstring)
    lines.append('"""')

    # 3. Imports.
    lines.extend(_import_block(spec))
    lines.append("")
    lines.append("")

    # 4. HOST / KEY (emulator-default form, matching the existing copies).
    lines.append('HOST = os.environ.get("ACCOUNT_HOST", "https://localhost:8081/")')
    lines.append("KEY = os.environ.get(")
    lines.append('    "ACCOUNT_KEY",')
    lines.append('    "' + _EMULATOR_KEY + '",')
    lines.append(")")
    lines.append("")
    lines.append("")

    # 5. Optional module-level helpers / constants.
    if spec.module_code.strip():
        lines.append(spec.module_code.strip("\n"))
        lines.append("")
        lines.append("")

    # 6. Class header + markers.
    for marker in class_markers:
        lines.append("@pytest.mark." + marker)
    lines.append("class " + spec.class_name + "(" + _class_base(spec.surface) + "):")
    lines.append("")

    # 7. Setup and cleanup, with the ``_backend="rust"`` pin.
    lines.extend(_fixture_block(spec))

    # 8. The copied methods. Each gets its ``# Source:`` line.
    for method in spec.methods:
        lines.append("")
        lines.extend(_method_block(spec, method, method_markers.get(method.name, ())))

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Writing to disk
# ---------------------------------------------------------------------------

def legacy_dir_for(spec: LegacyFileSpec, tests_root) -> pathlib.Path:
    """Return the migrated test's operation/surface package."""
    return pathlib.Path(tests_root) / spec.op / spec.surface


def write_legacy_family(spec: LegacyFileSpec, tests_root) -> pathlib.Path:
    """Write ``spec``'s legacy file (and the package ``__init__.py``) under
    ``tests_root``. Returns the written test file path."""
    directory = legacy_dir_for(spec, tests_root)
    directory.mkdir(parents=True, exist_ok=True)
    for package in (directory.parent, directory):
        marker = package / "__init__.py"
        if not marker.exists():
            marker.write_text(render_init_py(), encoding="utf-8")
    out_path = directory / spec.filename
    out_path.write_text(render_legacy_file(spec), encoding="utf-8")
    return out_path


# ---------------------------------------------------------------------------
# Bundled example specs
# ---------------------------------------------------------------------------
#
# Three reproduce an existing copy byte-for-byte and pin the canonical shape
# for each template axis (see the generator unit test):
#   * CREATE_ITEM_SYNC_NONE_OPTIONS -- sync, instance fixture, "licensed".
#   * CREATE_ITEM_SYNC_HEADERS      -- sync, class fixture, "mit", module code.
#   * CREATE_ITEM_AIO_HEADERS       -- async, "mit", module code.
# Two more show a new family generated in the canonical shape from a short
# spec: READ_ITEM_SYNC_NONE_OPTIONS and CREATE_ITEM_AIO_NONE_OPTIONS.


CREATE_ITEM_SYNC_NONE_OPTIONS = LegacyFileSpec(
    op="create_item",
    surface="sync",
    filename="test_none_options.py",
    class_name="TestNoneOptions",
    db_id_prefix="legacy_none_options",
    docstring=build_docstring(
        "sync",
        "test_container_create_item_none_options",
        "tests/test_none_options.py",
        "tests/create_item/sync/test_none_options.py",
    ),
    methods=(
        LegacyMethod(
            name="test_container_create_item_none_options",
            source="tests/test_none_options.py::TestNoneOptions.test_container_create_item_none_options",
            body="""\
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 1}
        created = self.container.create_item(
            item,
            indexing_directive=None,
            enable_automatic_id_generation=False,
            session_token=None,
            initial_headers=None,
            priority=None,
            no_response=None,
            retry_write=None,
            throughput_bucket=None,
        )
        assert created["id"] == item["id"]""",
        ),
    ),
)


_HEADERS_MODULE_CODE_SYNC = """\
# Preserve the original value at the typed native boundary.
# Wire-header conversion is checked by the binding settings tests.
request_throughput_bucket_number = 3"""


CREATE_ITEM_SYNC_HEADERS = LegacyFileSpec(
    op="create_item",
    surface="sync",
    filename="test_headers.py",
    class_name="TestHeaders",
    configured_data_auth=True,
    db_id_prefix="legacy_headers",
    license_style="mit",
    fixture="class",
    cosmos_imports=("PartitionKey",),
    extra_imports=("import importlib", "from unittest.mock import patch", "from config import clients"),
    module_code=_HEADERS_MODULE_CODE_SYNC,
    docstring="""\
Sync ``test_container_create_item_throughput_bucket`` test against
the ``_backend="rust"`` path.

The other methods in the source ``TestHeaders`` class cover correlated
activity ids, dedicated-gateway max-age, query headers, etc.; they
belong to their own operations' ``legacy/`` folders.

Self-contained: key-owned setup registers cleanup in ``setUpClass``;
data operations follow the configured key/AAD lane. The class name matches
``tests/test_headers.py``; copied method names add ``_rust``.

Run with::

    pytest --noconftest tests/create_item/sync/test_headers.py -v""",
    methods=(
        LegacyMethod(
            name="test_container_create_item_throughput_bucket",
            source="tests/test_headers.py::TestHeaders.test_container_create_item_throughput_bucket",
            body="""\
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "create_item", wraps=binding.create_item) as operation:
            created = self.container.create_item(
                body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
                throughput_bucket=request_throughput_bucket_number)
        operation.assert_called_once()
        prepared = operation.call_args.args[1]
        self.assertEqual(prepared.settings.throughput_bucket, request_throughput_bucket_number)
        self.assertEqual(prepared.op, "create_item")
        self.assertEqual(created["id"], prepared.item_id)""",
        ),
    ),
)


_HEADERS_MODULE_CODE_AIO = """\
# Preserve the original value at the typed native boundary.
# Wire-header conversion is checked by the binding settings tests.
request_throughput_bucket_number = 3"""


CREATE_ITEM_AIO_HEADERS = LegacyFileSpec(
    op="create_item",
    surface="aio",
    filename="test_headers.py",
    class_name="TestHeadersAsync",
    configured_data_auth=True,
    db_id_prefix="legacy_headers_async",
    license_style="mit",
    cosmos_imports=("PartitionKey",),
    extra_imports=("import importlib", "from unittest.mock import patch", "from config import clients"),
    module_code=_HEADERS_MODULE_CODE_AIO,
    docstring="""\
Async ``test_container_create_item_throughput_bucket`` test against
the ``_backend="rust"`` path.

The other methods in the source ``TestHeadersAsync`` class cover other
operations; they belong to their own operations' ``legacy/`` folders.

Self-contained: key-owned setup registers cleanup in ``asyncSetUp``;
data operations follow the configured key/AAD lane. The class name matches
``tests/test_headers_async.py``; copied method names add ``_rust``.

Run with::

    pytest --noconftest tests/create_item/aio/test_headers.py -v""",
    methods=(
        LegacyMethod(
            name="test_container_create_item_throughput_bucket_async",
            source="tests/test_headers_async.py::TestHeadersAsync.test_container_create_item_throughput_bucket_async",
            body="""\
        binding = importlib.import_module(type(self.client._adapter).__module__)._rust_module
        with patch.object(binding, "create_item_async", wraps=binding.create_item_async) as operation:
            created = await self.container.create_item(
                body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
                throughput_bucket=request_throughput_bucket_number)
        operation.assert_called_once()
        prepared = operation.call_args.args[1]
        self.assertEqual(prepared.settings.throughput_bucket, request_throughput_bucket_number)
        self.assertEqual(prepared.op, "create_item")
        self.assertEqual(created["id"], prepared.item_id)""",
        ),
    ),
)


READ_ITEM_SYNC_NONE_OPTIONS = LegacyFileSpec(
    op="read_item",
    surface="sync",
    filename="test_none_options.py",
    class_name="TestNoneOptions",
    db_id_prefix="legacy_read_none_options",
    docstring=build_docstring(
        "sync",
        "test_container_read_item_none_options",
        "tests/test_none_options.py",
        "tests/read_item/sync/test_none_options.py",
    ),
    methods=(
        LegacyMethod(
            name="test_container_read_item_none_options",
            source="tests/test_none_options.py::TestNoneOptions.test_container_read_item_none_options",
            body="""\
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 42}
        self.container.create_item(item)
        read_back = self.container.read_item(
            item["id"],
            partition_key=item["pk"],
            post_trigger_include=None,
            session_token=None,
            initial_headers=None,
            max_integrated_cache_staleness_in_ms=None,
            priority=None,
            throughput_bucket=None,
        )
        assert read_back["id"] == item["id"]""",
        ),
    ),
)


CREATE_ITEM_AIO_NONE_OPTIONS = LegacyFileSpec(
    op="create_item",
    surface="aio",
    filename="test_none_options.py",
    class_name="TestNoneOptionsAsync",
    db_id_prefix="legacy_none_options_async",
    docstring=build_docstring(
        "aio",
        "test_container_create_item_none_options_async",
        "tests/test_none_options_async.py",
        "tests/create_item/aio/test_none_options.py",
    ),
    methods=(
        LegacyMethod(
            name="test_container_create_item_none_options_async",
            source="tests/test_none_options_async.py::TestNoneOptionsAsync."
                   "test_container_create_item_none_options_async",
            body="""\
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 1}
        created = await self.container.create_item(
            item,
            indexing_directive=None,
            enable_automatic_id_generation=False,
            session_token=None,
            initial_headers=None,
            priority=None,
            no_response=None,
            retry_write=None,
            throughput_bucket=None,
        )
        assert created["id"] == item["id"]""",
        ),
    ),
)


#: Specs the CLI and the generator unit test exercise.
BUNDLED_SPECS = (
    CREATE_ITEM_SYNC_NONE_OPTIONS,
    CREATE_ITEM_SYNC_HEADERS,
    CREATE_ITEM_AIO_HEADERS,
    READ_ITEM_SYNC_NONE_OPTIONS,
    CREATE_ITEM_AIO_NONE_OPTIONS,
)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--out-dir",
        default=None,
        help="Write the bundled specs under this tests-root dir (a sandbox "
             "you choose). When omitted, the example file is printed.",
    )
    args = parser.parse_args(argv)

    if args.out_dir is None:
        print(render_legacy_file(CREATE_ITEM_SYNC_NONE_OPTIONS), end="")
        return 0

    for spec in BUNDLED_SPECS:
        written = write_legacy_family(spec, args.out_dir)
        print("wrote {}".format(written))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
