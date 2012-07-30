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

from azure import *
from azure.storage import *
from azure.servicebus import *
from azuretest.util import *

print('WARNING!!!')
print('')
print('This program cleans the storage account and the service namespace specified')
print('by the unit test credentials file (windowsazurecredentials.json) located in')
print('your home directory.')
print('')
print('You should not run this program while tests are running as this will')
print('interfere with the tests.')
print('')
print('The following will be deleted from the storage account:')
print(' - All containers')
print(' - All tables')
print(' - All queues')
print('')
print('The following will be deleted from the service namespace:')
print(' - All queues')
print(' - All topics')
print('')
print('Enter YES to proceed, or anything else to cancel')
print('')

input = raw_input('>')
if input == 'YES':
    print('Cleaning storage account...')

    bc = BlobService(credentials.getStorageServicesName(), 
                     credentials.getStorageServicesKey())

    ts = TableService(credentials.getStorageServicesName(), 
                      credentials.getStorageServicesKey())

    qs = QueueService(credentials.getStorageServicesName(), 
                      credentials.getStorageServicesKey())

    for container in bc.list_containers():
        bc.delete_container(container.name)

    for table in ts.query_tables():
        ts.delete_table(table.name)

    for queue in qs.list_queues():
        qs.delete_queue(queue.name)

    print('Cleaning service namespace...')

    sbs = ServiceBusService(credentials.getServiceBusNamespace(), 
                            credentials.getServiceBusKey(), 
                            'owner')

    for queue in sbs.list_queues():
        sbs.delete_queue(queue.name)

    for topic in sbs.list_topics():
        sbs.delete_topic(topic.name)

    print('Done.')
else:
    print('Canceled.')
