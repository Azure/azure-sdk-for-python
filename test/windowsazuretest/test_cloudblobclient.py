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

from windowsazure.storage.cloudblobclient import *
from windowsazure.storage import Metrics, BlockList
from windowsazure import WindowsAzureError

from windowsazuretest.util import (credentials, 
                                   getUniqueTestRunID,
                                   STATUS_OK,
                                   STATUS_CREATED,
                                   STATUS_ACCEPTED,
                                   DEFAULT_SLEEP_TIME,
                                   DEFAULT_LEASE_TIME)

import unittest
import time

#------------------------------------------------------------------------------
__uid = getUniqueTestRunID()

CONTAINER_TO_DELETE = 'containertodelete%s' % (__uid)
CONTAINER_NO_DELETE = 'containernodelete%s' % (__uid)
BLOB_TO_DELETE = 'blobtodelete%s' % (__uid)
BLOB_NO_DELETE = 'blobnodelete%s' % (__uid)
BLOCK_BLOB = 'blockblob%s' % (__uid)
PAGE_BLOB = 'mytestpageblob%s' % (__uid)
COPY_BLOB = 'mytestblobcopy%s' % (__uid)

#------------------------------------------------------------------------------
class CloudBlobClientTest(unittest.TestCase):

    def setUp(self):
        self.bc = CloudBlobClient(account_name=credentials.getStorageServicesName(), 
                                  account_key=credentials.getStorageServicesKey())
        self.cleanup()
        time.sleep(DEFAULT_SLEEP_TIME)
    
    def tearDown(self):
        self.cleanup()
        return super(CloudBlobClientTest, self).tearDown()

    def cleanup(self):
        for cont in [CONTAINER_NO_DELETE, CONTAINER_TO_DELETE]:
            for blob in [BLOB_NO_DELETE, BLOB_TO_DELETE]:
                try:
                    self.bc.delete_blob(cont, blob)
                except: pass

                try:
                    self.bc.delete_container(cont)
                except: pass
        
    def test_sanity(self):
        self.sanity_create_container()
        self.sanity_list_containers()
        self.sanity_get_container_properties()
        self.sanity_get_container_acl()
        self.sanity_set_container_acl()
        self.sanity_get_container_metadata()
        self.sanity_set_container_metadata()
        self.sanity_delete_container()

        self.sanity_put_blob()
        self.sanity_get_blob()
        self.sanity_get_blob_properties()
        self.sanity_set_blob_properties()
        self.sanity_get_blob_metadata()
        self.sanity_set_blob_metadata()
        self.sanity_lease_blob()
        self.sanity_snapshot_blob()
        self.sanity_copy_blob()
        self.sanity_list_blobs()
        self.sanity_delete_blob()
        self.sanity_put_block()
        self.sanity_put_block_list()
        self.sanity_get_block_list()
        self.sanity_put_page()
        self.sanity_get_page_ranges()

    #--Helpers-----------------------------------------------------------------
    # container tests
    def sanity_create_container(self):
        resp = self.bc.create_container(CONTAINER_NO_DELETE)
        self.assertTrue(resp)
        resp = self.bc.create_container(CONTAINER_TO_DELETE)
        self.assertTrue(resp)

    def list_containers_helper(self):
        containers = self.bc.list_containers()
        containers2 = [x for x in containers] #check __iter__
        containers = [x for x in containers.containers]
        self.assertItemsEqual(containers, containers2)
        
        tmpDict = {}
        for x in containers:
            if not tmpDict.has_key(x.name):
                tmpDict[x.name] = 0
            tmpDict[x.name] = tmpDict[x.name] + 1
        return tmpDict

    def sanity_list_containers(self):
        tmpDict = self.list_containers_helper()
        
        for x in [CONTAINER_NO_DELETE, CONTAINER_TO_DELETE]:
            self.assertIn(x, tmpDict.keys())
            self.assertEqual(tmpDict[x], 1)
    
    def list_blobs_helper(self, contName):
        blobs = self.bc.list_blobs(contName)
        blobs2 = [x for x in blobs] #check __iter__
        blobs = [x for x in blobs.blobs]
        self.assertItemsEqual(blobs, blobs2)
        
        tmpDict = {}
        for x in blobs:
            if not tmpDict.has_key(x.name):
                tmpDict[x.name] = 0
            tmpDict[x.name] = tmpDict[x.name] + 1
        return tmpDict

    def sanity_list_blobs(self):
        tmpDict = self.list_blobs_helper(CONTAINER_NO_DELETE)
        for x in [PAGE_BLOB, BLOCK_BLOB, 
                  BLOB_NO_DELETE, BLOB_TO_DELETE,
                  COPY_BLOB]:
            self.assertIn(x, tmpDict.keys())
            self.assertEqual(tmpDict[x], 1)

    def sanity_get_container_properties(self):
        container_properties = self.bc.get_container_properties(CONTAINER_NO_DELETE)

    def sanity_get_container_acl(self):
        container_acl = self.bc.get_container_acl(CONTAINER_NO_DELETE)
        self.assertEqual(len(container_acl.signed_identifiers),
                         0)

    def sanity_set_container_acl(self):
        container_acl = self.bc.get_container_acl(CONTAINER_NO_DELETE)
        resp = self.bc.set_container_acl(CONTAINER_NO_DELETE, container_acl)
        self.assertEqual(resp,
                         None)
        
        #What we get back here should be equivalent to the original
        container_acl2 = self.bc.get_container_acl(CONTAINER_NO_DELETE)
        self.assertEquals(container_acl.signed_identifiers,
                          container_acl2.signed_identifiers)

    def sanity_get_container_metadata(self):
        resp = self.bc.get_container_metadata(CONTAINER_NO_DELETE)
        # TODO: verify result

    def sanity_set_container_metadata(self):
        pass
        # TODO: verify this, behavior related to trimming of names appears to have changed
        #md = self.bc.get_container_metadata(CONTAINER_NO_DELETE)
        #self.assertFalse(hasattr(md, "x_ms_meta_a"))
        #resp = self.bc.set_container_metadata(CONTAINER_NO_DELETE, {'a' : 'bcbbd'})
        #self.assertEqual(resp,
        #                 None)
        #md = self.bc.get_container_metadata(CONTAINER_NO_DELETE)
        #self.assertEqual(md.x_ms_meta_a,
        #                 u'bcbbd')

    def sanity_delete_container(self):
        resp = self.bc.delete_container(CONTAINER_TO_DELETE)
        self.assertTrue(resp)
        
        #Verify it was actually removed
        tmpDict = self.list_containers_helper()

        self.assertNotIn(CONTAINER_TO_DELETE, tmpDict.keys())
        self.assertEqual(tmpDict[CONTAINER_NO_DELETE], 1)

    #blob tests
    def sanity_put_blob(self):
        resp = self.bc.put_blob(CONTAINER_NO_DELETE, 
                                BLOB_TO_DELETE, 
                                'This blob gets deleted', 
                                x_ms_blob_type='BlockBlob')
        self.assertEqual(resp, None)
        #self.assertEqual(resp.content_m_d5, u'tdVPvWDrISWkirBY9i0FSQ==')

        resp = self.bc.put_blob(CONTAINER_NO_DELETE, 
                                BLOB_NO_DELETE, 
                                'This is blob not deleted', 
                                x_ms_blob_type='BlockBlob')
        self.assertEqual(resp, None)
        #self.assertEqual(resp.content_m_d5, u'HZfRAUjvPvOegAWlLDwLTQ==')

        resp = self.bc.put_blob(CONTAINER_NO_DELETE, 
                                BLOCK_BLOB, 
                                'This is block blob', 
                                x_ms_blob_type='BlockBlob')
        self.assertEqual(resp, None)
        #self.assertEqual(resp.content_m_d5, u'6Eqt0OcuyhknAwC87yMtNA==')

        resp = self.bc.put_blob(CONTAINER_NO_DELETE, 
                                PAGE_BLOB, 
                                '', 
                                x_ms_blob_type='PageBlob', 
                                x_ms_blob_content_length='1024')
        self.assertEqual(resp, None)
        #self.assertFalse(hasattr(resp, "content_m_d5"))

    def sanity_get_blob(self):
        resp = self.bc.get_blob(CONTAINER_NO_DELETE, BLOB_NO_DELETE)
        self.assertEqual(resp, 'This is blob not deleted')
        self.assertEqual(type(resp), str)

    def sanity_get_blob_properties(self):
        resp = self.bc.get_blob_properties()
        self.assertIsInstance(resp.logging, Logging)
        self.assertIsInstance(resp.metrics, Metrics)

    def sanity_set_blob_properties(self):
        blob_properties = self.bc.get_blob_properties()
        
        self.assertEquals(blob_properties.logging.retention_policy.enabled,
                          False)
        blob_properties.logging.retention_policy.enabled=False
        
        self.assertEquals(blob_properties.metrics.enabled,
                          True)
        blob_properties.metrics.enabled=True
        
        self.assertEquals(blob_properties.metrics.retention_policy.enabled,
                          False)
        blob_properties.metrics.retention_policy.enabled=False
                
        resp = self.bc.set_blob_properties(blob_properties)
        self.assertEquals(resp, None)

        blob_properties2 = self.bc.get_blob_properties()
        self.assertEquals(blob_properties2.logging.retention_policy.enabled,
                          False)
        self.assertEquals(blob_properties2.metrics.enabled,
                          True)
        self.assertEquals(blob_properties2.metrics.retention_policy.enabled,
                          False)

    def sanity_get_blob_metadata(self):
        resp = self.bc.get_blob_metadata(CONTAINER_NO_DELETE, BLOB_NO_DELETE)
        # TODO: verify result

    def sanity_set_blob_metadata(self):
        pass
        # TODO: verify this, behavior related to trimming of names appears to have changed
        #resp = self.bc.set_blob_metadata(CONTAINER_NO_DELETE, 
        #                                 BLOB_NO_DELETE, 
        #                                 {'set_blob_metadata':'test1'})
        #self.assertEquals(resp, None)

        #resp = self.bc.get_blob_metadata(CONTAINER_NO_DELETE, BLOB_NO_DELETE)
        #self.assertEquals(resp['x_ms_meta_set_blob_metadata'], u'test1')

    def sanity_lease_blob(self):
        resp = self.bc.lease_blob(CONTAINER_NO_DELETE, 
                                  BLOB_NO_DELETE, 
                                  x_ms_lease_action='acquire')
        # TODO: verify result
        
        #The lease has a lifespan of a minute
        self.assertRaises(WindowsAzureError,
                         #TODO - WindowsAzureError doesn't override __str__ ?
                         #"There is already a lease present",
                         lambda: self.bc.lease_blob(CONTAINER_NO_DELETE, BLOB_NO_DELETE, x_ms_lease_action='acquire'))
        time.sleep(DEFAULT_LEASE_TIME)
        
        resp = self.bc.lease_blob(CONTAINER_NO_DELETE, 
                                  BLOB_NO_DELETE, 
                                  x_ms_lease_action='acquire')
        # TODO: verify result

        #TODO - file a bug
        if True:
            time.sleep(DEFAULT_LEASE_TIME)
        else:
            resp = self.bc.lease_blob(CONTAINER_NO_DELETE, 
                                      BLOB_NO_DELETE, 
                                      x_ms_lease_action='release')
            # TODO: verify result

    def sanity_snapshot_blob(self):
        resp = self.bc.snapshot_blob(CONTAINER_NO_DELETE, 
                                     BLOB_NO_DELETE)
        self.assertEquals(resp,
                          None)
        #self.assertTrue(hasattr(resp, "x_ms_snapshot"))

    def sanity_copy_blob(self):
        newBlobName = COPY_BLOB
        sourceblob = '/%s/%s/%s' % (credentials.getStorageServicesName(),
                                    CONTAINER_NO_DELETE,
                                    BLOB_NO_DELETE)
        resp = self.bc.copy_blob(CONTAINER_NO_DELETE, 
                                 newBlobName, 
                                 x_ms_copy_source=sourceblob)
        self.assertEquals(resp, None)

        resp = self.bc.get_blob(CONTAINER_NO_DELETE, newBlobName)
        self.assertEqual(resp, 'This is blob not deleted')

    def sanity_delete_blob(self):
        resp = self.bc.delete_blob(CONTAINER_NO_DELETE, BLOB_TO_DELETE)
        self.assertEquals(resp, None)

        self.assertRaises(WindowsAzureError,
                          lambda: self.bc.delete_blob(CONTAINER_NO_DELETE, BLOB_TO_DELETE))

    def sanity_put_block(self):
        md5Dict = {0: u'TjjhPkKeLS6Els52i6m9Bg==',
                   1: u'ZOnmAD+J5F2p66g8NFSefA==',
                   2: u'giBgEwOK96+T6eqweyrlNg==',
                   3: u'FDhv5/Vy34Z9KKvEnjH2lQ==',
                   4: u'jkC3Z8KTocewrRQF+tkxeA=='} 

        for i in xrange(5):
            resp = self.bc.put_block(CONTAINER_NO_DELETE, 
                                     BLOB_TO_DELETE,
                                     'block %d' % (i),
                                     str(i))
            self.assertEquals(resp, None)
            #self.assertEquals(resp.content_m_d5, md5Dict[i])

    def sanity_put_block_list(self):
        resp = self.bc.get_block_list(CONTAINER_NO_DELETE, BLOB_TO_DELETE)
        self.assertItemsEqual(resp.committed_blocks, 
                              [])
        self.assertItemsEqual(resp.uncommitted_blocks, 
                              [])

        bl = BlockList()
        bl.latest += [str(x) for x in range(4)]
        resp = self.bc.put_block_list(CONTAINER_NO_DELETE, BLOB_TO_DELETE, bl)
        self.assertEquals(resp, None)

    def sanity_get_block_list(self):
        resp = self.bc.get_block_list(CONTAINER_NO_DELETE, BLOB_TO_DELETE)
        self.assertItemsEqual([x.id for x in resp.committed_blocks], 
                              [str(x) for x in range(4)])
        #TODO - bug?
        #self.assertItemsEqual([x.id for x in resp.uncommitted_blocks], 
        #                      ["4"])
        
    def sanity_put_page(self):
        tmpBlobName = 'mytestpageblob1'
        resp = self.bc.put_blob(CONTAINER_NO_DELETE, 
                                tmpBlobName, 
                                '', 
                                x_ms_blob_type='PageBlob', 
                                x_ms_blob_content_length='1024')
        self.assertEquals(resp, None)

        resp = self.bc.put_page(CONTAINER_NO_DELETE, 
                                tmpBlobName, 
                                page='', 
                                x_ms_range='bytes=0-511', 
                                x_ms_page_write='clear')
        self.assertEquals(resp, None)
        #self.assertEquals(resp.x_ms_blob_sequence_number, u'0')

        resp = self.bc.get_page_ranges(CONTAINER_NO_DELETE, tmpBlobName)
        self.assertEquals(len(resp.page_ranges), 0)

    def sanity_get_page_ranges(self):
        self.bc.get_page_ranges(CONTAINER_NO_DELETE, PAGE_BLOB)

#------------------------------------------------------------------------------
if __name__ == '__main__':
    unittest.main()
