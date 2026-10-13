import hashlib
import os
from io import BytesIO
from unittest.mock import Mock
from zipfile import ZipFile

import nltk
import pytest
import requests

from azure.ai.evaluation._common.utils import nltk_tokenize

from tests import conftest as test_config


def _archive_contents(files):
    stream = BytesIO()
    with ZipFile(stream, "w") as archive:
        for name, contents in files.items():
            archive.writestr(name, contents)
    return stream.getvalue()


def _pin_test_archive(monkeypatch, contents, *, unpack=True):
    monkeypatch.setattr(
        test_config,
        "_NLTK_TEST_PACKAGES",
        {"tokenizers/punkt_tab.zip": (hashlib.sha256(contents).hexdigest(), unpack)},
    )


def _mock_download(monkeypatch, contents, *, status_code=200):
    response = requests.Response()
    response.status_code = status_code
    response.raw = BytesIO(contents)
    response.url = "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt_tab.zip"
    download = Mock(return_value=response)
    monkeypatch.setattr(test_config.requests, "get", download)
    return download


@pytest.mark.unittest
class TestNltkDataSetup:
    @pytest.mark.parametrize("unpack", [True, False])
    def test_downloads_and_caches_verified_data(self, tmp_path, monkeypatch, unpack):
        contents = _archive_contents({"punkt_tab/english/abbrev_types.txt": "example"})
        _pin_test_archive(monkeypatch, contents, unpack=unpack)
        download = _mock_download(monkeypatch, contents)

        test_config._prepare_nltk_test_data(tmp_path)

        assert (tmp_path / "tokenizers" / "punkt_tab.zip").read_bytes() == contents
        assert (tmp_path / "tokenizers" / "punkt_tab" / "english" / "abbrev_types.txt").exists() is unpack
        download.assert_called_once_with(
            "https://raw.githubusercontent.com/nltk/nltk_data/gh-pages/packages/tokenizers/punkt_tab.zip",
            timeout=60,
            allow_redirects=False,
        )

        test_config._prepare_nltk_test_data(tmp_path)

        assert download.call_count == 1
        assert not (tmp_path / "tokenizers" / "punkt_tab.zip.tmp").exists()

    def test_repairs_incomplete_extraction_without_downloading(self, tmp_path, monkeypatch):
        contents = _archive_contents(
            {"punkt_tab/english/abbrev_types.txt": "example", "punkt_tab/english/collocations.tab": "example"}
        )
        _pin_test_archive(monkeypatch, contents)
        download = _mock_download(monkeypatch, contents)
        test_config._prepare_nltk_test_data(tmp_path)
        missing_file = tmp_path / "tokenizers" / "punkt_tab" / "english" / "collocations.tab"
        missing_file.unlink()

        test_config._prepare_nltk_test_data(tmp_path)

        assert missing_file.read_text() == "example"
        assert download.call_count == 1

    @pytest.mark.parametrize("cached", [True, False])
    def test_rejects_checksum_mismatch(self, tmp_path, monkeypatch, cached):
        contents = _archive_contents({"punkt_tab/english/abbrev_types.txt": "example"})
        _pin_test_archive(monkeypatch, contents)
        download = _mock_download(monkeypatch, b"invalid archive")
        archive_path = tmp_path / "tokenizers" / "punkt_tab.zip"
        if cached:
            archive_path.parent.mkdir()
            archive_path.write_bytes(b"invalid archive")

        with pytest.raises(RuntimeError, match="SHA-256 checksum mismatch"):
            test_config._prepare_nltk_test_data(tmp_path)

        assert not (tmp_path / "tokenizers" / "punkt_tab").exists()
        assert archive_path.exists() is cached
        assert download.call_count == (0 if cached else 1)

    @pytest.mark.parametrize("status_code", [301, 403])
    def test_rejects_failed_or_redirected_download(self, tmp_path, monkeypatch, status_code):
        contents = _archive_contents({"punkt_tab/english/abbrev_types.txt": "example"})
        _pin_test_archive(monkeypatch, contents)
        _mock_download(monkeypatch, contents, status_code=status_code)

        expected_error = requests.HTTPError if status_code == 403 else RuntimeError
        with pytest.raises(expected_error, match=str(status_code)):
            test_config._prepare_nltk_test_data(tmp_path)

        assert not (tmp_path / "tokenizers").exists()

    @pytest.mark.parametrize(
        "member_name",
        [
            "../outside.txt",
            "punkt_tab/../outside.txt",
            r"punkt_tab\..\outside.txt",
            "/outside.txt",
            "C:/outside.txt",
            "punkt_tab/file.txt:stream",
        ],
    )
    def test_rejects_unsafe_archive_members_before_extraction(self, tmp_path, monkeypatch, member_name):
        contents = _archive_contents({"punkt_tab/valid.txt": "inside", member_name: "outside"})
        _pin_test_archive(monkeypatch, contents)
        _mock_download(monkeypatch, contents)

        with pytest.raises(RuntimeError, match="Unexpected member"):
            test_config._prepare_nltk_test_data(tmp_path)

        assert not (tmp_path / "tokenizers" / "punkt_tab").exists()
        assert not (tmp_path / "outside.txt").exists()

    def test_fixture_preserves_and_restores_existing_data_paths(self, tmp_path, monkeypatch):
        original_path = str(tmp_path / "existing_data")
        monkeypatch.setenv("NLTK_DATA", original_path)
        monkeypatch.setattr(nltk.data, "path", [original_path])
        prepare = Mock()
        monkeypatch.setattr(test_config, "_prepare_nltk_test_data", prepare)
        fixture = test_config.ensure_nltk_data.__wrapped__()

        next(fixture)
        try:
            prepared_path = nltk.data.path[0]
            assert os.environ["NLTK_DATA"] == f"{prepared_path}{os.pathsep}{original_path}"
            assert nltk.data.path == [prepared_path, original_path]
            prepare.assert_called_once()
            assert str(prepare.call_args.args[0]) == prepared_path
        finally:
            fixture.close()

        assert os.environ["NLTK_DATA"] == original_path
        assert nltk.data.path == [original_path]

    def test_tokenization_uses_prepared_data_with_no_proxy(self, monkeypatch):
        monkeypatch.setenv("NO_PROXY", "localhost,127.0.0.1")
        monkeypatch.setattr(nltk.data, "path", [nltk.data.path[0]])
        download = Mock(side_effect=AssertionError("Prepared test data must not invoke the NLTK downloader."))
        monkeypatch.setattr(nltk, "download", download)

        assert nltk_tokenize("The capital of China is Beijing.") == [
            "The",
            "capital",
            "of",
            "China",
            "is",
            "Beijing",
            ".",
        ]
        assert nltk_tokenize("The capital of China is \u5317\u4eac.") == [
            "The",
            "capital",
            "of",
            "China",
            "is",
            "\u5317\u4eac",
            ".",
        ]
        download.assert_not_called()
