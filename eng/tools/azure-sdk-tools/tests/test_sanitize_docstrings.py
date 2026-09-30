from packaging_tools.generate_utils import (
    _TRIPLE_QUOTED_RE,
    _fix_triple_quoted,
    sanitize_generated_docstrings,
)


def _run(src: str) -> str:
    return _TRIPLE_QUOTED_RE.sub(_fix_triple_quoted, src)


def test_fixes_invalid_W_escape():
    src = '"""hi (Regex match [\\W_])"""'
    assert _run(src) == '"""hi (Regex match [\\\\W_])"""'


def test_fixes_other_invalid_escapes():
    # \d \s are also invalid Python escapes
    src = '"""\\d \\s \\p"""'
    assert _run(src) == '"""\\\\d \\\\s \\\\p"""'


def test_idempotent():
    once = _run('"""[\\W_]"""')
    assert _run(once) == once


def test_leaves_valid_escapes_alone():
    src = '"""line1\\nline2\\ttab \\\\backslash \\"quote\\""""'
    assert _run(src) == src


def test_leaves_raw_strings_alone():
    src = 'r"""[\\W_]"""'
    assert _run(src) == src


def test_leaves_byte_strings_alone():
    # Byte triple-quoted strings are rare in docstrings but must not be touched.
    # The regex matches them, but `_fix_triple_quoted` bails out because the
    # captured prefix contains `b`.
    src = 'b"""[\\W_]"""'
    assert _run(src) == src


def test_leaves_raw_fstring_alone_rf_prefix():
    # Regression: ``rf"""..."""`` was previously sanitized because the
    # lookbehind only saw ``f`` immediately before the quote.
    src = 'rf"""[\\W_]"""'
    assert _run(src) == src


def test_leaves_raw_fstring_alone_fr_prefix():
    src = 'fr"""[\\W_]"""'
    assert _run(src) == src


def test_leaves_raw_byte_string_alone_rb_prefix():
    src = 'rb"""[\\W_]"""'
    assert _run(src) == src


def test_leaves_raw_byte_string_alone_br_prefix():
    src = 'br"""[\\W_]"""'
    assert _run(src) == src


def test_leaves_raw_byte_string_alone_mixed_case_prefix():
    for src in ('Rb"""[\\W_]"""', 'bR"""[\\W_]"""', 'rF"""[\\W_]"""', 'Fr"""[\\W_]"""'):
        assert _run(src) == src


def test_leaves_single_quoted_strings_alone():
    # Generated docstrings are always triple-quoted; regex literals in
    # generated code use double-quoted strings and must not be modified.
    src = 'PATTERN = "\\W"'
    assert _run(src) == src


def test_single_triple_quoted_string():
    src = "'''(Regex match [\\W_])'''"
    assert _run(src) == "'''(Regex match [\\\\W_])'''"


def test_unicode_prefix_preserved():
    src = 'u"""[\\W_]"""'
    assert _run(src) == 'u"""[\\\\W_]"""'


def test_fstring_prefix_preserved():
    src = 'f"""[\\W_]"""'
    assert _run(src) == 'f"""[\\\\W_]"""'


def test_multiline_docstring():
    src = '"""line1\nHas a special character (Regex match [\\W_])\nline3"""'
    expected = '"""line1\nHas a special character (Regex match [\\\\W_])\nline3"""'
    assert _run(src) == expected


def test_sanitize_writes_only_changed_files(tmp_path):
    # Simulate an sdk package layout: <pkg>/azure/<ns>/_models.py + _patch.py
    pkg = tmp_path / "azure-mgmt-foo"
    ns = pkg / "azure" / "mgmt" / "foo"
    ns.mkdir(parents=True)
    models = ns / "_models.py"
    models.write_text(
        'class M:\n    """Has [\\W_]"""\n    pass\n',
        encoding="utf-8",
    )
    # _patch.py is hand-written; must never be touched even if it has invalid escapes
    patch = ns / "_patch.py"
    patch_src = '"""user-authored [\\W_]"""\n'
    patch.write_text(patch_src, encoding="utf-8")
    unchanged = ns / "_clean.py"
    unchanged_src = '"""nothing to fix here"""\n'
    unchanged.write_text(unchanged_src, encoding="utf-8")

    sanitize_generated_docstrings(str(pkg))

    assert models.read_text(encoding="utf-8") == 'class M:\n    """Has [\\\\W_]"""\n    pass\n'
    assert patch.read_text(encoding="utf-8") == patch_src
    assert unchanged.read_text(encoding="utf-8") == unchanged_src


def test_sanitize_is_idempotent_on_disk(tmp_path):
    pkg = tmp_path / "azure-mgmt-foo"
    ns = pkg / "azure" / "mgmt" / "foo"
    ns.mkdir(parents=True)
    models = ns / "_models.py"
    models.write_text('"""Has [\\W_]"""\n', encoding="utf-8")

    sanitize_generated_docstrings(str(pkg))
    first = models.read_text(encoding="utf-8")
    sanitize_generated_docstrings(str(pkg))
    assert models.read_text(encoding="utf-8") == first


def test_sanitize_missing_azure_dir_is_noop(tmp_path):
    # No azure/ subdir -> nothing to do, no crash.
    pkg = tmp_path / "azure-mgmt-foo"
    pkg.mkdir()
    sanitize_generated_docstrings(str(pkg))
