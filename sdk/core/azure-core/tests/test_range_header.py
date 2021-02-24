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

from azure.core.pipeline.transport._requests_basic import parse_range_header, make_range_header

def test_basic_range_header():
    range_header = "bytes=0-500"
    range = parse_range_header(range_header)
    assert range == (0,500)

def test_no_start_range_header():
    range_header = "bytes=-500"
    range = parse_range_header(range_header)
    assert range == (-1,500)

def test_no_end_range_header():
    range_header = "bytes=0-"
    range = parse_range_header(range_header)
    assert range == (0,-1)

def test_make_basic_range_header():
    range_header = "bytes=0-500"
    range = parse_range_header(range_header)
    header = make_range_header(range, 100)
    assert header == "bytes=100-500"

def test_make_no_start_range_header():
    range_header = "bytes=-500"
    range = parse_range_header(range_header)
    header = make_range_header(range, 100)
    assert header == "bytes=-400"

def test_make_no_end_range_header():
    range_header = "bytes=0-"
    range = parse_range_header(range_header)
    header = make_range_header(range, 100)
    assert header == "bytes=100-"
