# coding: utf-8

# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

"""
FILE: sample_helpers.py
DESCRIPTION:
    Helper functions used for the azure attestation samples.


"""

def write_banner(banner):
    #type:(str) -> None
    separator = '*'*80
    print("\n")
    print(separator)
    print("        ", banner)
    print(separator)

