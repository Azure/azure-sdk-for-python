"""Diagnostic tools for Azure Cosmos database service operations.
"""

from requests.structures import CaseInsensitiveDict


class CosmosDiagnostics(object):
    """Record Response headers and other useful information from Cosmos read operations.

    The full response headers are stored in the ``headers`` property.

    Calling the class as a function will return a dictionary of all Diagnostics properties.

    Examples:

        >>> col = b.create_container(
        ...     id="some_container",
        ...     partition_key=PartitionKey(path='/id', kind='Hash'),
        >>> cd = col.diagnostics() #col.diagnostics would return the object itself which can still be used to get the properties.
        >>> cd['headers']['x-ms-activity-id']
        '6243eeed-f06a-413d-b913-dcf8122d0642'
        >>>cd
        {headers: {x-ms-activity-id: '6243eeed-f06a-413d-b913-dcf8122d0642',
                    ...: ... ,
                    ...: ...},
        body: { ...: ...,
               ...: ...,
               ...: ...},
        request_charge: #,
        error_code: #,
        error_message: ...
        ...: ...}

     New Properties can be added by adding a getter and setter for them.

     Example:

         @property
         def new_property(self):
            return self._new_property

         @new_property.setter
         def new_property(self, value: type):
            self._new_property = value

    """

    _common = {
        "x-ms-activity-id",
        "x-ms-session-token",
        "x-ms-item-count",
        "x-ms-request-quota",
        "x-ms-resource-usage",
        "x-ms-retry-after-ms",
    }

    def __init__(self):
        self._headers = CaseInsensitiveDict()
        self._body = None
        self._request_charge = 0
        self._error_code = 0
        self._error_message = ""

    @property
    def headers(self):
        return CaseInsensitiveDict(self._headers)

    @headers.setter
    def header(self, value: dict):
        self._headers = value
        self._request_charge += float(value.get("x-ms-request-charge", 0))

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value: dict):
        self._body = value

    @property
    def error_code(self):
        return self._error_code

    @error_code.setter
    def error_code(self, value: int):
        self._error_code = value

    @property
    def error_message(self):
        return self._error_message

    @error_message.setter
    def error_message(self, value: str):
        self._error_message = value

    @property
    def request_charge(self):
        return self._request_charge

    def clear(self):
        self._request_charge = 0

    def __call__(self):
        #This will format all the properties into a dictionary
        return {
            key: value
            for key, value in self.__dict__.items()
            if isinstance(value, property)
        }

    def __getattr__(self, name):
        key = "x-ms-" + name.replace("_", "-")
        if key in self._common:
            return self._headers[key]
        raise AttributeError(name)
