# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
"""Offline coverage for the tool that decides whether a full test run was acceptable.

The Rust path is run against the whole existing suite, and a short list of failures is
known about and signed off. The tool compares one run's failures against that list and
answers: nothing unexpected, something unexpected, or this run cannot be judged at all.

The third answer is why most of this file exists. The dangerous outcome is not a failure;
it is a run that never really happened being reported as clean -- the command died early,
collected nothing, or was interrupted, and the output was thin enough to look like
success. Several tests here feed in exactly those shapes and require a refusal.

The rest is about the exemption list being narrow. Entries must name one exact test, so
signing off a single known problem cannot quietly excuse everything near it.
"""
import importlib.util
import pathlib

import pytest

_ROOT = pathlib.Path(__file__).resolve().parents[2]
_SCRIPT = _ROOT / "scripts" / "v5" / "check_known_failures.py"
_spec = importlib.util.spec_from_file_location("check_known_failures", _SCRIPT)
ckf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ckf)

_KNOWN = "tests/test_query.py::QueryTests::test_query[West US]"
_FAILURE = "FAILED {} - AssertionError: expected result\n".format(_KNOWN)


def test_load_known_ids_preserves_case_and_parameters():
    """Reading the exemption list keeps the test name exactly, and accepts either path style.

    Comment lines and blank lines are ignored, so the list can explain itself. Path
    separators are made uniform, because the list is written on one operating system and
    read on another. Nothing else about the name is touched: the parameter in brackets,
    including its spaces and capitals, is part of which test this is.
    """
    ids = ckf.load_known_ids("# Reviewed limitation\n\n" + _KNOWN.replace("/", "\\") + "\n")
    assert ids == [_KNOWN]


@pytest.mark.parametrize("entry", ["query", "feed", "resource_token", "tests/test_query.py"])
def test_rejects_broad_known_failure_entries(entry):
    """An entry that would excuse more than one test is refused outright.

    Three of these are bare topic words and the fourth is a whole file. Any of them would
    turn a list of individually reviewed problems into a blanket exemption, and a new
    failure in that area would then never be reported.

    Refusing at load time rather than ignoring the line matters: a silently ignored entry
    would make someone believe a failure was signed off when it was not.
    """
    with pytest.raises(ValueError, match="exact"):
        ckf.load_known_ids(entry)


def test_matching_is_exact_not_a_feature_substring_or_case_fold():
    """A failure is excused only by its exact name, with one deliberate exception.

    Four failures are offered against a list holding one name. Only the identical one is
    excused. The other three are the near misses that a looser comparison would wrongly
    let through: the same name with something appended, the same name in lower case, and
    a different test in the same area.

    The exception is path separators, checked last: the same test written in the other
    operating system's style is still the same test, because the list and the run may
    come from different machines.
    """
    failures = [
        _KNOWN,
        _KNOWN + "-different",
        _KNOWN.lower(),
        "tests/test_feed.py::FeedTests::test_new_regression",
    ]
    assert ckf.classify(failures, [_KNOWN]) == ([_KNOWN], failures[1:])
    assert ckf.classify([_KNOWN.replace("/", "\\")], [_KNOWN])[1] == []


def test_summary_ids_preserve_spaces_in_parameters_and_strip_error_text():
    """Test names are read out of the run's output without the error message attached.

    Each line holds a name followed by a dash and a description of what went wrong. Only
    the name is wanted, and cutting at the wrong dash would lose part of it, since names
    can contain dashes inside their parameters.

    Both wordings count. A test that failed and a test whose setup or cleanup broke are
    different events, but both mean this run did not come out clean.
    """
    text = _FAILURE + "ERROR tests/test_item.py::Items::test_setup - RuntimeError\n"
    assert ckf.failed_ids_from_transcript(text) == [
        _KNOWN, "tests/test_item.py::Items::test_setup",
    ]


@pytest.mark.parametrize(
    "text, exit_code",
    [
        ("", 0),
        ("collected 10 items\n", 0),
        ("1 passed in 0.01s\nInterrupted", 0),
        ("no tests ran in 0.01s", 5),
        ("2 skipped in 0.01s", 0),
        ("2 deselected in 0.01s", 0),
        ("1 passed in 0.01s", 1),
        ("1 passed in 0.01s", 2),
        ("1 passed in 0.01s", 3),
        ("1 passed in 0.01s", 4),
        (_FAILURE + "1 failed in 0.01s", 0),
        ("1 failed in 0.01s", 1),
        (_FAILURE + "2 failed in 0.01s", 1),
        (_FAILURE + "1 passed in 0.01s", 0),
        ("1 passed, 1 passed in 0.01s", 0),
        ("unknown outcome in 0.01s", 0),
    ],
)
def test_invalid_runs_never_look_clean(text, exit_code):
    """Sixteen ways a run can be unjudgeable, and every one of them is refused.

    They fall into groups. Output with no final tally at all: nothing, a run that only
    listed tests, and one whose tally is there but was followed by an interruption
    notice. A process that did not finish normally, including the code meaning no tests
    ran and the ones meaning wrong usage or a crash. A tally where nothing actually
    executed, everything having been skipped or filtered out.

    Then the disagreements, which are the subtle ones. The tally and the exit code
    contradict each other. The tally claims a number of failures that does not match how
    many were actually named. The same word is counted twice, which means two runs' output
    ended up in one file. Or a word nobody recognizes, which means the format has moved on
    and the tool must say so rather than guess.

    Every one of these could otherwise be reported as a clean run.
    """
    with pytest.raises(ValueError):
        ckf.validate_run(text, exit_code)


