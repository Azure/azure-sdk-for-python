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
import json
import os
import time
import unittest

from exceptions import EnvironmentError

#------------------------------------------------------------------------------
class Credentials(object):
    '''
    Azure credentials needed to run Azure client tests.
    '''
    def __init__(self):
        credentialsFilename = "windowsazurecredentials.json"
        tmpName = os.path.join(os.getcwd(), credentialsFilename)
        if not os.path.exists(tmpName):
            if os.environ.has_key("USERPROFILE"):
                tmpName = os.path.join(os.environ["USERPROFILE"], 
                                       credentialsFilename)
            elif os.environ.has_key("HOME"):
                tmpName = os.path.join(os.environ["HOME"], 
                                       credentialsFilename)
        if not os.path.exists(tmpName):
            errMsg = "Cannot run Azure tests when the expected config file containing Azure credentials, '%s', does not exist!" % (tmpName)
            raise EnvironmentError(errMsg)

        with open(tmpName, "r") as f:
            self.ns = json.load(f)

    def getManagementCertFile(self):
        return self.ns[u'managementcertfile'] 

    def getSubscriptionId(self):
        return self.ns[u'subscriptionid'] 

    def getServiceBusKey(self):
        return self.ns[u'servicebuskey'] 

    def getServiceBusNamespace(self):
        return self.ns[u'servicebusns']

    def getStorageServicesKey(self):
        return self.ns[u'storageserviceskey']

    def getStorageServicesName(self):
        return self.ns[u'storageservicesname']

    def getLinuxOSVHD(self):
        return self.ns[u'linuxosvhd']

    def getProxyHost(self):
        return self.ns[u'proxyhost']

    def getProxyPort(self):
        return self.ns[u'proxyport']

    def getProxyUser(self):
        return self.ns[u'proxyuser']

    def getProxyPassword(self):
        return self.ns[u'proxypassword']

credentials = Credentials()

def getUniqueTestRunID():
    '''
    Returns a unique identifier for this particular test run so 
    parallel test runs using the same Azure keys do not interfere
    with one another.

    TODO:
    - not really unique now; just machine specific
    '''
    from os import environ
    if environ.has_key("COMPUTERNAME"):
        ret_val = environ["COMPUTERNAME"]
    else:
        import socket
        ret_val = socket.gethostname()
    for bad in ["-", "_", " ", "."]:
        ret_val = ret_val.replace(bad, "")
    ret_val = ret_val.lower().strip()
    #only return the first 20 characters so the lenghth of queue, table name will be less than 64. It may not be unique but doesn't really matter for the tests.
    return ret_val[:20]  

def getUniqueNameBasedOnCurrentTime(base_name):
    '''
    Returns a unique identifier for this particular test run so 
    parallel test runs using the same Azure keys do not interfere
    with one another.
    '''
    cur_time = str(time.time())
    for bad in ["-", "_", " ", "."]:
        cur_time = cur_time.replace(bad, "")
    cur_time = cur_time.lower().strip()
    return base_name + cur_time

class AzureTestCase(unittest.TestCase):
    def assertNamedItemInContainer(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                return

        standardMsg = '%s not found in %s' % (repr(item_name), repr(container))
        self.fail(self._formatMessage(msg, standardMsg))

    def assertNamedItemNotInContainer(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                standardMsg = '%s unexpectedly found in %s' % (repr(item_name), repr(container))
                self.fail(self._formatMessage(msg, standardMsg))
