# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import typing
from enum import Enum


class BaseObject:
    __slots__ = ()

    def __repr__(self):
        tmp = {}

        for key in self.__slots__:
            data = getattr(self, key, None)
            if isinstance(data, BaseObject):
                tmp[key] = repr(data)
            else:
                tmp[key] = data

        return repr(tmp)


class Data(BaseObject):
    """Data

    Args:
        base_data: Container for data item (B section).
        base_type: Name of item (B section) if any. If telemetry data is
        derived straight from this, this should be None.
    """

    __slots__ = ("base_data", "base_type")

    def __init__(self, base_data: any = None, base_type: str = None) -> None:
        self.base_data = base_data
        self.base_type = base_type

    def to_dict(self):
        return {
            "baseData": self.base_data.to_dict(),
            "baseType": self.base_type,
        }


class DataPointType(Enum):
    MEASUREMENT = 0
    AGGREGATION = 1


class DataPoint(BaseObject):
    """Metric data single measurement.

    Args:
        ns: Namespace of the metric
        name: Name of the metric.
        kind: Metric type. Single measurement or the aggregated value.
        value: Single value for measurement. Sum of individual measurements for the aggregation.
        count: Metric weight of the aggregated metric. Should not be set for a measurement.
        min: Minimum value of the aggregated metric. Should not be set for a measurement.
        max: Maximum value of the aggregated metric. Should not be set for a measurement.
        std_dev: Standard deviation of the aggregated metric. Should not be set for a measurement.
    """

    __slots__ = (
        "ns",
        "name",
        "kind",
        "value",
        "count",
        "min",
        "max",
        "std_dev",
    )

    def __init__(
        self,
        ns: str = "",
        name: str = "",
        kind: DataPointType = None,
        value: float = 0.0,
        count: float = None,
        min: float = None,  # pylint: disable=redefined-builtin
        max: float = None,  # pylint: disable=redefined-builtin
        std_dev: float = None,
    ) -> None:
        self.ns = ns  # pylint: disable=invalid-name
        self.name = name
        self.kind = kind
        self.value = value
        self.count = count
        self.min = min
        self.max = max
        self.std_dev = std_dev

    def to_dict(self):
        return {
            "ns": self.ns,
            "name": self.name,
            "kind": self.kind,
            "value": self.value,
            "count": self.count,
            "min": self.min,
            "max": self.max,
            "stdDev": self.std_dev,
        }


class Envelope(BaseObject):
    """Envelope represents a telemetry item

    Args:
        ver: Envelope version. For internal use only. By assigning this the default,
        it will not be serialized within the payload unless changed to a value other
        than #1.
        name: Type name of telemetry data item.
        time: Event date time when telemetry item was created. This is the wall clock
        time on the client when the event was generated.
        There is no guarantee that the client's time is accurate. This field must be
        formatted in UTC ISO 8601 format
        sample_rate: Sampling rate used in application. This telemetry item represents
        1 / sampleRate actual telemetry items.
        seq: Sequence field used to track absolute order of uploaded events.
        ikey: The application's instrumentation key.
        flags: Key/value collection of flags.
        tags: Key/value collection of context properties.
        data: Telemetry data item.
    """

    __slots__ = (
        "ver",
        "name",
        "time",
        "sample_rate",
        "seq",
        "ikey",
        "flags",
        "tags",
        "data",
    )

    def __init__(
        self,
        ver: int = 1,
        name: str = "",
        time: str = "",
        sample_rate: int = None,
        seq: str = None,
        ikey: str = None,
        flags: typing.Dict = None,
        tags: typing.Dict = None,
        data: Data = None,
    ) -> None:
        self.ver = ver
        self.name = name
        self.time = time
        self.sample_rate = sample_rate
        self.seq = seq
        self.ikey = ikey
        self.flags = flags
        self.tags = tags
        self.data = data

    def to_dict(self):
        return {
            "ver": self.ver,
            "name": self.name,
            "time": self.time,
            "sampleRate": self.sample_rate,
            "seq": self.seq,
            "iKey": self.ikey,
            "flags": self.flags,
            "tags": self.tags,
            "data": self.data.to_dict() if self.data else None,
        }


