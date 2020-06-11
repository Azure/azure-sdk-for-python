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


class BaseObject(dict):
    def __init__(self, *args, **kwargs):
        super(BaseObject, self).__init__(*args, **kwargs)
        for key in kwargs:
            self[key] = kwargs[key]

    def __repr__(self):
        tmp = {}
        while True:
            for item in self.items():
                if item[0] not in tmp:
                    tmp[item[0]] = item[1]
            if self._default == self:
                break
            self = self._default
        return repr(tmp)

    def __setattr__(self, name, value):
        self[name] = value

    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError("'{}' object has no attribute {}".format(
                type(self).__name__,
                name,
            ))

    def __getitem__(self, key):
        if self._default is self:
            return super(BaseObject, self).__getitem__(key)
        if key in self:
            return super(BaseObject, self).__getitem__(key)
        return self._default[key]


BaseObject._default = BaseObject()


class Data(BaseObject):
    _default = BaseObject(
        baseData=None,
        baseType=None,
    )

    def __init__(self, *args, **kwargs):
        super(Data, self).__init__(*args, **kwargs)
        self.baseData = self.baseData
        self.baseType = self.baseType


class DataPoint(BaseObject):
    _default = BaseObject(
        ns='',
        name='',
        kind=None,
        value=0.0,
        count=None,
        min=None,
        max=None,
        stdDev=None,
    )

    def __init__(self, *args, **kwargs):
        super(DataPoint, self).__init__(*args, **kwargs)
        self.name = self.name
        self.value = self.value


class Envelope(BaseObject):
    _default = BaseObject(
        ver=1,
        name='',
        time='',
        sampleRate=None,
        seq=None,
        iKey=None,
        flags=None,
        tags=None,
        data=None,
    )

    def __init__(self, *args, **kwargs):
        super(Envelope, self).__init__(*args, **kwargs)
        self.name = self.name
        self.time = self.time


class Event(BaseObject):
    _default = BaseObject(
        ver=2,
        name='',
        properties=None,
        measurements=None,
    )

    def __init__(self, *args, **kwargs):
        super(Event, self).__init__(*args, **kwargs)
        self.ver = self.ver
        self.name = self.name


class ExceptionData(BaseObject):
    _default = BaseObject(
        ver=2,
        exceptions=[],
        severityLevel=None,
        problemId=None,
        properties=None,
        measurements=None,
    )

    def __init__(self, *args, **kwargs):
        super(ExceptionData, self).__init__(*args, **kwargs)
        self.ver = self.ver
        self.exceptions = self.exceptions


class Message(BaseObject):
    _default = BaseObject(
        ver=2,
        message='',
        severityLevel=None,
        properties=None,
        measurements=None,
    )

    def __init__(self, *args, **kwargs):
        super(Message, self).__init__(*args, **kwargs)
        self.ver = self.ver
        self.message = self.message


class MetricData(BaseObject):
    _default = BaseObject(
        ver=2,
        metrics=[],
        properties=None,
    )

    def __init__(self, *args, **kwargs):
        super(MetricData, self).__init__(*args, **kwargs)
        self.ver = self.ver
        self.metrics = self.metrics


class RemoteDependency(BaseObject):
    _default = BaseObject(
        ver=2,
        name='',
        id='',
        resultCode='',
        duration='',
        success=True,
        data=None,
        type=None,
        target=None,
        properties=None,
        measurements=None,
    )

    def __init__(self, *args, **kwargs):
        super(RemoteDependency, self).__init__(*args, **kwargs)
        self.ver = self.ver
        self.name = self.name
        self.resultCode = self.resultCode
        self.duration = self.duration


class Request(BaseObject):
    _default = BaseObject(
        ver=2,
        id='',
        duration='',
        responseCode='',
        success=True,
        source=None,
        name=None,
        url=None,
        properties=None,
        measurements=None,
    )

    def __init__(self, *args, **kwargs):
        super(Request, self).__init__(*args, **kwargs)
        self.ver = self.ver
        self.id = self.id
        self.duration = self.duration
        self.responseCode = self.responseCode
        self.success = self.success
