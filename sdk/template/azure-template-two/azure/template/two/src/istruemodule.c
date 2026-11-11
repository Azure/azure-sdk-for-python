// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#define PY_SSIZE_T_CLEAN
#include <Python.h>

// This package exists to give the release pipeline a package that ships both a
// platform specific binary wheel and an sdist. The implementation is therefore
// deliberately trivial: one function that takes no arguments and returns True.
static PyObject* is_true(PyObject* self, PyObject* Py_UNUSED(ignored)) {
    Py_RETURN_TRUE;
}

static PyMethodDef istrue_methods[] = {
    { "is_true", (PyCFunction)is_true, METH_NOARGS, "Return True." },
    { NULL, NULL, 0, NULL }
};

static PyModuleDef istrue_module = {
    PyModuleDef_HEAD_INIT,
    "istrue",                                             // Module name to use with Python import statements
    "Minimal native extension used to exercise binary packaging and signing.",
    0,
    istrue_methods
};

PyMODINIT_FUNC
PyInit_istrue() {
    return PyModule_Create(&istrue_module);
}
