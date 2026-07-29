from pathlib import Path

from azpysdk.pylint import SNIPPET_IMPORT_DISABLES, get_sample_pylint_commands


def test_get_sample_pylint_commands_separates_snippet_files(tmp_path):
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

    commands = get_sample_pylint_commands("python", "samples_pylintrc", str(samples_dir))

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
            f"--disable={','.join(SNIPPET_IMPORT_DISABLES)}",
            str(snippet_sample),
        ],
    ]


def test_get_sample_pylint_commands_ignores_non_python_files(tmp_path):
    samples_dir = tmp_path / "samples"
    samples_dir.mkdir()
    Path(samples_dir / "README.md").write_text("# [START example]\n", encoding="utf-8")

    assert get_sample_pylint_commands("python", "samples_pylintrc", str(samples_dir)) == []
