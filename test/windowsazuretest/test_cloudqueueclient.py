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


from windowsazure.storage.cloudqueueclient import *

from windowsazuretest.util import credentials, getUniqueTestRunID

import unittest
import time

#------------------------------------------------------------------------------
__uid = getUniqueTestRunID()

QUEUE_NO_DELETE = 'mytestqueuenodelete%s' % (__uid)
QUEUE_TO_DELETE = 'mytestqueuetodelete%s' % (__uid)

#------------------------------------------------------------------------------
class StorageTest(unittest.TestCase):

    def setUp(self):
        self.queue_client = CloudQueueClient(account_name=credentials.getStorageServicesName(), 
                                             account_key=credentials.getStorageServicesKey())

        self.cleanup()
        time.sleep(10)
    
    def tearDown(self):
        self.cleanup()
        return super(StorageTest, self).tearDown()

    def cleanup(self):
        try:    self.queue_client.delete_queue(QUEUE_NO_DELETE)
        except: pass
        try:    self.queue_client.delete_queue(QUEUE_TO_DELETE)
        except: pass

    def test_queue_service(self):
        self.create_queue()
        self.list_queues()
        self.get_queue_service_properties()
        self.set_queue_service_properties()
        self.get_queue_metadata()
        self.set_queue_metadata()
        self.put_message()
        self.peek_messages()
        self.get_messages()
        self.update_message()
        self.delete_message()
        self.clear_messages()

    #--Helpers-----------------------------------------------------------------
    #queue test helpers
    def create_queue(self):
        self.queue_client.create_queue(QUEUE_TO_DELETE)
        self.queue_client.create_queue(QUEUE_NO_DELETE)

    def list_queues(self):
        self.queue_client.list_queues()

    def delete_queue(self):
        '''
        TODO - this isn't called by anything
        '''
        self.queue_client.delete_queue(QUEUE_TO_DELETE)

    def get_queue_service_properties(self):
        self.queue_client.get_queue_service_properties()

    def set_queue_service_properties(self):
        queue_properties = self.queue_client.get_queue_service_properties()
        queue_properties.logging.retention_policy.enabled=False
        queue_properties.metrics.enabled=False
        queue_properties.metrics.retention_policy.enabled=False
        self.queue_client.set_queue_service_properties(queue_properties)

    def get_queue_metadata(self):
        self.queue_client.get_queue_metadata(QUEUE_NO_DELETE)

    def set_queue_metadata(self):
        self.queue_client.set_queue_metadata(QUEUE_NO_DELETE, {'category':'test'})

    def put_message(self):
        self.queue_client.put_message(QUEUE_NO_DELETE, 'This is a message')

    def peek_messages(self):
        self.queue_client.peek_messages(QUEUE_NO_DELETE)

    def get_messages(self):
        self.queue_client.get_messages(QUEUE_NO_DELETE)

    def update_message(self):
        #self.queue_client.update_message(queuenodelete, messageid, 'This is updated message', popreceipt, visibilitytimeout)
        pass

    def delete_message(self):
        #self.queue_client.put_message(queuenodelete, 'This is message to delete')
        #self.queue_client.get_messages(queuenodelete)
        #self.queue_client.delete_message(queuenodelete, messageid, popreceipt)
        pass

    def clear_messages(self):
        self.queue_client.clear_messages(QUEUE_NO_DELETE)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
