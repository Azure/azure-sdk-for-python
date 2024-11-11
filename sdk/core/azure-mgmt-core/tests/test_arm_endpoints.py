# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
from azure.core import AzureClouds
from azure.mgmt.core.tools import get_arm_endpoints


def test_arm_endpoints():
    cloud_setting = AzureClouds.AZURE_PUBLIC_CLOUD
    cloud_meta = get_arm_endpoints(cloud_setting)
    assert cloud_meta["resource_manager"] == "https://management.azure.com/"
    assert cloud_meta["credential_scopes"] == ["https://management.azure.com/.default"]

    cloud_setting = AzureClouds.AZURE_US_GOVERNMENT
    cloud_meta = get_arm_endpoints(cloud_setting)
    assert cloud_meta["resource_manager"] == "https://management.usgovcloudapi.net/"
    assert cloud_meta["credential_scopes"] == ["https://management.core.usgovcloudapi.net/.default"]

    cloud_setting = AzureClouds.AZURE_CHINA_CLOUD
    cloud_meta = get_arm_endpoints(cloud_setting)
    assert cloud_meta["resource_manager"] == "https://management.chinacloudapi.cn/"
    assert cloud_meta["credential_scopes"] == ["https://management.chinacloudapi.cn/.default"]
