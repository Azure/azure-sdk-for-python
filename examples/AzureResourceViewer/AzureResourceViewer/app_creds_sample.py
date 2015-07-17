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
'''
Application configuration
=========================

The following assumes that you will be naming your application 'MyApp' and
publish it to azure at 'http://myapp.azurewebsites.net'.
Replace these values where applicable.

In the Azure portal, under active directory, create a new application and
configure it with the following values.

- properties
    - NAME
        - set to MyApp
    - SIGN-ON URL
        - set to http://myapp.azurewebsites.net/login
    - APPLICATION IS MULTI TENANT
        - set to YES
- single sign-on
    - APP ID URI
        - set this to http://<TENANT>/MyApp
          example: http://myname.onmicrosoft.com/MyApp
    - REPLY URL
        - add http://myapp.azurewebsites.net/authorized
        - add http://localhost:3939/authorized (check the port you use for local testing)
- permissions to other applications
    - add delegated permissions for
        - Windows Azure Active Directory
        - Windows Azure Service Management
'''
TENANT = 'myname.onmicrosoft.com'
AUTHORITY_HOST_URL = 'https://login.windows.net'

# From your application CONFIGURE page
CLIENT_ID = '01234567-0123-0123-0123-01234567890a'

# From your application CONFIGURE page
# The key value will appear after you've created a new key and save changes
CLIENT_SECRET = 'zSMzz5JcBLdSmsUtzt8LchGYaSB1l6Il8QloEcn+wpk='

# Any random value, used by Flask for session management
SESSION_SECRET = 'EEMPmtzqvE2ujf+WKgkr8H9IpvBjvQDDUUnNsMnDHA4IbGXyXugJIUMxiEmtpR27'
