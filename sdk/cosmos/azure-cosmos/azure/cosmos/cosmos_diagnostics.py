"""Diagnostic tools for Azure Cosmos database service operations.
"""

from requests.structures import CaseInsensitiveDict
import platform
import os
from ._utils import get_user_agent
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

    def __init__(self, ua):
        self._user_agent = ua
        self._consistency_level = None
        self._operation_type = None
        self._resource_type = None
        self._request_headers = CaseInsensitiveDict()
        self._response_headers = CaseInsensitiveDict()
        self._body = None
        self._status_code = None
        self._status_reason = None
        self._substatus_code = 0
        self._status_message = None
        self._elapsed_time = None

        self._system_information = self.get_system_info()

    @property
    def response_headers(self):
        return CaseInsensitiveDict(self._response_headers)

    @response_headers.setter
    def response_headers(self, value: dict):
        self._response_headers = value

    @property
    def request_headers(self):
        return CaseInsensitiveDict(self._request_headers)

    @request_headers.setter
    def request_headers(self, value: dict):
        self._request_headers = value

    @property
    def body(self):
        return dict(self._body)

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
    def substatus_code(self):
        return self._substatus_code

    @substatus_code.setter
    def substatus_code(self, value: int):
        self._substatus_code = value

    @property
    def status_reason(self):
        return self._status_reason

    @status_reason.setter
    def status_reason(self, value: str):
        self._status_reason = value

    @property
    def elapsed_time(self):
        return self._elapsed_time

    @elapsed_time.setter
    def elapsed_time(self, value):
        self._elapsed_time = value

    @property
    def status_message(self):
        return self._status_message

    @status_message.setter
    def status_message(self, value: str):
        self._status_message = value

    @property
    def user_agent(self):
        return self._user_agent

    @user_agent.setter
    def user_agent(self, value: str):
        self._user_agent = value

    @property
    def consistency_level(self):
        return self._consistency_level

    @consistency_level.setter
    def consistency_level(self, value: str):
        self._consistency_level = value

    @property
    def operation_type(self):
        return self._operation_type

    @operation_type.setter
    def operation_type(self, value: str):
        self._operation_type = value

    @property
    def resource_type(self):
        return self._resource_type

    @resource_type.setter
    def resource_type(self, value: str):
        self._resource_type = value

    def update_diagnostics(self, header: dict, body: dict, **kwargs):
        self.clear()
        self.response_headers = header
        try:
            self.body = dict(body)
        except ValueError as ve:
            self.body = body
        eTime = kwargs.get("elapsed_time")
        if eTime:
            self.elapsed_time = eTime
        e = kwargs.get("exception")
        sc = kwargs.get("status_code")
        if sc:
            self.status_code = sc
        sr = kwargs.get("status_reason")
        if sr:
            self.status_reason = sr
        sm = kwargs.get("response_text")
        if sm:
            self.status_message = sm
        ssc = kwargs.get("substatus_code")
        if ssc:
            self.substatus_code = ssc
        else:
            self.substatus_code = 0
        ua = kwargs.get("user_agent")
        if ua:
            self.user_agent = ua
        rh = kwargs.get("request_headers")
        if rh:
            self.request_headers = dict(rh)
        ot = kwargs.get("operation_type")
        if ot:
            self.operation_type = ot
        rt = kwargs.get("resource_type")
        if rt:
            self.resource_type = rt
        if e:
            self.status_code = e.status_code
            self.status_message = e.message

    def __call__(self, p=False):
        #This will format all the properties into a dictionary
        ret = {
            key: getattr(self, key)
            for key in vars(self)
        }
        if p:
            print("DIAGNOSTICS")
            for key, value in ret.items():
                if type(value) is dict:
                    print(str(key)+":")
                    for k, v in value.items():
                        print("    " + str(k) + ": " + str(v))
                else:
                    print(str(key)+": "+str(value))
        else:
            return ret

    def __getattr__(self, name):
        temp_name = name
        key = "x-ms-" + temp_name.replace("_", "-")
        try:
            if key in self._common:
                return self._response_headers[key]
            else:
                return getattr(self, name)
        except:
            raise AttributeError(name)

    #Current System info
    def get_system_info(self):
        ret = {}
        ret["system"] = platform.system()
        ret["python version"] = platform.python_version()
        ret["architecture"] = platform.architecture()
        ret["cpu"] = platform.processor()
        ret["cpu count"] = os.cpu_count()
        ret["machine"] = platform.machine()

        return ret

    def clear(self):
        self.response_headers = CaseInsensitiveDict()
        self.request_headers = CaseInsensitiveDict()
        self.body = None
        self.status_code = None
        self.status_reason = None
        self.substatus_code = 0
        self.status_message = None
        self.elapsed_time = None
        self.operation_type = None
        self.resource_type = None
