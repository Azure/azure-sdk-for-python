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
from ctypes import c_void_p, c_long, c_ulong, c_longlong, c_ulonglong, c_short, c_ushort, c_wchar_p, c_byte
from ctypes import byref, Structure, Union, POINTER, WINFUNCTYPE, HRESULT, oledll, WinDLL, cast, create_string_buffer
import ctypes
import urllib2  

VT_EMPTY = 0
VT_NULL	= 1
VT_I2 = 2
VT_I4 = 3
VT_BSTR	= 8
VT_BOOL	= 11
VT_I1 = 16
VT_UI1 = 17
VT_UI2 = 18
VT_UI4 = 19
VT_I8 = 20
VT_UI8 = 21
VT_ARRAY = 8192

HTTPREQUEST_PROXY_SETTING = c_long
HTTPREQUEST_SETCREDENTIALS_FLAGS = c_long

_ole32 = oledll.ole32
_oleaut32 = WinDLL('oleaut32')
_CLSIDFromString = _ole32.CLSIDFromString
_CoInitialize = _ole32.CoInitialize
_CoCreateInstance = _ole32.CoCreateInstance
_SysAllocString = _oleaut32.SysAllocString
_SysFreeString = _oleaut32.SysFreeString
_SafeArrayDestroy = _oleaut32.SafeArrayDestroy
_CoTaskMemAlloc = _ole32.CoTaskMemAlloc

class BSTR(c_wchar_p):
    def __init__(self, value):
        super(BSTR, self).__init__(_SysAllocString(value))

    def __del__(self):
        _SysFreeString(self)

class _tagSAFEARRAY(Structure):
    class _tagSAFEARRAYBOUND(Structure):
        _fields_ = [('c_elements', c_ulong), ('l_lbound', c_long)]

    _fields_ = [('c_dims', c_ushort), 
                ('f_features', c_ushort),
                ('cb_elements', c_ulong),
                ('c_locks', c_ulong),
                ('pvdata', c_void_p),
                ('rgsabound', _tagSAFEARRAYBOUND*1)]

    def __del__(self):
        _SafeArrayDestroy(self.pvdata)
        pass

class VARIANT(Structure):
    class _tagData(Union):
        class _tagRecord(Structure):
            _fields_= [('pvoid', c_void_p), ('precord', c_void_p)]

        _fields_ = [('llval', c_longlong),                    
                    ('ullval', c_ulonglong),
                    ('lval', c_long),
                    ('ulval', c_ulong),
                    ('ival', c_short),
                    ('boolval', c_ushort),
                    ('bstrval', BSTR),
                    ('parray', POINTER(_tagSAFEARRAY)),
                    ('record', _tagRecord)]

    _fields_ = [('vt', c_ushort), 
                ('wReserved1', c_ushort),
                ('wReserved2', c_ushort),
                ('wReserved3', c_ushort),
                ('vdata', _tagData)]

class GUID(Structure):
    """Represents vector data."""
    _fields_ = [("data1", c_ulong),
                ("data2", c_ushort),
                ("data3", c_ushort),
                ("data4", c_byte*8)]

    def __init__(self, name=None):
        if name is not None:
            _CLSIDFromString(unicode(name), byref(self))


