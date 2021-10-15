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

def test_example_raw_response_hook():
    def callback(response):
        response.http_response.status_code = 200
        response.http_response.headers["custom_header"] = "CustomHeader"

    from azure.core.pipeline import Pipeline
    from azure.core.pipeline.policies import RedirectPolicy, UserAgentPolicy
    from azure.core.pipeline.transport import RequestsTransport, HttpRequest
    from azure.core.pipeline.policies import CustomHookPolicy

    request = HttpRequest("GET", "https://bing.com")
    policies = [
        CustomHookPolicy(raw_response_hook=callback)
    ]

    with Pipeline(transport=RequestsTransport(), policies=policies) as pipeline:
        response = pipeline.run(request)
        assert response.http_response.status_code == 200
        assert response.http_response.headers["custom_header"] == "CustomHeader"
