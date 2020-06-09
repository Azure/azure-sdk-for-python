# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
import os
import json
import ctypes as ct


def _c_str(string):
    return ct.c_char_p(string.encode("utf-8"))


class _SecretSchemaAttribute(ct.Structure):
    _fields_ = [
        ("name", ct.c_char_p),
        ("type", ct.c_uint),
    ]

class _SecretSchema(ct.Structure):
    _fields_ = [
        ("name", ct.c_char_p),
        ("flags", ct.c_uint),
        ("attributes", _SecretSchemaAttribute * 2),
    ]
_PSecretSchema = ct.POINTER(_SecretSchema)

try:
    _libsecret = ct.cdll.LoadLibrary("libsecret-1.so.0")
    _libsecret.secret_schema_new.argtypes = [
        ct.c_char_p,
        ct.c_int,
        ct.c_char_p,
        ct.c_int,
        ct.c_char_p,
        ct.c_int,
        ct.c_void_p,
    ]
    _libsecret.secret_password_lookup_sync.argtypes = [
        ct.c_void_p,
        ct.c_void_p,
        ct.c_void_p,
        ct.c_char_p,
        ct.c_char_p,
        ct.c_char_p,
        ct.c_char_p,
        ct.c_void_p,
    ]
    _libsecret.secret_password_lookup_sync.restype = ct.c_char_p
    _libsecret.secret_schema_unref.argtypes = [ct.c_void_p]
except OSError:
    _libsecret = None


def _get_user_settings_path():
    app_data_folder = os.environ["HOME"]
    return os.path.join(app_data_folder, ".config", "Code", "User", "settings.json")


def _get_user_settings():
    path = _get_user_settings_path()
    try:
        with open(path) as file:
            data = json.load(file)
            environment_name = data.get("azure.cloud", "Azure")
            return environment_name
    except IOError:
        return "Azure"


def _get_refresh_token(service_name, account_name):
    if not _libsecret:
        return None

    err = ct.c_int()
    #schema = _libsecret.secret_schema_new(
    #    _c_str("org.freedesktop.Secret.Generic"), 2, _c_str("service"), 0, _c_str("account"), 0, None
    #)
    attribute1 = _SecretSchemaAttribute()
    setattr(attribute1, "name", _c_str("service"))
    setattr(attribute1, "type", 0)
    attribute2 = _SecretSchemaAttribute()
    setattr(attribute2, "name", _c_str("account"))
    setattr(attribute2, "type", 0)
    attributes = [attribute1, attribute2]
    pattributes = (_SecretSchemaAttribute * 2)(*attributes)
    schema = _SecretSchema()
    pschema = _PSecretSchema(schema)
    ct.memset(pschema, 0, ct.sizeof(schema))
    setattr(schema, "name", _c_str("org.freedesktop.Secret.Generic"))
    setattr(schema, "flags", 2)
    setattr(schema, "attributes", pattributes)
    p_str = _libsecret.secret_password_lookup_sync(
        pschema,
        None,
        ct.byref(err),
        _c_str("service"),
        _c_str(service_name),
        _c_str("account"),
        _c_str(account_name),
        None,
    )
    #_libsecret.secret_schema_unref(schema)
    if err.value == 0:
        return p_str.decode("utf-8")

    return None


def get_credentials():
    # Disable linux support for further investigation
    raise NotImplementedError("Not supported")
