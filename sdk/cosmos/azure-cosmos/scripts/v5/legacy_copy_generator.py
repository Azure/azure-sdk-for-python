# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Generate the legacy-folder parity copies from a compact per-file spec.

The parity workflow copies each in-scope v4 test into a
``tests/<op>/<surface>/legacy/`` folder, pins the client to ``_backend="rust"``,
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

* ``surface`` -- ``"sync"`` (``unittest.TestCase``, ``setUp`` / ``tearDown``)
  or ``"aio"`` (``unittest.IsolatedAsyncioTestCase``, ``asyncSetUp`` /
  ``asyncTearDown``, ``async def`` tests).
* ``fixture`` -- ``"instance"`` (``setUp``) or ``"class"`` (``setUpClass``).
  Async is always instance-fixtured.
* ``license_style`` -- ``"licensed"`` or ``"mit"`` (the two header styles).
* ``module_code`` -- module-level helpers / constants (e.g. a response hook).
* per-method ``decorators`` -- e.g. ``@pytest.mark.parametrize(...)``.

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
import pathlib
from dataclasses import dataclass
from typing import List, Tuple


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

    #: The test method name. Matches the source so test IDs differ only by
    #: path (the parity reporter pairs runs by ``(file, class, method)``).
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
    """One generated ``legacy/`` test file for a single operation + surface."""

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
    #: ``HOST`` / ``KEY`` block and the class. Dedented to column 0.
    module_code: str = ""

    #: Class-level pytest markers (without the ``@pytest.mark.`` prefix).
    class_markers: Tuple[str, ...] = ("cosmosEmulator",)

    #: ``"instance"`` (``setUp``) or ``"class"`` (``setUpClass``). Ignored for
    #: the aio surface, which is always instance-fixtured.
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
            "and deletes them in ``asyncTearDown``. The class name and method name\n"
            "match the source at ``{src}`` so test IDs\n"
            "differ only by path.\n"
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
        "deletes them in ``tearDown``. The class name and method name match the\n"
        "source at ``{src}`` so test IDs differ only by\n"
        "path.\n"
        "\n"
        "Run with::\n"
        "\n"
        "    pytest --noconftest {out} -v"
    ).format(method=method_name, src=source_file, out=out_path)


def render_init_py() -> str:
    """Return the canonical ``legacy/__init__.py`` contents."""
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
    """Render the setUp/tearDown block; the ``_backend="rust"`` pin is always included."""
    db_id = '"' + spec.db_id_prefix + '_" + uuid.uuid4().hex[:8]'

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
        "        self._db_id = " + db_id,
        '        self._container_id = "c_" + uuid.uuid4().hex[:8]',
        "        self.database = self.client.create_database(self._db_id)",
        "        self.container = self.database.create_container(",
        "            id=self._container_id,",
        '            partition_key=PartitionKey(path="/pk"),',
        "        )",
        "",
        "    def tearDown(self) -> None:",
        "        try:",
        "            self.client.delete_database(self._db_id)",
        "        except Exception:  # pylint: disable=broad-except",
        "            # Best-effort cleanup: the test has already produced its",
        "            # verdict by the time tearDown runs, and a stuck account",
        "            # state should not mask the test result.",
        "            pass",
    ]


def _method_block(spec: LegacyFileSpec, method: LegacyMethod) -> List[str]:
    lines: List[str] = []
    for decorator in method.decorators:
        lines.append("    " + decorator)
    def_keyword = "    async def " if spec.surface == "aio" else "    def "
    lines.append(def_keyword + method.name + "(self):")
    if method.docstring:
        lines.append('        """' + method.docstring + '"""')
    lines.append("        # Source: " + method.source)
    # The body is inserted verbatim (already indented to the method's column).
    lines.extend(method.body.strip("\n").split("\n"))
    return lines


def render_legacy_file(spec: LegacyFileSpec) -> str:
    """Render the full text of a ``legacy/`` test file from ``spec``."""
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
    for marker in spec.class_markers:
        lines.append("@pytest.mark." + marker)
    lines.append("class " + spec.class_name + "(" + _class_base(spec.surface) + "):")
    lines.append("")

    # 7. setUp/tearDown, which builds the client with the ``_backend="rust"`` pin.
    lines.extend(_fixture_block(spec))

    # 8. The copied methods. Each gets its ``# Source:`` line.
    for method in spec.methods:
        lines.append("")
        lines.extend(_method_block(spec, method))

    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Writing to disk
# ---------------------------------------------------------------------------

def legacy_dir_for(spec: LegacyFileSpec, tests_root) -> pathlib.Path:
    """Return ``<tests_root>/<op>/<surface>/legacy`` for ``spec``."""
    return pathlib.Path(tests_root) / spec.op / spec.surface / "legacy"


