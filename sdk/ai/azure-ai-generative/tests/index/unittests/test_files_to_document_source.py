import logging

from azure.ai.generative.index._documents.cracking import files_to_document_source

logger = logging.getLogger(__name__)


def test_files_to_document_source_folder(test_data_dir):
    folder_of_data_path = test_data_dir / "documents" / "incremental_many_docs" / "first_run"

    document_sources = list(files_to_document_source(folder_of_data_path))
    logger.debug(f"{document_sources = }")
    assert len(document_sources) > 1

    folder_of_data_str = str(folder_of_data_path)

    document_sources = list(files_to_document_source(folder_of_data_str))
    logger.debug(f"{document_sources = }")
    assert len(document_sources) > 1

    single_file_path = folder_of_data_path / "plain_text" / "no_heading.md"

    document_sources = list(files_to_document_source(single_file_path))
    logger.debug(f"{document_sources = }")
    assert len(document_sources) == 1

    single_file_str = str(single_file_path)

    document_sources = list(files_to_document_source(single_file_str))
    logger.debug(f"{document_sources = }")
    assert len(document_sources) == 1