#-------------------------------------------------------------------------
# Copyright (c) Microsoft.  All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#--------------------------------------------------------------------------
from ._common_error import (
    _validate_not_none,
)
from ._common_conversion import (
    _decode_base64_to_bytes,
)


def get_certificate_from_publish_settings(publish_settings_path, path_to_write_certificate, subscription_id=None):
    '''
    Writes a certificate file to the specified location.  This can then be used 
    to instantiate ServiceManagementService.  Returns the subscription ID.

    publish_settings_path: 
        Path to subscription file downloaded from 
        http://go.microsoft.com/fwlink/?LinkID=301775
    path_to_write_certificate:
        Path to write the certificate file.
    subscription_id:
        (optional)  Provide a subscription id here if you wish to use a 
        specific subscription under the publish settings file.
    '''
    import base64

    try:
        from xml.etree import cElementTree as ET
    except ImportError:
        from xml.etree import ElementTree as ET

    try:
        import OpenSSL.crypto as crypto
    except:
        raise Exception("pyopenssl is required to use get_certificate_from_publish_settings")

    _validate_not_none('publish_settings_path', publish_settings_path)
    _validate_not_none('path_to_write_certificate', path_to_write_certificate)

    # parse the publishsettings file and find the ManagementCertificate Entry
    tree = ET.parse(publish_settings_path)
    subscriptions = tree.getroot().findall("./PublishProfile/Subscription")
    
    # Default to the first subscription in the file if they don't specify
    # or get the matching subscription or return none.
    if subscription_id:
        subscription = next((s for s in subscriptions if s.get('Id').lower() == subscription_id.lower()), None)
    else:
        subscription = subscriptions[0]

    # validate that subscription was found
    if subscription is None:
        raise ValueError("The provided subscription_id '{}' was not found in the publish settings file provided at '{}'".format(subscription_id, publish_settings_path))

    cert_string = _decode_base64_to_bytes(subscription.get('ManagementCertificate'))

    # Load the string in pkcs12 format.  Don't provide a password as it isn't encrypted.
    cert = crypto.load_pkcs12(cert_string, b'') 

    # Write the data out as a PEM format to a random location in temp for use under this run.
    with open(path_to_write_certificate, 'wb') as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert.get_certificate()))
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, cert.get_privatekey()))

    return subscription.get('Id')
