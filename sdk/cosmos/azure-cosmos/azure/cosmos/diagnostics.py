#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

"""Diagnostic tools for Cosmos 
"""

class RecordHeaders(object):
    """ Record Response headers from Cosmos read operations.

    The full response headers are stored in the ``headers`` property. Common 
    Cosmos-specific headers that are prefixed with ``'x-ms-'``:

    * x-ms-activity-id
    * x-ms-request-charge
    * x-ms-session-token
    * x-ms-item-count
    * x-ms-request-quota
    * x-ms-resource-usage
    * x-ms-retry-after-ms
    
    may also be accessed by using snake cased attribute names. For instance, 
    the header ``'x-ms-request-charge'`` is accessible by a ``request_charge`` 
    attribute.

    Examples:

        >>> rh = RecordHeaders()

        >>> col = b.create_container(
        ...     id="some_comtainer",
        ...     partition_key=PartitionKey(path='/id', kind='Hash'),
        ...     response_hook=rh)

        >>> rh.activity_id
        '6243eeed-f06a-413d-b913-dcf8122d0642'



    """

    _common = {
        'x-ms-activity-id',
        'x-ms-request-charge',
        'x-ms-session-token',

        'x-ms-item-count',
        'x-ms-request-quota',
        'x-ms-resource-usage',
        'x-ms-retry-after-ms',
    }

    def __init__(self):
        self._headers = {}
        
    @property
    def headers(self):
        return dict(self._headers)
    
    def __call__(self, headers):
        self._headers = headers
        
    def __getattr__(self, name):
        key = "x-ms-" + name.replace("_", "-")
        if key in self._common:
            return self._headers[key]
        raise AttributeError(name)
