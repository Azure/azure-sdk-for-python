# The MIT License (MIT)
# Copyright (c) 2014 Microsoft Corporation

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Create permissions in the Azure Cosmos DB SQL API service.
"""
from typing import Dict, Any, Union

from .documents import PermissionMode


class Permission(object):
    """Represents a Permission object in the Azure Cosmos DB SQL API service.
    """
    def __init__(self, id, user_link, permission_mode, resource_link, properties):  # pylint: disable=redefined-builtin
        # type: (str, str, Union[str, PermissionMode], str, Dict[str, Any]) -> None
        self.id = id
        self.user_link = user_link
        self.permission_mode = permission_mode
        self.resource_link = resource_link
        self.properties = properties
        self.permission_link = u"{}/permissions/{}".format(self.user_link, self.id)
