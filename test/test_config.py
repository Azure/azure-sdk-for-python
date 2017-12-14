#The MIT License (MIT)
#Copyright (c) 2014 Microsoft Corporation

#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in all
#copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#SOFTWARE.

import os
try:
    import urllib3
    urllib3.disable_warnings()
except:
    print("no urllib3")

class _test_config(object):

    host = os.getenv('ACCOUNT_HOST', 'https://localhost:8081')
    masterKey = os.getenv('ACCOUNT_KEY', 'C2y6yDjf5/R+ob0N8A7Cgv30VRDJIWEHLM+4QDU5DE2nQ9nDuVTqobD4b8mGGyPMbIZnqyMsEcaGQy67XIw/Jw==')

    global_host = '[YOUR_GLOBAL_ENDPOINT_HERE]'
    write_location_host = '[YOUR_WRITE_ENDPOINT_HERE]'
    read_location_host = '[YOUR_READ_ENDPOINT_HERE]'
    read_location2_host = '[YOUR_READ_ENDPOINT2_HERE]'
    global_masterKey = '[YOUR_KEY_HERE]'

    write_location = '[YOUR_WRITE_LOCATION_HERE]'
    read_location = '[YOUR_READ_LOCATION_HERE]'
    read_location2 = '[YOUR_READ_LOCATION2_HERE]'


