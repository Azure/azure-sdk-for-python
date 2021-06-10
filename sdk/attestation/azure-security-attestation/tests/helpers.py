# coding: utf-8

#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

class PemUtils:
    """ PEM encoding utilities.
    """

    @staticmethod
    def pem_from_base64(base64_value, header_type):
        # type: (str, str) -> str
        pem = '-----BEGIN ' + header_type + '-----\n'
        while base64_value != '':
            pem += base64_value[:64] + '\n'
            base64_value = base64_value[64:]
        pem += '-----END ' + header_type + '-----\n'
        return pem
