# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import os
import json
from glob import glob
from typing import Iterator, Tuple, Any


def jsonl_file_iter(filepath: str) -> Iterator[Tuple[int, dict]]:
    '''Generate pool data from filepath, used to load from file iteratively.'''
    with open(filepath, 'r') as f:
        for idx, line in enumerate(f):
            if line.strip():
                yield idx, json.loads(line)


def resolve_file(dataset: str, filename: str) -> str:
    '''Resolve a file from a dataset and filename and assert only one file is found.'''
    if os.path.isfile(dataset):
        filenames = glob(dataset)
    else:
        path = os.path.join(dataset, filename)
        path = os.path.abspath(path)
        filenames = glob(path)
    assert len(filenames) == 1, \
        f'Expected 1 file for {filename}, found {len(filenames)}: {filenames} in {path}'
    return filenames[0]


def batched_iterator(iterator: Iterator[Any], batch_size: int) -> Iterator[Any]:
    '''Batch an iterator into a new iterator.'''
    batch = []
    for item in iterator:
        batch.append(item)
        if len(batch) == batch_size:
            yield batch
            batch = []
    if batch:
        yield batch
