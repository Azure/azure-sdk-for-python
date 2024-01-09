#pragma once

#define Py_LIMITED_API 3
#define PY_SSIZE_T_CLEAN

#include <Python.h>

PyObject* compute_crc64(PyObject* self, PyObject* args);