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
try:
    from unittest import mock
except ImportError:  # python < 3.3
    import mock
import pytest
from azure.core.pipeline import Pipeline
from azure.core.pipeline.transport import HttpRequest

def test_valid_kwargs():
    transport = mock.MagicMock()
    pipeline = Pipeline(transport=transport)
    pipeline.run(HttpRequest('GET', url='https://foo.bar'),
                 connection_timeout=1,
                 read_timeout=1,
                 connection_verify=True,
                 connection_cert='cert',
                 proxies='proxy',
                 cookies='cookie',
                 stream=False,
                 request_id='request_id',
                 connection_data_block_size=1024,
                 auth='auth')

def test_invalid_kwargs():
    transport = mock.MagicMock()
    pipeline = Pipeline(transport=transport)
    with pytest.raises(ValueError):
        pipeline.run(HttpRequest('GET', url='https://foo.bar'), other='other')
