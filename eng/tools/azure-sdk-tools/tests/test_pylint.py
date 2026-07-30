from pathlib import Path

from azpysdk.pylint import SNIPPET_SAMPLE_IMPORT_DISABLES, get_snippet_aware_sample_pylint_commands


def test_get_snippet_aware_sample_pylint_commands_separates_snippet_files(tmp_path):
    samples_dir = tmp_path / "samples"
    nested_dir = samples_dir / "nested"
    nested_dir.mkdir(parents=True)

    regular_sample = samples_dir / "regular.py"
    regular_sample.write_text("print('regular')\n", encoding="utf-8")

    snippet_sample = nested_dir / "snippet.py"
    snippet_sample.write_text(
        "# [START example]\nimport os\n# [END example]\n",
        encoding="utf-8",
    )

    commands = get_snippet_aware_sample_pylint_commands("python", "samples_pylintrc", str(samples_dir))

    assert commands == [
        [
            "python",
            "-m",
            "pylint",
            "--rcfile=samples_pylintrc",
            "--output-format=parseable",
            str(regular_sample),
        ],
        [
            "python",
            "-m",
            "pylint",
            "--rcfile=samples_pylintrc",
            "--output-format=parseable",
            f"--disable={','.join(SNIPPET_SAMPLE_IMPORT_DISABLES)}",
            str(snippet_sample),
        ],
    ]


def test_get_snippet_aware_sample_pylint_commands_ignores_non_python_files(tmp_path):
    samples_dir = tmp_path / "samples"
    samples_dir.mkdir()
    Path(samples_dir / "README.md").write_text("# [START example]\n", encoding="utf-8")

    assert get_snippet_aware_sample_pylint_commands("python", "samples_pylintrc", str(samples_dir)) == []


def test_get_snippet_aware_sample_pylint_commands_respects_ignore_patterns(tmp_path):
    """Files matching ignore-patterns in the rcfile must be excluded even when passed explicitly."""
    samples_dir = tmp_path / "samples"
    samples_dir.mkdir()

    # A normal sample that should be linted
    regular_sample = samples_dir / "sample_hello.py"
    regular_sample.write_text("print('hello')\n", encoding="utf-8")

    # conftest.py and setup.py match the ignore-patterns in samples_pylintrc
    conftest = samples_dir / "conftest.py"
    conftest.write_text("import pytest\n", encoding="utf-8")
    setup = samples_dir / "setup.py"
    setup.write_text("from setuptools import setup\n", encoding="utf-8")

    # Write a minimal rcfile with the same ignore-patterns as eng/samples_pylintrc
    rcfile = tmp_path / "samples_pylintrc"
    rcfile.write_text("[MASTER]\nignore-patterns=conftest,setup\n", encoding="utf-8")

    commands = get_snippet_aware_sample_pylint_commands("python", str(rcfile), str(samples_dir))

    # Only sample_hello.py should appear; conftest.py and setup.py must be excluded
    assert len(commands) == 1
    assert str(regular_sample) in commands[0]
    assert str(conftest) not in commands[0]
    assert str(setup) not in commands[0]
