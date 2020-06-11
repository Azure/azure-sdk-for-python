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

import importlib

__all__ = ['Namespace', 'load']


class Namespace(object):
    def __init__(self, name, parent=None):
        self.parent = parent
        self.name = name

    def __getattr__(self, name):
        return type(self)(name, self)

    def __str__(self):
        if self.parent is None:
            return self.name
        return '{!s}.{}'.format(self.parent, self.name)

    def __call__(self, *args, **kwargs):
        ctor = getattr(importlib.import_module(str(self.parent)), self.name)
        return ctor(*args, **kwargs)

    @classmethod
    def eval(cls, expr):
        return eval(expr, {}, {'opencensus': cls('opencensus')})


def load(expr):
    """Dynamically import OpenCensus components and evaluate the provided
    configuration expression.
    """
    return Namespace.eval(expr)
