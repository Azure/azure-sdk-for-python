# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

'''
FILE: blob_samples_directory_interface.py
DESCRIPTION:
    This example shows how to perform common filesystem-like operations on a
    container. This includes uploading and downloading files to and from the
    container with an optional prefix, listing files in the container both at
    a single level and recursively, and deleting files in the container either
    individually or recursively.

    To run this sample, provide the name of the storage container to operate on
    as the script argument (e.g. `python3 directory_interface.py my-container`).
    This sample expects that the `AZURE_STORAGE_CONNECTION_STRING` environment
    variable is set. It SHOULD NOT be hardcoded in any code derived from this
    sample.
  USAGE: python blob_samples_directory_interface.py CONTAINER_NAME
    Set the environment variables with your own values before running the sample:
    1) AZURE_STORAGE_CONNECTION_STRING - the connection string to your storage account
'''

import os
from azure.storage.blob import BlobServiceClient

class DirectoryClient:
  def __init__(self, connection_string, container_name):
    service_client = BlobServiceClient.from_connection_string(connection_string)
    self.client = service_client.get_container_client(container_name)

  def upload(self, source, dest):
    '''
    Upload a file or directory to a path inside the container
    '''
    if (os.path.isdir(source)):
      self.upload_dir(source, dest)
    else:
      self.upload_file(source, dest)

  def upload_file(self, source, dest):
    '''
    Upload a single file to a path inside the container
    '''
    print(f'Uploading {source} to {dest}')
    with open(source, 'rb') as data:
      self.client.upload_blob(name=dest, data=data)

  def upload_dir(self, source, dest):
    '''
    Upload a directory to a path inside the container
    '''
    prefix = '' if dest == '' else dest + '/'
    prefix += os.path.basename(source) + '/'
    for root, dirs, files in os.walk(source):
      for name in files:
        dir_part = os.path.relpath(root, source)
        dir_part = '' if dir_part == '.' else dir_part + '/'
        file_path = os.path.join(root, name)
        blob_path = prefix + dir_part + name
        self.upload_file(file_path, blob_path)

  def download(self, source, dest):
    '''
    Download a file or directory to a path on the local filesystem
    '''
    if not dest:
      raise Exception('A destination must be provided')

    blobs = self.ls_files(source, recursive=True)
    if blobs:
      # if source is a directory, dest must also be a directory
      if not source == '' and not source.endswith('/'):
        source += '/'
      if not dest.endswith('/'):
        dest += '/'
      # append the directory name from source to the destination
      dest += os.path.basename(os.path.normpath(source)) + '/'

      blobs = [source + blob for blob in blobs]
      for blob in blobs:
        blob_dest = dest + os.path.relpath(blob, source)
        self.download_file(blob, blob_dest)
    else:
      self.download_file(source, dest)

  def download_file(self, source, dest):
    '''
    Download a single file to a path on the local filesystem
    '''
    # dest is a directory if ending with '/' or '.', otherwise it's a file
    if dest.endswith('.'):
      dest += '/'
    blob_dest = dest + os.path.basename(source) if dest.endswith('/') else dest

    print(f'Downloading {source} to {blob_dest}')
    os.makedirs(os.path.dirname(blob_dest), exist_ok=True)
    bc = self.client.get_blob_client(blob=source)
    if not dest.endswith('/'):
        with open(blob_dest, 'wb') as file:
          data = bc.download_blob()
          file.write(data.readall())

  def ls_files(self, path, recursive=False):
    '''
    List files under a path, optionally recursively
    '''
    if not path == '' and not path.endswith('/'):
      path += '/'

    blob_iter = self.client.list_blobs(name_starts_with=path)
    files = []
    for blob in blob_iter:
      relative_path = os.path.relpath(blob.name, path)
      if recursive or not '/' in relative_path:
        files.append(relative_path)
    return files

  def ls_dirs(self, path, recursive=False):
    '''
    List directories under a path, optionally recursively
    '''
    if not path == '' and not path.endswith('/'):
      path += '/'

    blob_iter = self.client.list_blobs(name_starts_with=path)
    dirs = []
    for blob in blob_iter:
      relative_dir = os.path.dirname(os.path.relpath(blob.name, path))
      if relative_dir and (recursive or not '/' in relative_dir) and not relative_dir in dirs:
        dirs.append(relative_dir)

    return dirs

  def rm(self, path, recursive=False):
    '''
    Remove a single file, or remove a path recursively
    '''
    if recursive:
      self.rmdir(path)
    else:
      print(f'Deleting {path}')
      self.client.delete_blob(path)

  def rmdir(self, path):
    '''
    Remove a directory and its contents recursively
    '''
    blobs = self.ls_files(path, recursive=True)
    if not blobs:
      return

    if not path == '' and not path.endswith('/'):
      path += '/'
    blobs = [path + blob for blob in blobs]
    print(f'Deleting {", ".join(blobs)}')
    self.client.delete_blobs(*blobs)

# Sample setup

import sys
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

client = DirectoryClient(CONNECTION_STRING, CONTAINER_NAME)

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
import glob
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

import shutil
shutil.rmtree('downloads')
shutil.rmtree('cats')
os.remove('readme.txt')