def write_legacy_family(spec: LegacyFileSpec, tests_root) -> pathlib.Path:
    """Write ``spec``'s legacy file (and the package ``__init__.py``) under
    ``tests_root``. Returns the written test file path."""
    directory = legacy_dir_for(spec, tests_root)
    directory.mkdir(parents=True, exist_ok=True)
    (directory / "__init__.py").write_text(render_init_py(), encoding="utf-8")
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
        "tests/create_item/sync/legacy/test_none_options.py",
    ),
    methods=(
        LegacyMethod(
            name="test_container_create_item_none_options",
            source="tests/test_none_options.py::TestNoneOptions.test_container_create_item_none_options",
            body="""\
        item = {"id": str(uuid.uuid4()), "pk": "pk-value", "value": 1}
        created = self.container.create_item(
            item,
            pre_trigger_include=None,
            post_trigger_include=None,
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
# The throughput-bucket number the test asserts is stamped on the
# outgoing request. Kept identical to the source constant so the wire
# value is the same as what core-python sent.
request_throughput_bucket_number = 3


def request_raw_response_hook(response):
    assert (response.http_request.headers[http_constants.HttpHeaders.ThroughputBucket]
            == str(request_throughput_bucket_number))"""


CREATE_ITEM_SYNC_HEADERS = LegacyFileSpec(
    op="create_item",
    surface="sync",
    filename="test_headers.py",
    class_name="TestHeaders",
    db_id_prefix="legacy_headers",
    license_style="mit",
    fixture="class",
    cosmos_imports=("PartitionKey", "http_constants"),
    module_code=_HEADERS_MODULE_CODE_SYNC,
    docstring="""\
Sync ``test_container_create_item_throughput_bucket`` test against
the ``_backend="rust"`` path.

The other methods in the source ``TestHeaders`` class cover correlated
activity ids, dedicated-gateway max-age, query headers, etc.; they
belong to their own operations' ``legacy/`` folders.

Self-contained: builds its own database + container in ``setUpClass``
and deletes them in ``tearDownClass``. The class name and method name
match the source at ``tests/test_headers.py`` so test IDs differ only
by path.

Run with::

    pytest --noconftest tests/create_item/sync/legacy/test_headers.py -v""",
    methods=(
        LegacyMethod(
            name="test_container_create_item_throughput_bucket",
            source="tests/test_headers.py::TestHeaders.test_container_create_item_throughput_bucket",
            body="""\
        self.container.create_item(
            body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)""",
        ),
    ),
)


_HEADERS_MODULE_CODE_AIO = """\
# The throughput-bucket number the test asserts is stamped on the
# outgoing request. Kept identical to the source constant so the wire
# value is the same as what core-python sent.
request_throughput_bucket_number = 3


async def request_raw_response_hook(response):
    assert (response.http_request.headers[http_constants.HttpHeaders.ThroughputBucket]
            == str(request_throughput_bucket_number))"""


CREATE_ITEM_AIO_HEADERS = LegacyFileSpec(
    op="create_item",
    surface="aio",
    filename="test_headers.py",
    class_name="TestHeadersAsync",
    db_id_prefix="legacy_headers_async",
    license_style="mit",
    cosmos_imports=("PartitionKey", "http_constants"),
    module_code=_HEADERS_MODULE_CODE_AIO,
    docstring="""\
Async ``test_container_create_item_throughput_bucket`` test against
the ``_backend="rust"`` path.

The other methods in the source ``TestHeadersAsync`` class cover other
operations; they belong to their own operations' ``legacy/`` folders.

Self-contained: builds its own database + container in ``asyncSetUp``
and deletes them in ``asyncTearDown``. The class name and method name
match the source at ``tests/test_headers_async.py`` so test IDs differ
only by path.

Run with::

    pytest --noconftest tests/create_item/aio/legacy/test_headers.py -v""",
    methods=(
        LegacyMethod(
            name="test_container_create_item_throughput_bucket_async",
            source="tests/test_headers_async.py::TestHeadersAsync.test_container_create_item_throughput_bucket_async",
            body="""\
        await self.container.create_item(
            body={'id': '1' + str(uuid.uuid4()), 'pk': 'mypk'},
            throughput_bucket=request_throughput_bucket_number,
            raw_response_hook=request_raw_response_hook)""",
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
        "tests/read_item/sync/legacy/test_none_options.py",
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
        "tests/create_item/aio/legacy/test_none_options.py",
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
            pre_trigger_include=None,
            post_trigger_include=None,
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

