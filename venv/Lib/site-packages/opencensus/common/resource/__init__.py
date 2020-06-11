# Copyright 2019, OpenCensus Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from copy import copy
import logging
import os
import re


logger = logging.getLogger(__name__)


OC_RESOURCE_TYPE = 'OC_RESOURCE_TYPE'
OC_RESOURCE_LABELS = 'OC_RESOURCE_LABELS'

# Matches anything outside ASCII 32-126 inclusive
_NON_PRINTABLE_ASCII = re.compile(
    r'[^ !"#$%&\'()*+,\-./:;<=>?@\[\\\]^_`{|}~0-9a-zA-Z]')

# Label key/value tokens, may be quoted
_WORD_RES = r'(\'[^\']*\'|"[^"]*"|[^\s,=]+)'

_KV_RE = re.compile(r"""
    \s*                 # ignore leading spaces
    (?P<key>{word_re})  # capture the key word
    \s*=\s*
    (?P<val>{word_re})  # capture the value word
    \s*                 # ignore trailing spaces
    """.format(word_re=_WORD_RES), re.VERBOSE)

_LABELS_RE = re.compile(r"""
    ^\s*{word_re}\s*=\s*{word_re}\s*     # _KV_RE without the named groups
    (,\s*{word_re}\s*=\s*{word_re}\s*)*  # more KV pairs, comma delimited
    $
    """.format(word_re=_WORD_RES), re.VERBOSE)

_UNQUOTE_RE = re.compile(r'^([\'"]?)([^\1]*)(\1)$')


def merge_resources(resource_list):
    """Merge multiple resources to get a new resource.

    Resources earlier in the list take precedence: if multiple resources share
    a label key, use the value from the first resource in the list with that
    key. The combined resource's type will be the first non-null type in the
    list.

    :type resource_list: list(:class:`Resource`)
    :param resource_list: The list of resources to combine.

    :rtype: :class:`Resource`
    :return: The new combined resource.
    """
    if not resource_list:
        raise ValueError
    rtype = None
    for rr in resource_list:
        if rr.type:
            rtype = rr.type
            break
    labels = {}
    for rr in reversed(resource_list):
        labels.update(rr.labels)
    return Resource(rtype, labels)


def check_ascii_256(string):
    """Check that `string` is printable ASCII and at most 256 chars.

    Raise a `ValueError` if this check fails. Note that `string` itself doesn't
    have to be ASCII-encoded.

    :type string: str
    :param string: The string to check.
    """
    if string is None:
        return
    if len(string) > 256:
        raise ValueError("Value is longer than 256 characters")
    bad_char = _NON_PRINTABLE_ASCII.search(string)
    if bad_char:
        raise ValueError(u'Character "{}" at position {} is not printable '
                         'ASCII'
                         .format(
                             string[bad_char.start():bad_char.end()],
                             bad_char.start()))


class Resource(object):
    """A description of the entity for which signals are reported.

    `type_` and `labels`' keys and values should contain only printable ASCII
    and should be at most 256 characters.

    See:
        https://github.com/census-instrumentation/opencensus-specs/blob/master/resource/Resource.md

    :type type_: str
    :param type_: The resource type identifier.

    :type labels: dict
    :param labels: Key-value pairs that describe the entity.
    """  # noqa

    def __init__(self, type_=None, labels=None):
        if type_ is not None and not type_:
            raise ValueError("Resource type must not be empty")
        check_ascii_256(type_)
        if labels is None:
            labels = {}
        for key, value in labels.items():
            if not key:
                raise ValueError("Resource key must not be null or empty")
            if value is None:
                raise ValueError("Resource value must not be null")
            check_ascii_256(key)
            check_ascii_256(value)

        self.type = type_
        self.labels = copy(labels)

    def get_type(self):
        """Get this resource's type.

        :rtype: str
        :return: The resource's type.
        """
        return self.type

    def get_labels(self):
        """Get this resource's labels.

        :rtype: dict
        :return: The resource's label dict.
        """
        return copy(self.labels)

    def merge(self, other):
        """Get a copy of this resource combined with another resource.

        The combined resource will have the union of both resources' labels,
        keeping this resource's label values if they conflict.

        :type other: :class:`Resource`
        :param other: The other resource to merge.

        :rtype: :class:`Resource`
        :return: The new combined resource.
        """
        return merge_resources([self, other])


def unquote(string):
    """Strip quotes surrounding `string` if they exist.

    >>> unquote('abc')
    'abc'
    >>> unquote('"abc"')
    'abc'
    >>> unquote("'abc'")
    'abc'
    >>> unquote('"a\\'b\\'c"')
    "a'b'c"
    """
    return _UNQUOTE_RE.sub(r'\2', string)


def parse_labels(labels_str):
    """Parse label keys and values following the Resource spec.

    >>> parse_labels("k=v")
    {'k': 'v'}
    >>> parse_labels("k1=v1, k2=v2")
    {'k1': 'v1', 'k2': 'v2'}
    >>> parse_labels("k1='v1,=z1'")
    {'k1': 'v1,=z1'}
    """
    if not _LABELS_RE.match(labels_str):
        return None
    labels = {}
    for kv in _KV_RE.finditer(labels_str):
        gd = kv.groupdict()
        key = unquote(gd['key'])
        if key in labels:
            logger.warning('Duplicate label key "%s"', key)
        labels[key] = unquote(gd['val'])
    return labels


def get_from_env():
    """Get a Resource from environment variables.

    :rtype: :class:`Resource`
    :return: A resource with type and labels from the environment.
    """
    type_env = os.getenv(OC_RESOURCE_TYPE)
    if type_env is None:
        return None
    type_env = type_env.strip()

    labels_env = os.getenv(OC_RESOURCE_LABELS)
    if labels_env is None:
        return Resource(type_env)

    labels = parse_labels(labels_env)

    return Resource(type_env, labels)