class Event(BaseObject):
    """Instances of Event represent structured event records that can be grouped
    and searched by their properties. Event data item also creates a metric of
    event count by name.

    Args:
        ver: Schema version.
        name: Event name. Keep it low cardinality to allow proper grouping and
        useful metrics.
        properties: Collection of custom properties.
        measurements: Collection of custom measurements.
    """

    __slots__ = ("ver", "name", "properties", "measurements")

    def __init__(
        self,
        ver: int = 2,
        name: str = "",
        properties: typing.Dict[str, any] = None,
        measurements: typing.Dict[str, int] = None,
    ):
        self.ver = ver
        self.name = name
        self.properties = properties
        self.measurements = measurements

    def to_dict(self):
        return {
            "ver": self.ver,
            "name": self.name,
            "properties": self.properties,
            "measurements": self.measurements,
        }


class ExceptionDetails(BaseObject):
    """Exception details of the exception in a chain.

    Args:
        id: In case exception is nested (outer exception contains inner one),
        the id and outerId properties are used to represent the nesting.
        outer_id: The value of outerId is a reference to an element in
        ExceptionDetails that represents the outer exception.
        type_name: Exception type name.
        message: Exception message.
        has_full_stack: Indicates if full exception stack is provided in the exception.
        The stack may be trimmed, such as in the case of a StackOverflow exception.
        stack: Text describing the stack. Either stack or parsedStack should have a
        value.
        parsed_stack: List of stack frames. Either stack or parsedStack should have
        a value.
    """

    __slots__ = (
        "id",
        "outer_id",
        "type_name",
        "message",
        "has_full_stack",
        "stack",
        "parsed_stack",
    )

    def __init__(
        self,
        id: int = None,  # pylint: disable=redefined-builtin
        outer_id: int = None,
        type_name: str = None,
        message: str = None,
        has_full_stack: bool = None,
        stack: str = None,
        parsed_stack: any = None,
    ) -> None:
        self.id = id  # pylint: disable=invalid-name
        self.outer_id = outer_id
        self.type_name = type_name
        self.message = message
        self.has_full_stack = has_full_stack
        self.stack = stack
        self.parsed_stack = parsed_stack

    def to_dict(self):
        return {
            "id": self.id,
            "outerId": self.outer_id,
            "typeName": self.type_name,
            "message": self.message,
            "hasFullStack ": self.has_full_stack,
            "stack": self.stack,
            "parsedStack": self.parsed_stack,
        }


class ExceptionData(BaseObject):
    """An instance of Exception represents a handled or unhandled exception that
    occurred during execution of the monitored application.

    Args:
        ver: Schema version.
        exceptions: Exception chain - list of inner exceptions.
        severity_level: Severity level. Mostly used to indicate exception severity
        level when it is reported by logging library.
        problem_id: Identifier of where the exception was thrown in code.
        Used for exceptions grouping. Typically a combination of exception type
        and a function from the call stack.
        properties: Collection of custom properties.
        measurements: Collection of custom measurements.
    """

    __slots__ = (
        "ver",
        "exceptions",
        "severity_level",
        "problem_id",
        "properties",
        "measurements",
    )

    def __init__(
        self,
        ver: int = 2,
        exceptions: typing.List[ExceptionDetails] = None,
        severity_level: int = None,
        problem_id: str = None,
        properties: typing.Dict[str, any] = None,
        measurements: typing.Dict[str, int] = None,
    ) -> None:
        if exceptions is None:
            exceptions = []
        self.ver = ver
        self.exceptions = exceptions
        self.severity_level = severity_level
        self.problem_id = problem_id
        self.properties = properties
        self.measurements = measurements

    def to_dict(self):
        return {
            "ver": self.ver,
            "exceptions": self.exceptions,
            "severityLevel": self.severity_level,
            "problemId": self.problem_id,
            "properties": self.properties,
            "measurements": self.measurements,
        }


class SeverityLevel(Enum):
    VERBOSE = 0
    INFORMATION = 1
    WARNING = 2
    ERROR = 3
    CRITICAL = 4


class Message(BaseObject):
    """Instances of Message represent printf-like trace statements that are
    text-searched. The message does not have measurements.

    Args:
        ver: Schema version.
        message: Trace message.
        severity_level: Trace severity level.
        properties: Collection of custom properties.
    """

    __slots__ = (
        "ver",
        "message",
        "measurements",
        "severity_level",
        "properties",
    )

    def __init__(
        self,
        ver: int = 2,
        message: str = "",
        severity_level: SeverityLevel = None,
        properties: typing.Dict[str, any] = None,
        measurements: typing.Dict[str, int] = None,
    ) -> None:
        self.ver = ver
        self.message = message
        self.severity_level = severity_level
        self.properties = properties
        self.measurements = measurements

    def to_dict(self):
        return {
            "ver": self.ver,
            "message": self.message,
            "severityLevel": self.severity_level,
            "properties": self.properties,
            "measurements": self.measurements,
        }


