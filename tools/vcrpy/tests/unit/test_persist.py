import pytest

from vcr.persisters.filesystem import FilesystemPersister
from vcr.serializers import jsonserializer, yamlserializer


@pytest.mark.parametrize(
    "cassette_path, serializer",
    [
        ("tests/fixtures/migration/old_cassette.json", jsonserializer),
        ("tests/fixtures/migration/old_cassette.yaml", yamlserializer),
    ],
)
def test_load_cassette_with_old_cassettes(cassette_path, serializer):
    with pytest.raises(ValueError) as excinfo:
        FilesystemPersister.load_cassette(cassette_path, serializer)
    assert "run the migration script" in excinfo.exconly()


@pytest.mark.parametrize(
    "cassette_path, serializer",
    [
        ("tests/fixtures/migration/not_cassette.txt", jsonserializer),
        ("tests/fixtures/migration/not_cassette.txt", yamlserializer),
    ],
)
def test_load_cassette_with_invalid_cassettes(cassette_path, serializer):
    with pytest.raises(Exception) as excinfo:
        FilesystemPersister.load_cassette(cassette_path, serializer)
    assert "run the migration script" not in excinfo.exconly()
