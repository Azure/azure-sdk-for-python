#-------------------------------------------------------------------------
# Copyright 2011 Microsoft Corporation
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

"""
How to: Create a Container
--------------------------
>>> from azure.storage import *
>>> blob_service = BlobService(name, key)
>>> blob_service.create_container('mycontainer')
True

>>> blob_service.create_container('mycontainer2', x_ms_blob_public_access='container')
True

>>> blob_service.set_container_acl('mycontainer', x_ms_blob_public_access='container')

How to: Upload a Blob into a Container
--------------------------------------
>>> myblob = 'hello blob'
>>> blob_service.put_blob('mycontainer', 'myblob', myblob, x_ms_blob_type='BlockBlob')

How to: List the Blobs in a Container
-------------------------------------
>>> blobs = blob_service.list_blobs('mycontainer')
>>> for blob in blobs:
...     print(blob.name)
myblob

How to: Download Blobs
----------------------
>>> blob = blob_service.get_blob('mycontainer', 'myblob')
>>> print(blob)
hello blob

How to: Delete a Blob
---------------------
>>> blob_service.delete_blob('mycontainer', 'myblob')

>>> blob_service.delete_container('mycontainer')
True

>>> blob_service.delete_container('mycontainer2')
True

"""
from azuretest.util import *

name = credentials.getStorageServicesName()
key = credentials.getStorageServicesKey()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
