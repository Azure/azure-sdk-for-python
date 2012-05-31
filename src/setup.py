#!/usr/bin/env python

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

from distutils.core import setup

setup(name='windowsazure',
      version='0.2.2',
      description='Windows Azure client APIs',
      url='https://github.com/WindowsAzure/azure-sdk-for-python',
      packages=['windowsazure',
                'windowsazure.http',
                'windowsazure.servicebus',
                'windowsazure.storage']
     )
