import copy
import logging
import os
from pathlib import Path
from typing import Iterator

import pytest
from azure.ai.generative.index._documents.chunking import DocumentSource
from azure.ai.generative.index._documents.cracking import crack_documents, file_extension_loaders

logger = logging.getLogger(__name__)

extension_loaders = copy.deepcopy(file_extension_loaders)

def create_local_source_iterator(source_dir: Path) -> Iterator[DocumentSource]:
    if not source_dir.exists():
        raise ValueError(f"Source directory does not exist: {source_dir}")
    for file in source_dir.iterdir():
        if file.is_file():
            relative_path = file.relative_to(source_dir)
            url = str(relative_path)
        yield DocumentSource(
            path=file,
            filename=file.name,
            url=url,
            mtime=file.stat().st_mtime
        )

def test_crack_and_chunk_pdf(test_data_dir: Path):
    #set up local document source
    source_dir = (test_data_dir / "documents" / "incremental_many_docs" / "first_run" / "pdfs").resolve()

    #crack document
    chunked_documents = crack_documents(
        sources=create_local_source_iterator(source_dir),
        file_extension_loaders=extension_loaders
    )

    # verify the chunked documents
    chunk_count = 0
    for chunk in chunked_documents:
        chunk_count += 1
        assert(chunk.get_metadata() is not None)
        assert(len(chunk.flatten()) > 0)

    # and there are 2 pdf files in current test data directory
    assert(chunk_count == 2)