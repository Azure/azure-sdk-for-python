# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------

"""
FILE: sample_simple.py

DESCRIPTION:
    This sample demonstrates how to run the template method from the template package. Here, you should
    explain what the sample does and what setup is necessary to run it.

    See https://github.com/Azure/azure-sdk-for-python/blob/main/doc/dev/sample_guide.md for more details.

USAGE:
    python sample_simple.py
"""

from azure.template import template_main


def simple_sample() -> None:
    print("Running simple sample")
    template_main()
    print("Completed running simple sample")


if __name__ == "__main__":
    simple_sample()
