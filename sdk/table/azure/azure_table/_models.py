from azure.azure_table._generated.models import TableProperties
from azure.azure_table._shared.response_handlers import return_context_and_deserialized, process_storage_error
from azure.core.exceptions import HttpResponseError
from azure.core.paging import PageIterator
from ._generated.models import AccessPolicy as GenAccessPolicy
from ._generated.models import Logging as GeneratedLogging
from ._generated.models import Metrics as GeneratedMetrics
from ._generated.models import RetentionPolicy as GeneratedRetentionPolicy
from ._generated.models import CorsRule as GeneratedCorsRule


class TableAnalyticsLogging(GeneratedLogging):
    """Azure Analytics Logging settings.

    All required parameters must be populated in order to send to Azure.

    :keyword str version: Required. The version of Storage Analytics to configure.
    :keyword bool delete: Required. Indicates whether all delete requests should be logged.
    :keyword bool read: Required. Indicates whether all read requests should be logged.
    :keyword bool write: Required. Indicates whether all write requests should be logged.
    :keyword ~azure.storage.queue.RetentionPolicy retention_policy: Required.
        The retention policy for the metrics.
    """

    def __init__(self, **kwargs):
        self.version = kwargs.get('version', u'1.0')
        self.delete = kwargs.get('delete', False)
        self.read = kwargs.get('read', False)
        self.write = kwargs.get('write', False)
        self.retention_policy = kwargs.get('retention_policy') or RetentionPolicy()

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            version=generated.version,
            delete=generated.delete,
            read=generated.read,
            write=generated.write,
            retention_policy=RetentionPolicy._from_generated(generated.retention_policy)  # pylint: disable=protected-access
        )


class Metrics(GeneratedMetrics):
    """A summary of request statistics grouped by API in hour or minute aggregates.

    All required parameters must be populated in order to send to Azure.

    :keyword str version: The version of Storage Analytics to configure.
    :keyword bool enabled: Required. Indicates whether metrics are enabled for the service.
    :keyword bool include_ap_is: Indicates whether metrics should generate summary
        statistics for called API operations.
    :keyword ~azure.storage.queue.RetentionPolicy retention_policy: Required.
        The retention policy for the metrics.
    """

    def __init__(self, **kwargs):
        self.version = kwargs.get('version', u'1.0')
        self.enabled = kwargs.get('enabled', False)
        self.include_apis = kwargs.get('include_apis')
        self.retention_policy = kwargs.get('retention_policy') or RetentionPolicy()

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            version=generated.version,
            enabled=generated.enabled,
            include_apis=generated.include_apis,
            retention_policy=RetentionPolicy._from_generated(generated.retention_policy)  # pylint: disable=protected-access
        )


class RetentionPolicy(GeneratedRetentionPolicy):
    """The retention policy which determines how long the associated data should
    persist.

    All required parameters must be populated in order to send to Azure.

    :param bool enabled: Required. Indicates whether a retention policy is enabled
        for the storage service.
    :param int days: Indicates the number of days that metrics or logging or
        soft-deleted data should be retained. All data older than this value will
        be deleted.
    """

    def __init__(self, enabled=False, days=None):
        self.enabled = enabled
        self.days = days
        if self.enabled and (self.days is None):
            raise ValueError("If policy is enabled, 'days' must be specified.")

    @classmethod
    def _from_generated(cls, generated):
        if not generated:
            return cls()
        return cls(
            enabled=generated.enabled,
            days=generated.days,
        )


