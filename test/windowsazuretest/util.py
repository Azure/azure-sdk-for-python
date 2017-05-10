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

import json
import os
import time
from exceptions import EnvironmentError

STATUS_OK         = 200
STATUS_CREATED    = 201
STATUS_ACCEPTED   = 202
STATUS_NO_CONTENT = 204
STATUS_NOT_FOUND  = 404
STATUS_CONFLICT   = 409

DEFAULT_SLEEP_TIME = 60
DEFAULT_LEASE_TIME = 65

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

    def getServiceBusKey(self):
        return self.ns[u'servicebuskey'] 

    def getServiceBusNamespace(self):
        return self.ns[u'servicebusns']

    def getStorageServicesKey(self):
        return self.ns[u'storageserviceskey']

    def getStorageServicesName(self):
        return self.ns[u'storageservicesname']

    def getHostServiceID(self):
        return self.ns[u'hostserviceid']

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
    return ret_val

def getUniqueNameBasedOnCurrentTime(base_name):
    '''
    Returns a unique identifier for this particular test run so 
    parallel test runs using the same Azure keys do not interfere
    with one another.
    '''
    cur_time = str(time.clock())
    for bad in ["-", "_", " ", "."]:
        cur_time = cur_time.replace(bad, "")
    cur_time = cur_time.lower().strip()
    return base_name + cur_time