@pytest.mark.parametrize(
    "summary",
    [
        "1 passed in 0.01s",
        "===== 1 passed, 1 skipped, 2 deselected, 1 warning in 0.01s =====",
        "=== 1 passed in 4000.01s (1:06:40) ===",
        "\x1b[32m1 passed in 0.01s\x1b[0m",
    ],
)
def test_complete_successful_runs_are_accepted(summary):
    """Real successful output is accepted in each of the forms it actually arrives in.

    Being strict is only useful if genuine runs still pass. These are the real variations:
    a bare tally, one padded with equals signs and carrying several counts, one with an
    elapsed time long enough that pytest adds the duration in hours, and one still
    carrying the colour codes a terminal adds.

    That last case is why colour is stripped before anything is read. Output captured
    from a build pipeline usually has it, and treating it as part of the text would make
    every real run unjudgeable.
    """
    assert ckf.validate_run(summary, 0) == []


def test_failure_and_teardown_error_counts_are_not_deduplicated():
    """One test that both failed and broke during cleanup counts as two events, not one.

    The name appears twice and both are kept, because the tally counts them separately
    and the two numbers have to agree. Collapsing them to one would make the comparison
    fail on a real and entirely ordinary run.

    It also means being exempt covers the test, not one of its two problems: a test on
    the list that fails and then breaks in cleanup is still fully accounted for.
    """
    text = _FAILURE + "ERROR " + _KNOWN + " - teardown\n1 failed, 1 error in 0.01s"
    assert ckf.validate_run(text, 1) == [_KNOWN, _KNOWN]


@pytest.mark.parametrize("encoding", ["utf-8", "utf-8-sig", "utf-16"])
def test_cli_accepts_complete_exempt_failure_in_powershell_encodings(tmp_path, encoding, capsys):
    """A captured run is read correctly whichever way the shell wrote the file.

    PowerShell writes captured output in several encodings depending on how it was
    redirected, including one that is two bytes per character. The tool detects that from
    the first bytes of the file rather than assuming, because reading it the wrong way
    turns every line into nonsense and a perfectly good run is reported as unjudgeable.

    The run here has one failure which is on the exemption list, so the answer is success
    with a note saying one failure was excused -- not silence, so nobody has to guess
    whether the list was consulted.
    """
    transcript = tmp_path / "run.txt"
    known = tmp_path / "known.txt"
    transcript.write_text(_FAILURE + "1 failed in 0.01s", encoding=encoding)
    known.write_text(_KNOWN, encoding="utf-8")
    assert ckf.main([str(transcript), str(known), "--pytest-exit-code", "1"]) == 0
    assert "1 explicitly exempt" in capsys.readouterr().out


def test_cli_reports_unexplained_failure(tmp_path, capsys):
    """A failure nobody signed off is reported by name, and the run is judged a failure.

    Same run as above but with an empty exemption list. The name has to appear in the
    error output: whoever reads the build log needs to know which test, not just that
    something went wrong.
    """
    transcript = tmp_path / "run.txt"
    known = tmp_path / "known.txt"
    transcript.write_text(_FAILURE + "1 failed in 0.01s", encoding="utf-8")
    known.write_text("# No exemptions\n", encoding="utf-8")
    assert ckf.main([str(transcript), str(known), "--pytest-exit-code", "1"]) == 1
    assert _KNOWN in capsys.readouterr().err


def test_cli_rejects_empty_transcript_without_printing_success(tmp_path, capsys):
    """An empty file is rejected, and nothing resembling success is printed.

    The third answer gets its own result code, distinct from both clean and failing, so a
    build step can tell "this run was fine" apart from "this run could not be judged".

    The check that normal output is completely empty is deliberate. A success message
    printed alongside the refusal would be the exact thing this tool exists to prevent:
    something scanning the log for a reassuring line and finding one.
    """
    transcript = tmp_path / "run.txt"
    transcript.write_text("", encoding="utf-8")
    assert ckf.main([str(transcript), "--pytest-exit-code", "0"]) == 2
    output = capsys.readouterr()
    assert "INVALID" in output.err
    assert not output.out


def test_cli_requires_real_pytest_exit_code():
    """The tool refuses to run unless it is told how the test process actually ended.

    There is no default. Without the real exit code the tool could only read the captured
    text, and text alone cannot show that the process finished normally -- which is half
    of what it checks. Leaving it out is a mistake in how the tool was called, so it
    stops immediately rather than judging the run on partial information.
    """
    with pytest.raises(SystemExit) as error:
        ckf.main(["run.txt"])
    assert error.value.code == 2


def test_checked_in_allowlist_does_not_exempt_unreviewed_failures():
    """The real exemption list in this repository excuses nothing it was not meant to.

    Every other test here uses made-up input. This one loads the file actually committed
    and offers it two failures that are not on it. Both must come back unexcused.

    It is a check on the file as much as on the tool: if someone added a broad entry, or
    one whose name happened to cover more than intended, this notices.
    """
    ids = ckf.load_known_ids((_ROOT / "tests" / "known_rust_failures.txt").read_text(encoding="utf-8"))
    failures = [
        "tests/test_query.py::QueryTests::test_unreviewed_regression",
        "tests/test_feed.py::FeedTests::test_unreviewed_regression",
    ]
    assert ckf.classify(failures, ids) == ([], failures)
