"""Diagnostic tools for Azure Cosmos database service operations.
"""

from requests.structures import CaseInsensitiveDict
import platform
import os
from . import exceptions


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
        self._status_code = 200
        self._status_message = "Standard response for successful HTTP requests"
        self._system_information = self.get_system_info()

    @property
    def headers(self):
        return CaseInsensitiveDict(self._headers)

    @headers.setter
    def headers(self, value: dict):
        self._headers = value
        self._request_charge += float(value.get("x-ms-request-charge", 0))

    @property
    def body(self):
        return self._body

    @body.setter
    def body(self, value: dict):
        self._body = value

    @property
    def status_code(self):
        return self._status_code

    @status_code.setter
    def status_code(self, value: int):
        self._status_code = value

    @property
    def status_message(self):
        return self._status_message

    @status_message.setter
    def status_message(self, value: str):
        self._status_message = value

    @property
    def request_charge(self):
        return self._request_charge

    def clear(self):
        self._request_charge = 0

    def update_header_and_body(self, header, body):
        self.header(header)
        self.body(body)

    def update_diagnostics(self, header: dict, body: dict, e: exceptions.CosmosHttpResponseError, **kwargs):
        self.headers = header
        self.body = body
        #Note: Plan is to use kwargs to be able to easily modify this function to update with needed information
        #notes figure out how to just get status information instead of just relying on exceptions being passed
        if e:
            self.status_code = e.status_code
            self.status_message = e.message
        else:
            #cureent hacky way to get succesful status code
            self.status_code = 200
            self.status_message = "Standard response for successful HTTP requests"

    #Note: Planning to add a flag to print it in a pretty format instead of just returning a dictionary
    def __call__(self):
        #This will format all the properties into a dictionary
        return {
            key: getattr(self, key)
            for key in vars(self)
        }
        # return {
        #     key: value
        #     for key, value in self.__dict__.items()
        #     if isinstance(value, property)
        # }

    def __getattr__(self, name):
        temp_name = name
        key = "x-ms-" + temp_name.replace("_", "-")
        if key in self._common:
            return self._headers[key]
        else:
            return getattr(self, name)
        raise AttributeError(name)

    #Current System info I was able to get
    def get_system_info(self):
        ret = {}
        ret["system"] = platform.system()
        ret["python version"] = platform.python_version()
        ret["architecture"] = platform.architecture()
        ret["cpu"] = platform.processor()
        ret["cpu count"] = os.cpu_count()
        ret["machine"] = platform.machine()

        return ret
