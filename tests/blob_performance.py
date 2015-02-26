#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
import os
import datetime
import sys

from azure.storage import BlobService
from util import credentials

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


def upload_blob(service, name, connections, is_page_blob):
    blob_name = name
    file_name = input_file(name)
    sys.stdout.write('\tUp:')
    start_time = datetime.datetime.now()
    if is_page_blob:
        service.put_page_blob_from_path(
            CONTAINER_NAME, blob_name, file_name, max_connections=connections)
    else:
        service.put_block_blob_from_path(
            CONTAINER_NAME, blob_name, file_name, max_connections=connections)
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
        CONTAINER_NAME, blob_name, target_file_name, max_connections=connections)
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


def process(service, blobs, counts, is_page_blob):
    for name, size_in_megs, additional in blobs:
        create_random_content_file(name, size_in_megs, additional)

    for name, _, _ in blobs:
        for max_conn in counts:
            sys.stdout.write('{0}\tParallel:{1}'.format(name, max_conn))
            upload_blob(service, name, max_conn, is_page_blob)
            download_blob(service, name, max_conn)
            compare_files(name)
            print('')
        print('')


def main():
    service = BlobService(
        credentials.getStorageServicesName(),
        credentials.getStorageServicesKey(),
    )

    service.create_container(CONTAINER_NAME)

    process(service, LOCAL_BLOCK_BLOB_FILES, CONNECTION_COUNTS, is_page_blob=False)
    process(service, LOCAL_PAGE_BLOB_FILES, CONNECTION_COUNTS, is_page_blob=True)


if __name__ == '__main__':
    main()