class _WinHttpRequest(c_void_p):
    _SetProxy = WINFUNCTYPE(HRESULT, HTTPREQUEST_PROXY_SETTING, VARIANT, VARIANT)(7, 'SetProxy')
    _SetCredentials = WINFUNCTYPE(HRESULT, BSTR, BSTR, HTTPREQUEST_SETCREDENTIALS_FLAGS)(8, 'SetCredentials')
    _Open = WINFUNCTYPE(HRESULT, BSTR, BSTR, VARIANT)(9, 'Open')
    _SetRequestHeader = WINFUNCTYPE(HRESULT, BSTR, BSTR)(10, 'SetRequestHeader')
    _GetResponseHeader = WINFUNCTYPE(HRESULT, BSTR, POINTER(c_void_p))(11, 'GetResponseHeader')
    _GetAllResponseHeaders = WINFUNCTYPE(HRESULT, POINTER(c_void_p))(12, 'GetAllResponseHeaders')
    _Send = WINFUNCTYPE(HRESULT, VARIANT)(13, 'Send')
    _Status = WINFUNCTYPE(HRESULT, POINTER(c_long))(14, 'Status')
    _StatusText = WINFUNCTYPE(HRESULT, POINTER(c_void_p))(15, 'StatusText')
    _ResponseText = WINFUNCTYPE(HRESULT, POINTER(c_void_p))(16, 'ResponseText')
    _ResponseBody = WINFUNCTYPE(HRESULT, POINTER(VARIANT))(17, 'ResponseBody')
    _ResponseStream = WINFUNCTYPE(HRESULT, POINTER(VARIANT))(18, 'ResponseStream')
    _WaitForResponse = WINFUNCTYPE(HRESULT, VARIANT, POINTER(c_ushort))(21, 'WaitForResponse')
    _Abort = WINFUNCTYPE(HRESULT)(22, 'Abort')
    _SetTimeouts = WINFUNCTYPE(HRESULT, c_long, c_long, c_long, c_long)(23, 'SetTimeouts')
    _SetClientCertificate = WINFUNCTYPE(HRESULT, BSTR)(24, 'SetClientCertificate')

    def open(self, method, url):
        flag = VARIANT()
        flag.vt = VT_BOOL
        flag.vdata.boolval = 0

        _method = BSTR(method)
        _url = BSTR(url)
        _WinHttpRequest._Open(self, _method, _url, flag)

    def set_request_header(self, name, value):
        _name = BSTR(name)
        _value = BSTR(value)
        _WinHttpRequest._SetRequestHeader(self, _name, _value)

    def get_all_response_headers(self):
        bstr_headers = c_void_p()
        _WinHttpRequest._GetAllResponseHeaders(self, byref(bstr_headers))
        bstr_headers = ctypes.cast(bstr_headers, c_wchar_p)
        headers = bstr_headers.value
        _SysFreeString(bstr_headers)
        return headers

    def send(self, request = None):
        if request is None:
            var_empty = VARIANT()
            var_empty.vt = VT_EMPTY
            var_empty.vdata.llval = 0
            _WinHttpRequest._Send(self, var_empty)
        else:
            _request = VARIANT()
            _request.vt = VT_ARRAY | VT_UI1
            safearray = _tagSAFEARRAY()
            safearray.c_dims = 1
            safearray.cb_elements = 1
            safearray.c_locks = 0
            safearray.f_features = 128
            safearray.rgsabound[0].c_elements = len(request)
            safearray.rgsabound[0].l_lbound = 0
            safearray.pvdata = cast(_CoTaskMemAlloc(len(request)), c_void_p)
            ctypes.memmove(safearray.pvdata, request, len(request))
            _request.vdata.parray = cast(byref(safearray), POINTER(_tagSAFEARRAY))
            _WinHttpRequest._Send(self, _request)            

    def status(self):
        status = c_long()
        _WinHttpRequest._Status(self, byref(status))
        return int(status.value)

    def status_text(self):
        bstr_status_text = c_void_p()
        _WinHttpRequest._StatusText(self, byref(bstr_status_text))
        bstr_status_text = ctypes.cast(bstr_status_text, c_wchar_p)
        status_text = bstr_status_text.value
        _SysFreeString(bstr_status_text)
        return status_text

    def response_text(self):
        bstr_resptext = c_void_p()
        _WinHttpRequest._ResponseText(self, byref(bstr_resptext))
        bstr_resptext = ctypes.cast(bstr_resptext, c_wchar_p)
        resptext = bstr_resptext.value
        _SysFreeString(bstr_resptext)
        return resptext
    
    def response_body(self):
        var_respbody = VARIANT()
        _WinHttpRequest._ResponseBody(self, byref(var_respbody))
        if var_respbody.vt == VT_ARRAY | VT_UI1:
            safearray = var_respbody.vdata.parray.contents
            respbody = ctypes.string_at(safearray.pvdata, safearray.rgsabound[0].c_elements)

            if respbody[3:].startswith('<?xml'):
                respbody = respbody[3:]
            return respbody
        else:
            return ''

    def set_client_certificate(self, certificate):
        _certificate = BSTR(certificate)
        _WinHttpRequest._SetClientCertificate(self, _certificate)


class _Response:
    def __init__(self, _status, _status_text, _length, _headers, _respbody):
        self.status = _status
        self.reason = _status_text
        self.length = _length
        self.headers = _headers
        self.respbody = _respbody
        
    def getheaders(self):
        return self.headers

    def read(self, _length):
        return self.respbody[:_length]


class _HTTPConnection:

    def __init__(self, host, cert_file=None, key_file=None, protocol='http'):
        self.host = unicode(host)
        self.cert_file = cert_file
        self._httprequest = _WinHttpRequest()
        self.protocol = protocol
        clsid = GUID('{2087C2F4-2CEF-4953-A8AB-66779B670495}')
        iid = GUID('{016FE2EC-B2C8-45F8-B23B-39E53A75396B}')
        _CoInitialize(0)
        _CoCreateInstance(byref(clsid), 0, 1, byref(iid), byref(self._httprequest))
        
    def putrequest(self, method, uri):
        protocol = unicode(self.protocol + '://')
        url = protocol + self.host + unicode(uri)
        self._httprequest.open(unicode(method), url)
        if self.cert_file is not None:
            self._httprequest.set_client_certificate(BSTR(unicode(self.cert_file)))

    def putheader(self, name, value):
        self._httprequest.set_request_header(unicode(name), unicode(value))

    def endheaders(self):
        pass

    def send(self, request_body):
        if not request_body:
            self._httprequest.send()
        else:
            self._httprequest.send(request_body)

    def getresponse(self):
        status = self._httprequest.status()
        status_text = self._httprequest.status_text()

        resp_headers = self._httprequest.get_all_response_headers()
        headers = []
        for resp_header in resp_headers.split('\n'):
            if ':' in resp_header:
                pos = resp_header.find(':')
                headers.append((resp_header[:pos], resp_header[pos+1:].strip()))

        body = self._httprequest.response_body()
        length = len(body)
                
        return _Response(status, status_text, length, headers, body)




