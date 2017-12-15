# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

"""
Setup the eventhubs module.

"""

import sys
import eventhubs
from setuptools import setup

def find_packages():
    """Return packages based on sys version."""
    if sys.version_info[0] >= 3:
        return ['eventhubs', 'eventhubs.async', 'eventprocessorhost']
    return ['eventhubs']

setup(name='eventhubs',
      version=eventhubs.__version__,
      description='Python client library for Azure Event Hubs',
      url='http://github.com/azure/azure-event-hubs-python',
      author='microsoft',
      license='MIT',
      packages=find_packages(),
      zip_safe=False)
