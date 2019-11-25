# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
import os
import datetime
import sys

from azure.storage.blob import (
    BlobServiceClient,
    ContainerClient,
    BlobClient,
)
import tests.settings_real as settings

# Warning:
# This script will take a while to run with everything enabled.
# Edit the lists below to enable only the blob sizes and connection
# counts that you are interested in.

# NAME, SIZE (MB), +ADD SIZE (B)
LOCAL_BLOCK_BLOB_FILES = [
    ('BLOC-0080M+000B', 80, 0),
    ('BLOC-0080M+013B', 80, 13),
    ('BLOC-0500M+000B', 500, 0),
    ('BLOC-2500M+000B', 2500, 0),
]
LOCAL_PAGE_BLOB_FILES = [
    ('PAGE-0072M+000B', 72, 0),
    ('PAGE-0072M+512B', 72, 512),
    ('PAGE-0500M+000B', 500, 0),
    ('PAGE-2500M+000B', 2500, 0),
]

LOCAL_APPEND_BLOB_FILES = [
    ('APPD-0072M+000B', 80, 0),
    ('APPD-0072M+512B', 80, 13),
    ('APPD-0500M+000B', 500, 0),
    ('APPD-2500M+000B', 2500, 0),
]

CONNECTION_COUNTS = [1, 2, 5, 10, 50]

CONTAINER_NAME = 'performance'


def input_file(name):
    return 'input-' + name


def output_file(name):
    return 'output-' + name

def create_random_content_file(name, size_in_megs, additional_byte_count=0):
    file_name = input_file(name)
    if not os.path.exists(file_name):
        print('generating {0}'.format(name))
        with open(file_name, 'wb') as stream:
            for i in range(size_in_megs):
                stream.write(os.urandom(1048576))
            if additional_byte_count > 0:
                stream.write(os.urandom(additional_byte_count))

def upload_blob(service, name, connections):
    blob_name = name
    file_name = input_file(name)
    sys.stdout.write('\tUp:')
    start_time = datetime.datetime.now()
    if isinstance(service, BlockBlobService):
        service.create_blob_from_path(
            CONTAINER_NAME, blob_name, file_name, max_concurrency=connections)
    elif isinstance(service, PageBlobService):
        service.create_blob_from_path(
            CONTAINER_NAME, blob_name, file_name, max_concurrency=connections)
    elif isinstance(service, AppendBlobService):
        service.append_blob_from_path(
            CONTAINER_NAME, blob_name, file_name, max_concurrency=connections)
    else:
        service.create_blob_from_path(
            CONTAINER_NAME, blob_name, file_name, max_concurrency=connections)
    elapsed_time = datetime.datetime.now() - start_time
    sys.stdout.write('{0}s'.format(elapsed_time.total_seconds()))

def download_blob(service, name, connections):
    blob_name = name
    target_file_name = output_file(name)
    if os.path.exists(target_file_name):
        os.remove(target_file_name)
    sys.stdout.write('\tDn:')
    start_time = datetime.datetime.now()
    service.get_blob_to_path(
        CONTAINER_NAME, blob_name, target_file_name, max_concurrency=connections)
    elapsed_time = datetime.datetime.now() - start_time
    sys.stdout.write('{0}s'.format(elapsed_time.total_seconds()))

def file_contents_equal(first_file_path, second_file_path):
    first_size = os.path.getsize(first_file_path);
    second_size = os.path.getsize(second_file_path)
    if first_size != second_size:
        return False
    with open(first_file_path, 'rb') as first_stream:
        with open(second_file_path, 'rb') as second_stream:
            while True:
                first_data = first_stream.read(1048576)
                second_data = second_stream.read(1048576)
                if first_data != second_data:
                    return False
                if not first_data:
                    return True

def compare_files(name):
    first_file_path = input_file(name)
    second_file_path = output_file(name)
    sys.stdout.write('\tCmp:')
    if file_contents_equal(first_file_path, second_file_path):
        sys.stdout.write('ok')
    else:
        sys.stdout.write('ERR!')

def process(service, blobs, counts):
    for name, size_in_megs, additional in blobs:
        create_random_content_file(name, size_in_megs, additional)

    for name, _, _ in blobs:
        for max_conn in counts:
            sys.stdout.write('{0}\tParallel:{1}'.format(name, max_conn))
            upload_blob(service, name, max_conn)
            download_blob(service, name, max_conn)
            compare_files(name)
            print('')
        print('')

def main():
    bbs = BlockBlobService(settings.STORAGE_ACCOUNT_NAME, settings.STORAGE_ACCOUNT_KEY)
    pbs = PageBlobService(settings.STORAGE_ACCOUNT_NAME, settings.STORAGE_ACCOUNT_KEY)
    abs = AppendBlobService(settings.STORAGE_ACCOUNT_NAME, settings.STORAGE_ACCOUNT_KEY)
    service.create_container(CONTAINER_NAME)

    process(bbs, LOCAL_BLOCK_BLOB_FILES, CONNECTION_COUNTS)
    process(pbs, LOCAL_PAGE_BLOB_FILES, CONNECTION_COUNTS)
    process(abs, LOCAL_APPEND_BLOB_FILES, CONNECTION_COUNTS)

if __name__ == '__main__':
    main()
