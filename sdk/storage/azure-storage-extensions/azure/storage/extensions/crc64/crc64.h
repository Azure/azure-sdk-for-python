// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#pragma once

#define PY_SSIZE_T_CLEAN

#include <Python.h>

PyObject* compute_crc64(PyObject* self, PyObject* args);