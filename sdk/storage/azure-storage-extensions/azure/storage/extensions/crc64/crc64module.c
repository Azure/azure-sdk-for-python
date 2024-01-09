
#define Py_LIMITED_API 3

#include <Python.h>
#include "crc64.h"

static PyMethodDef crc64_methods[] = {
    { "compute_crc64", (PyCFunction)compute_crc64, METH_VARARGS, "Compute Storage CRC64 over given data." },
    { NULL, NULL, 0, NULL }
};

static PyModuleDef crc64_module = {
    PyModuleDef_HEAD_INIT,
    "crc64",                                   // Module name to use with Python import statements
    "Native implementation of Storage CRC64",  // Module description
    0,
    crc64_methods
};

PyMODINIT_FUNC PyInit_crc64() {
    return PyModule_Create(&crc64_module);
}