class CorsRule(GeneratedCorsRule):
    """CORS is an HTTP feature that enables a web application running under one
    domain to access resources in another domain. Web browsers implement a
    security restriction known as same-origin policy that prevents a web page
    from calling APIs in a different domain; CORS provides a secure way to
    allow one domain (the origin domain) to call APIs in another domain.

    All required parameters must be populated in order to send to Azure.

    :param list(str) allowed_origins:
        A list of origin domains that will be allowed via CORS, or "*" to allow
        all domains. The list of must contain at least one entry. Limited to 64
        origin domains. Each allowed origin can have up to 256 characters.
    :param list(str) allowed_methods:
        A list of HTTP methods that are allowed to be executed by the origin.
        The list of must contain at least one entry. For Azure Storage,
        permitted methods are DELETE, GET, HEAD, MERGE, POST, OPTIONS or PUT.
    :keyword int max_age_in_seconds:
        The number of seconds that the client/browser should cache a
        pre-flight response.
    :keyword list(str) exposed_headers:
        Defaults to an empty list. A list of response headers to expose to CORS
        clients. Limited to 64 defined headers and two prefixed headers. Each
        header can be up to 256 characters.
    :keyword list(str) allowed_headers:
        Defaults to an empty list. A list of headers allowed to be part of
        the cross-origin request. Limited to 64 defined headers and 2 prefixed
        headers. Each header can be up to 256 characters.
    """

    def __init__(self, allowed_origins, allowed_methods, **kwargs):
        self.allowed_origins = ','.join(allowed_origins)
        self.allowed_methods = ','.join(allowed_methods)
        self.allowed_headers = ','.join(kwargs.get('allowed_headers', []))
        self.exposed_headers = ','.join(kwargs.get('exposed_headers', []))
        self.max_age_in_seconds = kwargs.get('max_age_in_seconds', 0)

    @classmethod
    def _from_generated(cls, generated):
        return cls(
            [generated.allowed_origins],
            [generated.allowed_methods],
            allowed_headers=[generated.allowed_headers],
            exposed_headers=[generated.exposed_headers],
            max_age_in_seconds=generated.max_age_in_seconds,
        )

class TablePropertiesPaged(PageIterator):
    """An iterable of Table properties.

    :ivar str service_endpoint: The service URL.
    :ivar str prefix: A queue name prefix being used to filter the list.
    :ivar str marker: The continuation token of the current page of results.
    :ivar int results_per_page: The maximum number of results retrieved per API call.
    :ivar str next_marker: The continuation token to retrieve the next page of results.
    :ivar str location_mode: The location mode being used to list results. The available
        options include "primary" and "secondary".
    :param callable command: Function to retrieve the next page of items.
    :param str prefix: Filters the results to return only queues whose names
        begin with the specified prefix.
    :param int results_per_page: The maximum number of queue names to retrieve per
        call.
    :param str continuation_token: An opaque continuation token.
    """
    def __init__(self, command, prefix=None, results_per_page=None, continuation_token=None):
        super(TablePropertiesPaged, self).__init__(
            self._get_next_cb,
            self._extract_data_cb,
            continuation_token=continuation_token or ""
        )
        self._command = command
        self.service_endpoint = None
        self.prefix = prefix
        self.marker = None
        self.results_per_page = results_per_page
        self.location_mode = None

    def _get_next_cb(self, continuation_token):
        try:
            return self._command(
                 cls=return_context_and_deserialized,
                 use_location=self.location_mode)
        except HttpResponseError as error:
            process_storage_error(error)

    def _extract_data_cb(self, get_next_return):
        self.location_mode, self._response = get_next_return
        props_list = [t for t in self._response.value]
        # props_list = [TableProperties._from_generated(q) for q in self._response.value] # pylint: disable=protected-access
        # return self._response.next_marker or None, props_list
        return None, props_list

def service_stats_deserialize(generated):
    """Deserialize a ServiceStats objects into a dict.
    """
    return {
        'geo_replication': {
            'status': generated.geo_replication.status,
            'last_sync_time': generated.geo_replication.last_sync_time,
        }
    }


def service_properties_deserialize(generated):
    """Deserialize a ServiceProperties objects into a dict.
    """
    return {
        'analytics_logging': TableAnalyticsLogging._from_generated(generated.logging),  # pylint: disable=protected-access
        'hour_metrics': Metrics._from_generated(generated.hour_metrics),  # pylint: disable=protected-access
        'minute_metrics': Metrics._from_generated(generated.minute_metrics),  # pylint: disable=protected-access
        'cors': [CorsRule._from_generated(cors) for cors in generated.cors],  # pylint: disable=protected-access
    }
