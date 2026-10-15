from pathlib import Path

from azpysdk.pylint import (
    SNIPPET_SAMPLE_IMPORT_DISABLES,
    get_snippet_aware_sample_pylint_commands,
    get_test_pylint_command,
)


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


def test_get_test_pylint_command_supports_namespace_test_directories(tmp_path):
    tests_dir = tmp_path / "tests"
    nested_dir = tests_dir / "nested"
    nested_dir.mkdir(parents=True)
    test_file = tests_dir / "test_client.py"
    helper = nested_dir / "helper.py"
    for path in (test_file, helper):
        path.write_text("pass\n", encoding="utf-8")
    (tests_dir / "README.md").write_text("Test documentation\n", encoding="utf-8")

    assert get_test_pylint_command("python", "test_pylintrc", str(tests_dir)) == [
        "python",
        "-m",
        "pylint",
        "--rcfile=test_pylintrc",
        "--output-format=parseable",
        *sorted([str(test_file), str(helper)]),
    ]


def test_get_test_pylint_command_ignores_empty_directories(tmp_path):
    assert get_test_pylint_command("python", "test_pylintrc", str(tmp_path)) == []
