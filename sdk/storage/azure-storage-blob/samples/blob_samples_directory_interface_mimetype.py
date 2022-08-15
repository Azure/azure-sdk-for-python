# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

'''
FILE: blob_samples_directory_interface_mimetype.py
DESCRIPTION:
    This example is just adn addition to'blob_samples_directory_interface.py'.
    It is to just add functionality to add content-type to blob when
    uploading file. (e.g. 'text/html' is set when uploading .html files)
  USAGE: python blob_samples_directory_interface_mimetype.py CONTAINER_NAME
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
'''

import sys
import shutil
import glob
from blob_samples_directory_interface import DirectoryClient
import mimetypes
import os
from azure.storage.blob import ContentSettings

class DirectoryClientEx(DirectoryClient):
    # overriding upload_file method
    def upload_file(self, source, dest):
        '''
        Upload a single file to a path inside the container with content-type set
        '''
        content_type = mimetypes.guess_type(source)[0]
        print(f'Uploading {source} to {dest} (type: {content_type})')
        with open(source, 'rb') as data:
            self.client.upload_blob(name=dest, data=data, content_settings=ContentSettings(
                content_type=content_type))

# Sample setup

try:
    CONNECTION_STRING = os.environ['AZURE_STORAGE_CONNECTION_STRING']
except KeyError:
    print('AZURE_STORAGE_CONNECTION_STRING must be set')
    sys.exit(1)

try:
    CONTAINER_NAME = sys.argv[1]
except IndexError:
    print('usage: directory_interface.py CONTAINER_NAME')
    print('error: the following arguments are required: CONTAINER_NAME')
    sys.exit(1)

SAMPLE_DIRS = [
    'cats/calico',
    'cats/siamese',
    'cats/tabby'
]

SAMPLE_FILES = [
    'readme.txt',
    'cats/herds.txt',
    'cats/calico/anna.txt',
    'cats/calico/felix.txt',
    'cats/siamese/mocha.txt',
    'cats/tabby/bojangles.txt'
]

for path in SAMPLE_DIRS:
    os.makedirs(path, exist_ok=True)

for path in SAMPLE_FILES:
    with open(path, 'w') as file:
        file.write('content')

# Sample body

client = DirectoryClientEx(CONNECTION_STRING, CONTAINER_NAME)

# Upload a single file to the container. The destination must be a path
# including the destination file name.
#
# After this call, the container will look like:
#   cat-herding/
#     readme.txt
client.upload('readme.txt', 'cat-herding/readme.txt')
files = client.ls_files('', recursive=True)
print(files)

# Upload a directory to the container with a path prefix. The directory
# structure will be preserved inside the path prefix.
#
# After this call, the container will look like:
#   cat-herding/
#     readme.txt
#     cats/
#       herds.txt
#       calico/
#         anna.txt
#         felix.txt
#       siamese/
#         mocha.txt
#       tabby/
#         bojangles.txt
client.upload('cats', 'cat-herding')
files = client.ls_files('', recursive=True)
print(files)

# List files in a single directory
# Returns:
# ['herds.txt']
files = client.ls_files('cat-herding/cats')
print(files)

# List files in a directory recursively
# Returns:
# [
#   'herds.txt',
#   'calico/anna.txt',
#   'calico/felix.txt',
#   'siamese/mocha.txt',
#   'tabby/bojangles.txt'
# ]
files = client.ls_files('cat-herding/cats', recursive=True)
print(files)

# List directories in a single directory
# Returns:
# ['calico', 'siamese', 'tabby']
dirs = client.ls_dirs('cat-herding/cats')
print(dirs)

# List files in a directory recursively
# Returns:
# ['cats', 'cats/calico', 'cats/siamese', 'cats/tabby']
dirs = client.ls_dirs('cat-herding', recursive=True)
print(dirs)

# Download a single file to a location on disk, specifying the destination file
# name. When the destination does not end with a slash '/' and is not a relative
# path specifier (e.g. '.', '..', '../..', etc), the destination will be
# interpreted as a full path including the file name. If intermediate
# directories in the destination do not exist they will be created.
#
# After this call, your working directory will look like:
#   downloads/
#     cat-info.txt
client.download('cat-herding/readme.txt', 'downloads/cat-info.txt')
print(glob.glob('downloads/**', recursive=True))

# Download a single file to a folder on disk, preserving the original file name.
# When the destination ends with a slash '/' or is a relative path specifier
# (e.g. '.', '..', '../..', etc), the destination will be interpreted as a
# directory name and the specified file will be saved within the destination
# directory. If intermediate directories in the destination do not exist they
# will be created.
#
# After this call, your working directory will look like:
#   downloads/
#     cat-info.txt
#     herd-info/
#       herds.txt
client.download('cat-herding/cats/herds.txt', 'downloads/herd-info/')
print(glob.glob('downloads/**', recursive=True))

# Download a directory to a folder on disk. The destination is always
# interpreted as a directory name. The directory structure will be preserved
# inside destination folder. If intermediate directories in the destination do
# not exist they will be created.
#
# After this call, your working directory will look like:
#   downloads/
#     cat-data/
#       cats/
#         herds.txt
#         calico/
#          anna.txt
#          felix.txt
#         siamese/
#           mocha.txt
#         tabby/
#           bojangles.txt
#     cat-info.txt
#     herd-info/
#       herds.txt
client.download('cat-herding/cats', 'downloads/cat-data')
print(glob.glob('downloads/**', recursive=True))

# Delete a single file from the container
#
# After this call, the container will look like:
#   cat-herding/
#     readme.txt
#     cats/
#       herds.txt
#       calico/
#         anna.txt
#       siamese/
#         mocha.txt
#       tabby/
#         bojangles.txt
client.rm('cat-herding/cats/calico/felix.txt')
files = client.ls_files('', recursive=True)
print(files)

# Delete files in a directory recursively. This is equivalent to
# client.rmdir('cat-herding/cats')
#
# After this call, the container will look like:
#   cat-herding/
#     readme.txt
client.rm('cat-herding/cats', recursive=True)
files = client.ls_files('', recursive=True)
print(files)

# Delete files in a directory recursively. This is equivalent to
# client.rm('cat-herding', recursive=True)
#
# After this call, the container will be empty.
client.rmdir('cat-herding')
files = client.ls_files('', recursive=True)
print(files)

# Sample cleanup

shutil.rmtree('downloads')
shutil.rmtree('cats')
os.remove('readme.txt')
