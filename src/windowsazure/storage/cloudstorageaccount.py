#------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. 
#
# This source code is subject to terms and conditions of the Apache License, 
# Version 2.0. A copy of the license can be found in the License.html file at 
# the root of this distribution. If you cannot locate the Apache License, 
# Version 2.0, please send an email to vspython@microsoft.com. By using this 
# source code in any fashion, you are agreeing to be bound by the terms of the 
# Apache License, Version 2.0.
#
# You must not remove this notice, or any other, from this software.
#------------------------------------------------------------------------------
from windowsazure.storage.cloudblobclient import CloudBlobClient
from windowsazure.storage.cloudtableclient import CloudTableClient
from windowsazure.storage.cloudqueueclient import CloudQueueClient

class CloudStorageAccount:
    
    def __init__(self, account_name, account_key):
        self.account_name = account_name
        self.account_key = account_key

    def create_blob_client(self):
        return CloudBlobClient(self.account_name, self.account_key)

    def create_table_client(self):
        return CloudTableClient(self.account_name, self.account_key)

    def create_queue_client(self):
        return CloudQueueClient(self.account_name, self.account_key)