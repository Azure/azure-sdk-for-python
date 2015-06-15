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

class ResourceBase(object):
    def __init__(self, **kwargs):
        self._location = kwargs.get('location')
        self._tags = kwargs.get('tags')

    @property
    def location(self):
        """
         Gets the location of the resource.
        """
        return self._location
    
    @location.setter 
    def location(self, value):
        self._location = value

    @property
    def tags(self):
        """
         Gets the tags attached to the resource.
        """
        return self._tags
    
    @tags.setter 
    def tags(self, value):
        self._tags = value

class ResourceBaseExtended(ResourceBase):
    def __init__(self, **kwargs):
        super(ResourceBaseExtended, self).__init__(**kwargs)
        self._id = kwargs.get('id')
        self._name = kwargs.get('name')
        self._type = kwargs.get('type')

    @property
    def id(self):
        """
         Gets the ID of the resource.
        """
        return self._id
    
    @id.setter 
    def id(self, value):
        self._id = value

    @property
    def name(self):
        """
         Gets the name of the resource.
        """
        return self._name
    
    @name.setter 
    def name(self, value):
        self._name = value

    @property
    def type(self):
        """
         Gets the type of the resource.
        """
        return self._type
    
    @type.setter 
    def type(self, value):
        self._type = value
