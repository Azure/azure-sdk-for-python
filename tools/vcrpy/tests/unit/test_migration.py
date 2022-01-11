import filecmp
import json
import shutil
import yaml

import vcr.migration

# Use the libYAML versions if possible
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader


def test_try_migrate_with_json(tmpdir):
    cassette = tmpdir.join("cassette.json").strpath
    shutil.copy("tests/fixtures/migration/old_cassette.json", cassette)
    assert vcr.migration.try_migrate(cassette)
    with open("tests/fixtures/migration/new_cassette.json", "r") as f:
        expected_json = json.load(f)
    with open(cassette, "r") as f:
        actual_json = json.load(f)
    assert actual_json == expected_json


def test_try_migrate_with_yaml(tmpdir):
    cassette = tmpdir.join("cassette.yaml").strpath
    shutil.copy("tests/fixtures/migration/old_cassette.yaml", cassette)
    assert vcr.migration.try_migrate(cassette)
    with open("tests/fixtures/migration/new_cassette.yaml", "r") as f:
        expected_yaml = yaml.load(f, Loader=Loader)
    with open(cassette, "r") as f:
        actual_yaml = yaml.load(f, Loader=Loader)
    assert actual_yaml == expected_yaml


def test_try_migrate_with_invalid_or_new_cassettes(tmpdir):
    cassette = tmpdir.join("cassette").strpath
    files = [
        "tests/fixtures/migration/not_cassette.txt",
        "tests/fixtures/migration/new_cassette.yaml",
        "tests/fixtures/migration/new_cassette.json",
    ]
    for file_path in files:
        shutil.copy(file_path, cassette)
        assert not vcr.migration.try_migrate(cassette)
        assert filecmp.cmp(cassette, file_path)  # shold not change file
