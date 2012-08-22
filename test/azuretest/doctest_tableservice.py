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

"""
How To: Create a Table
----------------------
>>> from azure.storage import *
>>> table_service = TableService(name, key)
>>> table_service.create_table('tasktable')
True

How to Add an Entity to a Table
-------------------------------
>>> task = {'PartitionKey': 'tasksSeattle', 'RowKey': '1', 'description' : 'Take out the trash', 'priority' : 200}
>>> table_service.insert_entity('tasktable', task)

>>> task = Entity()
>>> task.PartitionKey = 'tasksSeattle'
>>> task.RowKey = '2'
>>> task.description = 'Wash the car'
>>> task.priority = 100
>>> table_service.insert_entity('tasktable', task)

How to Update an Entity
-----------------------
>>> task = {'description' : 'Take out the garbage', 'priority' : 250}
>>> table_service.update_entity('tasktable', 'tasksSeattle', '1', task)

>>> task = {'description' : 'Take out the garbage again', 'priority' : 250}
>>> table_service.insert_or_replace_entity('tasktable', 'tasksSeattle', '1', task)

>>> task = {'description' : 'Buy detergent', 'priority' : 300}
>>> table_service.insert_or_replace_entity('tasktable', 'tasksSeattle', '3', task)


How to Change a Group of Entities
---------------------------------
>>> task10 = {'PartitionKey': 'tasksSeattle', 'RowKey': '10', 'description' : 'Go grocery shopping', 'priority' : 400}
>>> task11 = {'PartitionKey': 'tasksSeattle', 'RowKey': '11', 'description' : 'Clean the bathroom', 'priority' : 100}
>>> table_service.begin_batch()
>>> table_service.insert_entity('tasktable', task10)
>>> table_service.insert_entity('tasktable', task11)
>>> table_service.commit_batch()

How to Query for an Entity
--------------------------
>>> task = table_service.get_entity('tasktable', 'tasksSeattle', '1')
>>> print(task.description)
Take out the garbage again
>>> print(task.priority)
250

>>> task = table_service.get_entity('tasktable', 'tasksSeattle', '10')
>>> print(task.description)
Go grocery shopping
>>> print(task.priority)
400

How to Query a Set of Entities
------------------------------
>>> tasks = table_service.query_entities('tasktable', "PartitionKey eq 'tasksSeattle'")
>>> for task in tasks:
...     print(task.description)
...     print(task.priority)
Take out the garbage again
250
Go grocery shopping
400
Clean the bathroom
100
Wash the car
100
Buy detergent
300

How to Query a Subset of Entity Properties
------------------------------------------
>>> tasks = table_service.query_entities('tasktable', "PartitionKey eq 'tasksSeattle'", 'description')
>>> for task in tasks:
...     print(task.description)
Take out the garbage again
Go grocery shopping
Clean the bathroom
Wash the car
Buy detergent

How to Delete an Entity
-----------------------
>>> table_service.delete_entity('tasktable', 'tasksSeattle', '1')

How to Delete a Table
---------------------
>>> table_service.delete_table('tasktable')
True

"""
from azuretest.util import *

name = credentials.getStorageServicesName()
key = credentials.getStorageServicesKey()

if __name__ == "__main__":
    import doctest
    doctest.testmod()