class MetricData(BaseObject):
    """An instance of the Metric item is a list of measurements (single data points)
    and/or aggregations.

    Args:
        ver: Data base data.
        metrics: List of metrics. Only one metric in the list is currently supported
        by Application Insights storage. If multiple data points were sent only the
        first one will be used.
        properties:Collection of custom properties.
    """

    __slots__ = ("ver", "metrics", "properties")

    def __init__(
        self,
        ver: int = 2,
        metrics: typing.List[DataPoint] = None,
        properties: typing.Dict[str, any] = None,
    ) -> None:
        if metrics is None:
            metrics = []
        self.ver = ver
        self.metrics = metrics
        self.properties = properties

    def to_dict(self):
        return {
            "ver": self.ver,
            "metrics": list(map(lambda x: x.to_dict(), self.metrics)),
            "properties": self.properties,
        }


class RemoteDependency(BaseObject):
    """An instance of Remote Dependency represents an interaction of the monitored component
    with a remote component/service like SQL or an HTTP endpoint.

    Args:
        ver: Schema version.
        name: Name of the command initiated with this dependency call. Low cardinality value.
        Examples are stored procedure name and URL path template.
        id: Identifier of a dependency call instance. Used for correlation with the request
        telemetry item corresponding to this dependency call.
        result_code: Result code of a dependency call. Examples are SQL error code and HTTP
        status code.
        duration: Request duration in format: DD.HH:MM:SS.MMMMMM. Must be less than 1000 days.
        success: Indication of successfull or unsuccessfull call.
        data: Command initiated by this dependency call. Examples are SQL statement and HTTP
        URL's with all query parameters.
        type: Dependency type name. Very low cardinality value for logical grouping of
        dependencies and interpretation of other fields like commandName and resultCode.
        Examples are SQL, Azure table, and HTTP.
        target: Target site of a dependency call. Examples are server name, host address.
        properties: Collection of custom properties.
        measurements: Collection of custom measurements.
    """

    __slots__ = (
        "ver",
        "name",
        "id",
        "result_code",
        "duration",
        "success",
        "data",
        "type",
        "target",
        "properties",
        "measurements",
    )

    def __init__(
        self,
        ver: int = 2,
        name: str = "",
        id: str = "",  # pylint: disable=redefined-builtin
        result_code: str = "",
        duration: str = "",
        success: bool = True,
        data: Data = None,
        type: str = None,  # pylint: disable=redefined-builtin
        target: str = None,
        properties: typing.Dict[str, any] = None,
        measurements: typing.Dict[str, int] = None,
    ) -> None:
        self.ver = ver
        self.name = name
        self.id = id  # pylint: disable=invalid-name
        self.result_code = result_code
        self.duration = duration
        self.success = success
        self.data = data
        self.type = type
        self.target = target
        self.properties = properties
        self.measurements = measurements

    def to_dict(self):
        return {
            "ver": self.ver,
            "name": self.name,
            "id": self.id,
            "resultCode": self.result_code,
            "duration": self.duration,
            "success": self.success,
            "data": self.data,
            "type": self.type,
            "target": self.target,
            "properties": self.properties,
            "measurements": self.measurements,
        }


