// Copyright (c) Microsoft Corporation.
// Licensed under the MIT License.

#define PY_SSIZE_T_CLEAN
#include <Python.h>

#include "helpers.h"

PyObject* compute(PyObject* self, PyObject* args) {
    const unsigned char* src;
    Py_ssize_t length;
    uint64_t uCrc;

    // Parse the bytes input, length, and initial CRC
    if (!PyArg_ParseTuple(args, "y#K", &src, &length, &uCrc))
        return NULL;

    int pData = 0;
    uint64_t uSize = (uint64_t)length;
    uint64_t uBytes, uStop;

    uCrc ^= m_uComplement;

    uBytes = 0;
    uStop = uSize - (uSize % 32);
    if (uStop >= 2 * 32)
    {
        uint64_t uCrc0 = 0ULL;
        uint64_t uCrc1 = 0ULL;
        uint64_t uCrc2 = 0ULL;
        uint64_t uCrc3 = 0ULL;

        int pLast = pData + (int)uStop - 32;
        uSize -= uStop;
        uCrc0 = uCrc;

        for (; pData < pLast; pData += 32)
        {
            uint64_t b0, b1, b2, b3;

            // Convert 8 bytes of data to uint64_t by simply casting the pointer and accessing it.
            // This works since its little endian order.
            b0 = *((uint64_t*)(src + pData + 0)) ^ uCrc0;
            b1 = *((uint64_t*)(src + pData + 8)) ^ uCrc1;
            b2 = *((uint64_t*)(src + pData + 16)) ^ uCrc2;
            b3 = *((uint64_t*)(src + pData + 24)) ^ uCrc3;

            uCrc0 = m_u32[(7) * 256 + ((b0) & (256 - 1))];
            b0 >>= 8;
            uCrc1 = m_u32[(7) * 256 + ((b1) & (256 - 1))];
            b1 >>= 8;
            uCrc2 = m_u32[(7) * 256 + ((b2) & (256 - 1))];
            b2 >>= 8;
            uCrc3 = m_u32[(7) * 256 + ((b3) & (256 - 1))];
            b3 >>= 8;
            uCrc0 ^= m_u32[(6) * 256 + ((b0) & (256 - 1))];
            b0 >>= 8;
            uCrc1 ^= m_u32[(6) * 256 + ((b1) & (256 - 1))];
            b1 >>= 8;
            uCrc2 ^= m_u32[(6) * 256 + ((b2) & (256 - 1))];
            b2 >>= 8;
            uCrc3 ^= m_u32[(6) * 256 + ((b3) & (256 - 1))];
            b3 >>= 8;
            uCrc0 ^= m_u32[(5) * 256 + ((b0) & (256 - 1))];
            b0 >>= 8;
            uCrc1 ^= m_u32[(5) * 256 + ((b1) & (256 - 1))];
            b1 >>= 8;
            uCrc2 ^= m_u32[(5) * 256 + ((b2) & (256 - 1))];
            b2 >>= 8;
            uCrc3 ^= m_u32[(5) * 256 + ((b3) & (256 - 1))];
            b3 >>= 8;
            uCrc0 ^= m_u32[(4) * 256 + ((b0) & (256 - 1))];
            b0 >>= 8;
            uCrc1 ^= m_u32[(4) * 256 + ((b1) & (256 - 1))];
            b1 >>= 8;
            uCrc2 ^= m_u32[(4) * 256 + ((b2) & (256 - 1))];
            b2 >>= 8;
            uCrc3 ^= m_u32[(4) * 256 + ((b3) & (256 - 1))];
            b3 >>= 8;
            uCrc0 ^= m_u32[(3) * 256 + ((b0) & (256 - 1))];
            b0 >>= 8;
            uCrc1 ^= m_u32[(3) * 256 + ((b1) & (256 - 1))];
            b1 >>= 8;
            uCrc2 ^= m_u32[(3) * 256 + ((b2) & (256 - 1))];
            b2 >>= 8;
            uCrc3 ^= m_u32[(3) * 256 + ((b3) & (256 - 1))];
            b3 >>= 8;
            uCrc0 ^= m_u32[(2) * 256 + ((b0) & (256 - 1))];
            b0 >>= 8;
            uCrc1 ^= m_u32[(2) * 256 + ((b1) & (256 - 1))];
            b1 >>= 8;
            uCrc2 ^= m_u32[(2) * 256 + ((b2) & (256 - 1))];
            b2 >>= 8;
            uCrc3 ^= m_u32[(2) * 256 + ((b3) & (256 - 1))];
            b3 >>= 8;
            uCrc0 ^= m_u32[(1) * 256 + ((b0) & (256 - 1))];
            b0 >>= 8;
            uCrc1 ^= m_u32[(1) * 256 + ((b1) & (256 - 1))];
            b1 >>= 8;
            uCrc2 ^= m_u32[(1) * 256 + ((b2) & (256 - 1))];
            b2 >>= 8;
            uCrc3 ^= m_u32[(1) * 256 + ((b3) & (256 - 1))];
            b3 >>= 8;
            uCrc0 ^= m_u32[(0) * 256 + ((b0) & (256 - 1))];
            uCrc1 ^= m_u32[(0) * 256 + ((b1) & (256 - 1))];
            uCrc2 ^= m_u32[(0) * 256 + ((b2) & (256 - 1))];
            uCrc3 ^= m_u32[(0) * 256 + ((b3) & (256 - 1))];
        }

        uCrc = 0;
        uCrc ^= *((uint64_t*)(src + pData + 0)) ^ uCrc0;
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc ^= *((uint64_t*)(src + pData + 8)) ^ uCrc1;
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc ^= *((uint64_t*)(src + pData + 16)) ^ uCrc2;
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc ^= *((uint64_t*)(src + pData + 24)) ^ uCrc3;
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc) & (256 - 1))];
        pData += 32;
    }

    for (uBytes = 0; uBytes < uSize; ++uBytes, ++pData)
    {
        uCrc = (uCrc >> 8) ^ m_u1[((uCrc ^ src[pData]) & (256 - 1))];
    }

    return Py_BuildValue("K", uCrc ^ m_uComplement);
}

