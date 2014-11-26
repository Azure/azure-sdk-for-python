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
from contextlib import contextmanager

if sys.version_info < (3,):
    from exceptions import RuntimeError

#------------------------------------------------------------------------------


class Credentials(object):

    '''
    Azure credentials needed to run Azure client tests.
    '''

    def __init__(self):
        credentialsFilename = "azurecredentials.json"
        tmpName = os.path.join(os.getcwd(), credentialsFilename)
        if not os.path.exists(tmpName):
            if "USERPROFILE" in os.environ:
                tmpName = os.path.join(os.environ["USERPROFILE"],
                                       credentialsFilename)
            elif "HOME" in os.environ:
                tmpName = os.path.join(os.environ["HOME"],
                                       credentialsFilename)
        if not os.path.exists(tmpName):
            errMsg = "Cannot run Azure tests when the expected config file containing Azure credentials, '{0}', does not exist!".format(
                tmpName)
            raise RuntimeError(errMsg)

        with open(tmpName, "r") as f:
            self.ns = json.load(f)

    def getManagementCertFile(self):
        return self.ns[u'managementcertfile']

    def getSubscriptionId(self):
        return self.ns[u'subscriptionid']

    def getServiceBusAuthenticationType(self):
        return self.ns[u'servicebusauthenticationtype']

    def getServiceBusKey(self):
        return self.ns[u'servicebuskey']

    def getServiceBusNamespace(self):
        return self.ns[u'servicebusns']

    def getServiceBusSasKeyName(self):
        return self.ns[u'servicebussaskeyname']

    def getServiceBusSasKeyValue(self):
        return self.ns[u'servicebussaskeyvalue']

    def getEventHubNamespace(self):
        return self.ns[u'eventhubns']

    def getEventHubSasKeyName(self):
        return self.ns[u'eventhubsaskeyname']

    def getEventHubSasKeyValue(self):
        return self.ns[u'eventhubsaskeyvalue']

    def getStorageServicesKey(self):
        return self.ns[u'storageserviceskey']

    def getStorageServicesName(self):
        return self.ns[u'storageservicesname']

    def getRemoteStorageServicesKey(self):
        ''' Key for remote storage account (different location). '''
        if u'remotestorageserviceskey' in self.ns:
            return self.ns[u'remotestorageserviceskey']
        return None

    def getRemoteStorageServicesName(self):
        ''' Name for remote storage account (different location). '''
        if u'remotestorageservicesname' in self.ns:
            return self.ns[u'remotestorageservicesname']
        return None

    def getLinuxOSVHD(self):
        ''' URL to a blob of a linux .vhd in storageservicesname account'''
        return self.ns[u'linuxosvhd']

    def getProxyHost(self):
        ''' Optional. Address of the proxy server. '''
        if u'proxyhost' in self.ns:
            return self.ns[u'proxyhost']
        return None

    def getUseRequestsLibrary(self):
        if u'userequestslibrary' in self.ns:
            return self.ns[u'userequestslibrary'].lower() == 'true'
        return None

    def getLinuxVMImageName(self):
        ''' Name of a Linux VM image in the current subscription.'''
        if u'linuxvmimagename' in self.ns:
            return self.ns[u'linuxvmimagename']
        return None

    def getLinuxVMRemoteSourceImageLink(self):
        ''' Link to a .vhd in a public blob in separate storage account
        Make sure to use a storage account in West US to avoid timeout'''
        if u'linuxvmremotesourceimagelink' in self.ns:
            return self.ns[u'linuxvmremotesourceimagelink']
        return None

    def getProxyPort(self):
        ''' Optional. Port of the proxy server. '''
        if u'proxyport' in self.ns:
            return self.ns[u'proxyport']
        return None

    def getProxyUser(self):
        ''' Optional. User name for proxy server authentication. '''
        if u'proxyuser' in self.ns:
            return self.ns[u'proxyuser']
        return None

    def getProxyPassword(self):
        ''' Optional. Password for proxy server authentication. '''
        if u'proxypassword' in self.ns:
            return self.ns[u'proxypassword']
        return None

    def getUseHttplibOverride(self):
        ''' Optional. When specified, it will override the value of
        use_httplib that is set by the auto-detection in httpclient.py.
        When testing management APIs, make sure to specify a value that is
        compatible with the value of 'managementcertfile' ie. True for a .pem
        certificate file path, False for a Windows Certificate Store path.
        '''
        if u'usehttpliboverride' in self.ns:
            return self.ns[u'usehttpliboverride'].lower() != 'false'
        return None


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
    return base_name + str(random.randint(10, 99)) + cur_time[:12]


def create_service_management(service_class):
    if credentials.getUseRequestsLibrary():
        from requests import Session
        session = Session()
        session.cert = credentials.getManagementCertFile()
        service = service_class(credentials.getSubscriptionId(),
                            request_session=session)
    else:
        service = service_class(credentials.getSubscriptionId(),
                            credentials.getManagementCertFile())
    set_service_options(service)
    return service

def set_service_options(service):
    useHttplibOverride = credentials.getUseHttplibOverride()
    if useHttplibOverride is not None:
        # Override the auto-detection of what type of connection to create.
        # This allows testing of both httplib and winhttp on Windows.
        service._httpclient.use_httplib = useHttplibOverride

    service.set_proxy(credentials.getProxyHost(),
                      credentials.getProxyPort(),
                      credentials.getProxyUser(),
                      credentials.getProxyPassword())


class AzureTestCase(unittest.TestCase):

    def assertNamedItemInContainer(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                return

        standardMsg = '{0} not found in {1}'.format(
            repr(item_name), repr(container))
        self.fail(self._formatMessage(msg, standardMsg))

    def assertNamedItemNotInContainer(self, container, item_name, msg=None):
        for item in container:
            if item.name == item_name:
                standardMsg = '{0} unexpectedly found in {1}'.format(
                    repr(item_name), repr(container))
                self.fail(self._formatMessage(msg, standardMsg))

    if sys.version_info < (2,7):
        def assertIsNone(self, obj):
            self.assertEqual(obj, None)

        def assertIsNotNone(self, obj):
            self.assertNotEqual(obj, None)

        def assertIsInstance(self, obj, type):
            self.assertTrue(isinstance(obj, type))

        def assertGreater(self, a, b):
            self.assertTrue(a > b)

        def assertGreaterEqual(self, a, b):
            self.assertTrue(a >= b)

        def assertLess(self, a, b):
            self.assertTrue(a < b)

        def assertLessEqual(self, a, b):
            self.assertTrue(a <= b)

        def assertIn(self, member, container):
            if member not in container:
                self.fail('{0} not found in {1}.'.format(
                    safe_repr(member), safe_repr(container)))

        @contextmanager
        def _assertRaisesContextManager(self, excClass):
            try:
                yield
                self.fail('{0} was not raised'.format(safe_repr(excClass)))
            except excClass:
                pass

        def assertRaises(self, excClass, callableObj=None, *args, **kwargs):
            if callableObj:
                super(AzureTestCase, self).assertRaises(
                    excClass,
                    callableObj,
                    *args,
                    **kwargs
                )
            else:
                return self._assertRaisesContextManager(excClass)