class Request(BaseObject):
    """An instance of Request represents completion of an external request to the
    application to do work and contains a summary of that request execution and the
    results.

    Args:
        ver: Schema version.
        id: Identifier of a request call instance. Used for correlation between request
        and other telemetry items.
        duration: Request duration in format: DD.HH:MM:SS.MMMMMM. Must be less than 1000
        days.
        response_code: Response code from Request
        success: Indication of successfull or unsuccessfull call.
        source: Source of the request. Examples are the instrumentation key of the caller
        or the ip address of the caller.
        name: Name of the request. Represents code path taken to process request. Low
        cardinality value to allow better grouping of requests. For HTTP requests it
        represents the HTTP method and URL path template like 'GET /values/{id}'.
        url: Request URL with all query string parameters.
        properties: Collection of custom properties.
        measurements: Collection of custom measurements.
    """

    __slots__ = (
        "ver",
        "id",
        "duration",
        "response_code",
        "success",
        "source",
        "name",
        "url",
        "properties",
        "measurements",
    )

    def __init__(
        self,
        ver: int = 2,
        id: str = "",  # pylint: disable=redefined-builtin
        duration: str = "",
        response_code: str = "",
        success: bool = True,
        source: str = None,
        name: str = None,
        url: str = None,
        properties: typing.Dict[str, any] = None,
        measurements: typing.Dict[str, int] = None,
    ) -> None:
        self.ver = ver
        self.id = id  # pylint: disable=invalid-name
        self.duration = duration
        self.response_code = response_code
        self.success = success
        self.source = source
        self.name = name
        self.url = url
        self.properties = properties
        self.measurements = measurements

    def to_dict(self):
        return {
            "ver": self.ver,
            "id": self.id,
            "duration": self.duration,
            "responseCode": self.response_code,
            "success": self.success,
            "source": self.source,
            "name": self.name,
            "url": self.url,
            "properties": self.properties,
            "measurements": self.measurements,
        }


class LiveMetricDocument(BaseObject):

    __slots__ = (
        "quickpulse_type",
        "document_type",
        "version",
        "operation_id",
        "properties",
    )

    def __init__(
        self,
        quickpulse_type: str = "",
        document_type: str = "",
        version: str = "",
        operation_id: str = "",
        properties: typing.Dict[str, any] = None,
    ) -> None:
        self.quickpulse_type = quickpulse_type
        self.document_type = document_type
        self.version = version
        self.operation_id = operation_id
        self.properties = properties

    def to_dict(self):
        return {
            "__type": self.quickpulse_type,
            "DocumentType": self.document_type,
            "Version": self.version,
            "OperationId": self.operation_id,
            "Properties": self.properties,
        }


class LiveMetric(BaseObject):

    __slots__ = ("name", "value", "weight")

    def __init__(self, name: str, value: str, weight: int) -> None:
        self.name = name
        self.value = value
        self.weight = weight

    def to_dict(self):
        return {"Name": self.name, "Value": self.value, "Weight": self.weight}


class LiveMetricEnvelope(BaseObject):
    """Envelope to send data to Live Metrics service.

    Args:
        documents: An array of detailed failure documents, each representing a full SDK telemetry item.
        instance: Instance name. Either a cloud RoleInstance (if running in Azure), or the machine name otherwise.
        instrumentation_key: Instrumentation key that the agent is instrumented with. While SDK can send to multiple ikeys,
        it must select a single ikey to send QuickPulse data to - and only consider telemetry items sent to that ikey while collecting.
        invariant_version: Version of QPS protocol that SDK supports. Currently, the latest is 2.
        machine_name: Machine name.
        metrics: Metrics
        stream_id: A random GUID generated at start-up. Must remain unchanged while the application is running.
        timestamp: UTC time the request was made in the Microsoft JSON format, e.g. "/Date(1478555534692)/".
        version: SDK version (not specific to QuickPulse). Please make sure that there's some sort of prefix to identify the client (.NET SDK, Java SDK, etc.).
    """

    __slots__ = (
        "documents",
        "instance",
        "instrumentation_key",
        "invariant_version",
        "machine_name",
        "metrics",
        "stream_id",
        "timestamp",
        "version",
    )

    def __init__(
        self,
        documents: typing.List[LiveMetricDocument] = None,
        instance: str = "",
        instrumentation_key: str = "",
        invariant_version: int = 1,
        machine_name: str = "",
        metrics: typing.List[LiveMetric] = None,
        stream_id: str = "",
        timestamp: str = "",
        version: str = "",
    ) -> None:
        if metrics is None:
            metrics = []
        self.documents = documents
        self.instance = instance
        self.instrumentation_key = instrumentation_key
        self.invariant_version = invariant_version
        self.machine_name = machine_name
        self.metrics = metrics
        self.stream_id = stream_id
        self.timestamp = timestamp
        self.version = version

    def to_dict(self):
        return {
            "Documents": list(map(lambda x: x.to_dict(), self.documents))
            if self.documents
            else None,
            "Instance": self.instance,
            "InstrumentationKey": self.instrumentation_key,
            "InvariantVersion": self.invariant_version,
            "MachineName": self.machine_name,
            "Metrics": list(map(lambda x: x.to_dict(), self.metrics)),
            "StreamId": self.stream_id,
            "Timestamp": self.timestamp,
            "Version": self.version,
        }