PyObject* concat(PyObject* self, PyObject* args) {
    uint64_t uInitialCrcAB, uInitialCrcA, uFinalCrcA, uSizeA, uInitialCrcB, uFinalCrcB, uSizeB;

    // Parse the inputs
    if (!PyArg_ParseTuple(args, "KKKKKKK", &uInitialCrcAB, &uInitialCrcA, &uFinalCrcA, &uSizeA, &uInitialCrcB, &uFinalCrcB, &uSizeB))
        return NULL;

    uint64_t uFinalCrcAB = uFinalCrcA ^ m_uComplement;

    if (uInitialCrcA != uInitialCrcAB)
    {
        uFinalCrcAB ^= MulX_N(uInitialCrcA ^ uInitialCrcAB, uSizeA);
    }

    uFinalCrcAB ^= uInitialCrcB ^ m_uComplement;
    uFinalCrcAB = MulX_N(uFinalCrcAB, uSizeB);
    uFinalCrcAB ^= uFinalCrcB;

    return Py_BuildValue("K", uFinalCrcAB);
}

static PyMethodDef crc64_methods[] = {
    { "compute", (PyCFunction)compute, METH_VARARGS, "Compute Storage CRC64 over given data with given initial CRC64 value."},
    { "concat", (PyCFunction)concat, METH_VARARGS, "Concatenate two Storage CRC64s together."},
    { NULL, NULL, 0, NULL }
};

static PyModuleDef crc64_module = {
    PyModuleDef_HEAD_INIT,
    "crc64",                                   // Module name to use with Python import statements
    "Native implementation of Storage CRC64",  // Module description
    0,
    crc64_methods
};

PyMODINIT_FUNC
PyInit_crc64() {
    return PyModule_Create(&crc64_module);
}
