# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Keep smoke failures visible in test results without making service calls."""

import textwrap
import xml.etree.ElementTree as ET

import pytest

from smoke import test_smoke_scripts as smoke_runner

pytest_plugins = ["pytester"]


@pytest.fixture
def make_script(tmp_path, monkeypatch):
    monkeypatch.setattr(smoke_runner, "_have_binding", lambda: True)
    monkeypatch.setattr(smoke_runner, "_have_account", lambda: True)

    def write(body):
        script = tmp_path / "replace_item" / "smoke_test_rust_replace_item.py"
        script.parent.mkdir(exist_ok=True)
        script.write_text("def main():\n" + textwrap.indent(body, "    ") + "\n", encoding="utf-8")
        return script

    return write


@pytest.mark.parametrize("code", [1, 3, None])
def test_failed_smoke_includes_both_output_streams_rust(make_script, capfd, code):
    script = make_script(
        "import sys\n"
        "print('[3] guarded replace')\n"
        "print('FAIL: expected 412, got 200.', file=sys.stderr)\n"
        f"return {code!r}"
    )
    with pytest.raises(pytest.fail.Exception) as failure:
        smoke_runner.test_smoke_round_trip_rust(script, capfd)
    message = str(failure.value)
    assert f"replace_item smoke round trip failed (exit {code})" in message
    assert "Smoke stdout:\n[3] guarded replace" in message
    assert "Smoke stderr:\nFAIL: expected 412, got 200." in message


def test_successful_smoke_keeps_normal_capture_rust(make_script, capfd):
    script = make_script("print('OK round trip')\nreturn 0")
    smoke_runner.test_smoke_round_trip_rust(script, capfd)
    assert capfd.readouterr().out == "OK round trip\n"


def test_missing_operation_still_skips_rust(make_script, capfd):
    script = make_script("print('binding operation missing')\nreturn 2")
    with pytest.raises(pytest.skip.Exception, match="binding/op missing"):
        smoke_runner.test_smoke_round_trip_rust(script, capfd)
    assert capfd.readouterr().out == "binding operation missing\n"


@pytest.mark.parametrize("check", ["_have_binding", "_have_account"])
def test_missing_prerequisites_do_not_run_smoke_rust(make_script, monkeypatch, capfd, check):
    script = make_script("raise AssertionError('smoke must not run')")
    monkeypatch.setattr(smoke_runner, check, lambda: False)
    with pytest.raises(pytest.skip.Exception):
        smoke_runner.test_smoke_round_trip_rust(script, capfd)


def test_unhandled_smoke_exception_still_propagates_rust(make_script, capfd):
    script = make_script("raise RuntimeError('uncaught smoke error')")
    with pytest.raises(RuntimeError, match="uncaught smoke error"):
        smoke_runner.test_smoke_round_trip_rust(script, capfd)


def test_junit_failure_contains_script_output_without_junit_logging_rust(make_script, pytester):
    script = make_script(
        "import sys\n"
        "print('[1] create new id')\n"
        "print('FAIL on create: diagnostic detail', file=sys.stderr)\n"
        "return 1"
    )
    pytester.makepyfile(test_reporting=f"""
        from pathlib import Path
        from smoke import test_smoke_scripts as smoke_runner

        def test_failed_smoke(monkeypatch, capfd):
            monkeypatch.setattr(smoke_runner, "_have_binding", lambda: True)
            monkeypatch.setattr(smoke_runner, "_have_account", lambda: True)
            smoke_runner.test_smoke_round_trip_rust(Path({str(script)!r}), capfd)
        """)
    report = pytester.path / "pytest.xml"
    outcome = pytester.runpytest_inprocess(
        "--noconftest", "-p", "no:cacheprovider", "--junitxml", str(report), "-o", "junit_logging=no"
    )
    outcome.assert_outcomes(failed=1)
    failure = ET.parse(report).find(".//testcase/failure")
    assert failure is not None
    assert failure.text is not None
    assert "replace_item smoke round trip failed (exit 1)" in failure.get("message", "")
    assert "[1] create new id" in failure.text
    assert "FAIL on create: diagnostic detail" in failure.text
