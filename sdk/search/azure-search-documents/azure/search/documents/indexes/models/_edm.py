# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

String = "Edm.String"
Int32 = "Edm.Int32"
Int64 = "Edm.Int64"
Single = "Edm.Single"
Double = "Edm.Double"
Boolean = "Edm.Boolean"
DateTimeOffset = "Edm.DateTimeOffset"
GeographyPoint = "Edm.GeographyPoint"
ComplexType = "Edm.ComplexType"


def Collection(typ: str) -> str:
    return "Collection({})".format(typ)
