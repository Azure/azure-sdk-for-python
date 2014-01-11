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
import random
import sys
import time
import unittest

if sys.version_info < (3,):
    from exceptions import RuntimeError

#------------------------------------------------------------------------------
class Credentials(object):
    '''
    Azure credentials needed to run Azure client tests.
    '''
    def __init__(self):
        credentialsFilename = "windowsazurecredentials.json"
        tmpName = os.path.join(os.getcwd(), credentialsFilename)
        if not os.path.exists(tmpName):
            if "USERPROFILE" in os.environ:
                tmpName = os.path.join(os.environ["USERPROFILE"], 
                                       credentialsFilename)
            elif "HOME" in os.environ:
                tmpName = os.path.join(os.environ["HOME"], 
                                       credentialsFilename)
        if not os.path.exists(tmpName):
            errMsg = "Cannot run Azure tests when the expected config file containing Azure credentials, '%s', does not exist!" % (tmpName)
            raise RuntimeError(errMsg)

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

    def getForceUseHttplib(self):
        return self.ns[u'forceusehttplib'].lower() == 'true'

credentials = Credentials()

def getUniqueName(base_name):
    '''
    Returns a unique identifier for this particular test run so 
    parallel test runs using the same Azure keys do not interfere
    with one another.
    '''
    cur_time = str(time.time())
    for bad in ["-", "_", " ", "."]:
        cur_time = cur_time.replace(bad, "")
    cur_time = cur_time.lower().strip()
    return base_name + str(random.randint(10,99)) + cur_time[:12]

class AzureTestCase(unittest.TestCase):
    def assertNamedItemInContainer(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                return

        standardMsg = '{0} not found in {1}'.format(repr(item_name), repr(container))
        self.fail(self._formatMessage(msg, standardMsg))

    def assertNamedItemNotInContainer(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                standardMsg = '{0} unexpectedly found in {1}'.format(repr(item_name), repr(container))
                self.fail(self._formatMessage(msg, standardMsg))
