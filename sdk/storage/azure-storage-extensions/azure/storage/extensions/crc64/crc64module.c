
#include <Python.h>

#include "crc64.h"

static PyMethodDef crc64_methods[] = {
    // The first property is the name exposed to Python, compute_crc64
    // The second is the C function with the implementation
    // METH_VARARGS means it takes a self argument and a list of other arguments
    { "compute_crc64", (PyCFunction)compute_crc64, METH_VARARGS, "Compute custom Storage CRC64 over given data." },

    // Terminate the array with an object containing nulls.
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
