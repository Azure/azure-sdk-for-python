# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from datetime import datetime, timezone
from urllib.parse import parse_qs, urlsplit
from urllib.parse import urlparse

import pytest
from azure.core import MatchConditions
from azure.storage.blob import ContainerClient, StandardBlobTier
from azure.storage.blob import RehydratePriority
from azure.storage.blob._container_client_helpers import (
    _generate_delete_blobs_options,
    _generate_delete_blobs_subrequest_options,
    _generate_set_tiers_subrequest_options,
)
from azure.storage.blob._container_client_helpers import _generate_set_tiers_options
from azure.storage.blob._serialize import get_access_conditions, get_modify_conditions

from devtools_testutils.storage import StorageRecordedTestCase
from settings.testcase import BlobPreparer


class TestContainerClientHelpersGaps(StorageRecordedTestCase):

    def test_container_client_init_when_account_url_is_not_string_raises_value_error(self):
        with pytest.raises(ValueError) as error:
            ContainerClient(account_url=1, container_name='container', credential='fake_key')

        assert str(error.value) == 'Container URL must be a string.'

    def test_container_client_init_when_account_url_is_not_string_sets_attribute_error_as_cause(self):
        with pytest.raises(ValueError) as error:
            ContainerClient(account_url=object(), container_name='container', credential='fake_key')

        assert type(error.value.__cause__) is AttributeError
        assert str(error.value.__cause__) == "'object' object has no attribute 'lower'"

    def test_container_client_init_when_container_name_missing_or_url_invalid_raises_value_error(self):
        with pytest.raises(ValueError) as error:
            ContainerClient(
                account_url='https://fakestorage.blob.core.windows.net',
                container_name='',
                credential='fake_key'
            )
        assert str(error.value) == 'Please specify a container name.'

        with pytest.raises(ValueError) as error:
            ContainerClient(account_url='https://', container_name='container', credential='fake_key')
        assert str(error.value) == 'Invalid URL: https://'

    def test_container_client_init_when_container_name_is_bytes_preserves_encoded_url(self):
        client = ContainerClient(
            account_url='https://fakestorage.blob.core.windows.net',
            container_name=b'foo bar',
            credential='fake_key'
        )

        assert client.container_name == b'foo bar'
        assert client.url == 'https://fakestorage.blob.core.windows.net/foo%20bar'

    def test_delete_blobs_when_blob_has_lease_id_adds_lease_header_to_subrequest(self):
        client = ContainerClient(
            account_url='https://fakestorage.blob.core.windows.net',
            container_name='container',
            credential='fake_key'
        )
        client._batch_send = lambda *reqs, **kwargs: (reqs, kwargs)

        reqs, options = client.delete_blobs({'name': 'blob-name', 'lease_id': 'lease-1234'})

        assert len(reqs) == 1
        assert reqs[0].method == 'DELETE'
        assert reqs[0].url == '/container/blob-name?'
        assert reqs[0].headers['x-ms-lease-id'] == 'lease-1234'
        assert options['raise_on_any_failure'] is True

    def _create_container_client(self, storage_account_name, storage_account_key):
        return ContainerClient(
            self.account_url(storage_account_name, "blob"),
            "container",
            credential=storage_account_key.secret,
        )

    def _capture_batch_requests(self, container_client):
        captured = {}

        def fake_batch_send(*reqs, **kwargs):
            captured['reqs'] = reqs
            captured['kwargs'] = kwargs
            return []

        container_client._batch_send = fake_batch_send
        return captured

    @BlobPreparer()
    def test_delete_blobs_when_blob_has_if_modified_since_adds_modified_since_header(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container = self._create_container_client(storage_account_name, storage_account_key)
        captured = self._capture_batch_requests(container)
        if_modified_since = datetime(2020, 1, 1, 12, 0, 0)

        # Act
        container.delete_blobs({"name": "blob1", "if_modified_since": if_modified_since})

        # Assert
        assert len(captured['reqs']) == 1
        assert captured['reqs'][0].headers['If-Modified-Since'] == 'Wed, 01 Jan 2020 12:00:00 GMT'

    @BlobPreparer()
    def test_delete_blobs_when_blob_has_if_unmodified_since_adds_unmodified_since_header(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container = self._create_container_client(storage_account_name, storage_account_key)
        captured = self._capture_batch_requests(container)
        if_unmodified_since = datetime(2020, 1, 2, 12, 0, 0)

        # Act
        container.delete_blobs({"name": "blob1", "if_unmodified_since": if_unmodified_since})

        # Assert
        assert len(captured['reqs']) == 1
        assert captured['reqs'][0].headers['If-Unmodified-Since'] == 'Thu, 02 Jan 2020 12:00:00 GMT'

    @BlobPreparer()
    def test_delete_blobs_when_blob_has_etag_and_if_not_modified_match_condition_adds_match_header(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container = self._create_container_client(storage_account_name, storage_account_key)
        captured = self._capture_batch_requests(container)
        etag = '0x8D1234567890ABC'

        # Act
        container.delete_blobs({
            "name": "blob1",
            "etag": etag,
            "match_condition": MatchConditions.IfNotModified,
        })

        # Assert
        assert len(captured['reqs']) == 1
        assert captured['reqs'][0].headers['If-Match'] == etag

    @BlobPreparer()
    def test_delete_blobs_when_blob_has_etag_and_if_modified_match_condition_adds_none_match_header(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container = self._create_container_client(storage_account_name, storage_account_key)
        captured = self._capture_batch_requests(container)
        etag = '0x8DABCDEF1234567'

        # Act
        container.delete_blobs({
            "name": "blob1",
            "etag": etag,
            "match_condition": MatchConditions.IfModified,
        })

        # Assert
        assert len(captured['reqs']) == 1
        assert captured['reqs'][0].headers['If-None-Match'] == etag

    @BlobPreparer()
    def test_delete_blobs_when_blob_has_if_tags_match_condition_adds_tags_header(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        container = self._create_container_client(storage_account_name, storage_account_key)
        captured = self._capture_batch_requests(container)
        if_tags_match_condition = '"tag1"=\'value1\''

        # Act
        container.delete_blobs({"name": "blob1", "if_tags_match_condition": if_tags_match_condition})

        # Assert
        assert len(captured['reqs']) == 1
        assert captured['reqs'][0].headers['x-ms-if-tags'] == if_tags_match_condition

    def _get_generated_client(self, storage_account_name, storage_account_key):
        container_client = ContainerClient(
            self.account_url(storage_account_name, "blob"),
            container_name="container",
            credential=storage_account_key.secret,
        )
        return container_client._client

    @BlobPreparer()
    def test_delete_blobs_when_blob_snapshot_provided_adds_snapshot_query_parameter(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        client = self._get_generated_client(storage_account_name, storage_account_key)
        snapshot = "2024-01-02T03:04:05.0000000Z"

        reqs, _ = _generate_delete_blobs_options(
            "?sig=fakesig",
            "container",
            client,
            {"name": "blob", "snapshot": snapshot},
        )

        query = parse_qs(urlsplit(reqs[0].url).query)
        assert len(reqs) == 1
        assert reqs[0].method == "DELETE"
        assert reqs[0].url.startswith("/container/blob?")
        assert query["sig"] == ["fakesig"]
        assert query["snapshot"] == [snapshot]

    @BlobPreparer()
    def test_delete_blobs_when_blob_timeout_provided_adds_timeout_query_parameter(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        client = self._get_generated_client(storage_account_name, storage_account_key)

        reqs, _ = _generate_delete_blobs_options(
            "?sig=fakesig",
            "container",
            client,
            {"name": "blob", "timeout": 7},
        )

        query = parse_qs(urlsplit(reqs[0].url).query)
        assert len(reqs) == 1
        assert reqs[0].method == "DELETE"
        assert reqs[0].url.startswith("/container/blob?")
        assert query["sig"] == ["fakesig"]
        assert query["timeout"] == ["7"]

    @BlobPreparer()
    def test_delete_blobs_when_delete_snapshots_specified_adds_delete_snapshots_header(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        client = self._get_generated_client(storage_account_name, storage_account_key)

        reqs, _ = _generate_delete_blobs_options(
            "?sig=fakesig",
            "container",
            client,
            "blob",
            delete_snapshots="include",
        )

        assert len(reqs) == 1
        assert reqs[0].method == "DELETE"
        assert reqs[0].headers["x-ms-delete-snapshots"] == "include"

    @BlobPreparer()
    def test_generate_delete_blobs_subrequest_options_when_lease_access_conditions_present_adds_lease_header(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        client = self._get_generated_client(storage_account_name, storage_account_key)
        lease_id = "00000000-1111-2222-3333-444444444444"
        lease_access_conditions = get_access_conditions(lease_id)

        query_parameters, header_parameters = _generate_delete_blobs_subrequest_options(
            client,
            lease_access_conditions=lease_access_conditions,
        )

        assert query_parameters == {}
        assert header_parameters == {"x-ms-lease-id": lease_id}

    @BlobPreparer()
    def test_generate_delete_blobs_subrequest_options_when_if_modified_since_present_adds_modified_since_header(self, **kwargs):
        storage_account_name = kwargs.pop("storage_account_name")
        storage_account_key = kwargs.pop("storage_account_key")

        client = self._get_generated_client(storage_account_name, storage_account_key)
        if_modified_since = datetime(2024, 1, 2, 3, 4, 5)
        modified_access_conditions = get_modify_conditions({"if_modified_since": if_modified_since})

        query_parameters, header_parameters = _generate_delete_blobs_subrequest_options(
            client,
            modified_access_conditions=modified_access_conditions,
        )

        assert query_parameters == {}
        assert header_parameters == {"If-Modified-Since": "Tue, 02 Jan 2024 03:04:05 GMT"}


class TestContainerClientHelpers(StorageRecordedTestCase):

    def _get_generated_client(self):
        return ContainerClient(
            "https://fakename.blob.core.windows.net",
            "container",
            credential="fake_key"
        )._client

    def test_generate_delete_blobs_subrequest_options_when_if_unmodified_since_present_adds_unmodified_since_header(self):
        client = self._get_generated_client()
        modified_access_conditions = get_modify_conditions({
            "if_unmodified_since": datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        })

        query_parameters, header_parameters = _generate_delete_blobs_subrequest_options(
            client,
            modified_access_conditions=modified_access_conditions,
        )

        assert query_parameters == {}
        assert header_parameters == {"If-Unmodified-Since": "Mon, 01 Jan 2024 12:00:00 GMT"}

    def test_generate_delete_blobs_subrequest_options_when_if_none_match_present_adds_none_match_header(self):
        client = self._get_generated_client()
        modified_access_conditions = get_modify_conditions({"if_none_match": '"etag-1"'})

        query_parameters, header_parameters = _generate_delete_blobs_subrequest_options(
            client,
            modified_access_conditions=modified_access_conditions,
        )

        assert query_parameters == {}
        assert header_parameters == {"If-None-Match": '"etag-1"'}

    def test_generate_set_tiers_subrequest_options_when_tier_missing_raises_value_error(self):
        client = self._get_generated_client()

        with pytest.raises(ValueError) as exc:
            _generate_set_tiers_subrequest_options(client=client, tier=None)

        assert str(exc.value) == "A blob tier must be specified"

    def test_generate_set_tiers_subrequest_options_when_lease_access_conditions_missing_omits_lease_header(self):
        client = self._get_generated_client()

        query_parameters, header_parameters = _generate_set_tiers_subrequest_options(
            client=client,
            tier=StandardBlobTier.Hot,
            if_tags='"tag"=\'value\'',
            timeout=7,
        )

        assert query_parameters == {"timeout": "7", "comp": "tier"}
        assert header_parameters == {
            "x-ms-access-tier": "Hot",
            "x-ms-if-tags": '"tag"=\'value\''
        }

    def test_generate_set_tiers_subrequest_options_when_lease_access_conditions_present_adds_lease_header(self):
        client = self._get_generated_client()
        lease_access_conditions = get_access_conditions("lease-id")

        query_parameters, header_parameters = _generate_set_tiers_subrequest_options(
            client=client,
            tier=StandardBlobTier.Cool,
            lease_access_conditions=lease_access_conditions,
        )

        assert query_parameters == {"comp": "tier"}
        assert header_parameters == {
            "x-ms-access-tier": "Cool",
            "x-ms-lease-id": "lease-id"
        }


class _FakeSerializer(object):
    def __init__(self):
        self.query_calls = []
        self.header_calls = []

    def query(self, name, value, data_type, **kwargs):
        self.query_calls.append((name, value, data_type, kwargs))
        return value

    def header(self, name, value, data_type):
        self.header_calls.append((name, value, data_type))
        return value


class _FakeGeneratedClient(object):
    def __init__(self):
        self._serialize = _FakeSerializer()


class TestContainerClientHelpersAdditional(StorageRecordedTestCase):

    def test_generate_set_tiers_subrequest_options_when_timeout_not_provided_omits_timeout_query_parameter(self):
        client = _FakeGeneratedClient()

        query_parameters, header_parameters = _generate_set_tiers_subrequest_options(
            client=client,
            tier=StandardBlobTier.Hot,
        )

        assert query_parameters == {'comp': 'tier'}
        assert header_parameters == {'x-ms-access-tier': StandardBlobTier.Hot}
        assert client._serialize.query_calls == [('comp', 'tier', 'str', {})]

    def test_generate_set_tiers_subrequest_options_when_version_id_provided_adds_versionid_and_comp_query_parameters(self):
        client = _FakeGeneratedClient()
        version_id = '2024-05-04T12:00:00.0000000Z'

        query_parameters, header_parameters = _generate_set_tiers_subrequest_options(
            client=client,
            tier=StandardBlobTier.Cool,
            version_id=version_id,
        )

        assert query_parameters == {'versionid': version_id, 'comp': 'tier'}
        assert header_parameters == {'x-ms-access-tier': StandardBlobTier.Cool}
        assert client._serialize.query_calls == [
            ('version_id', version_id, 'str', {}),
            ('comp', 'tier', 'str', {}),
        ]

    def test_generate_set_tiers_subrequest_options_when_snapshot_provided_adds_snapshot_query_parameter(self):
        client = _FakeGeneratedClient()
        snapshot = '2024-05-04T12:00:00.0000000Z'

        query_parameters, header_parameters = _generate_set_tiers_subrequest_options(
            client=client,
            tier=StandardBlobTier.Archive,
            snapshot=snapshot,
        )

        assert query_parameters == {'snapshot': snapshot, 'comp': 'tier'}
        assert header_parameters == {'x-ms-access-tier': StandardBlobTier.Archive}
        assert client._serialize.query_calls == [
            ('snapshot', snapshot, 'str', {}),
            ('comp', 'tier', 'str', {}),
        ]

    def test_generate_set_tiers_subrequest_options_when_timeout_provided_adds_timeout_query_parameter(self):
        client = _FakeGeneratedClient()

        query_parameters, header_parameters = _generate_set_tiers_subrequest_options(
            client=client,
            tier=StandardBlobTier.Cool,
            timeout=15,
        )

        assert query_parameters == {'timeout': 15, 'comp': 'tier'}
        assert header_parameters == {'x-ms-access-tier': StandardBlobTier.Cool}
        assert client._serialize.query_calls == [
            ('timeout', 15, 'int', {'minimum': 0}),
            ('comp', 'tier', 'str', {}),
        ]

    def test_generate_set_tiers_subrequest_options_when_rehydrate_priority_and_if_tags_provided_adds_optional_headers(self):
        client = _FakeGeneratedClient()
        if_tags = '"tag"=\'value\''

        query_parameters, header_parameters = _generate_set_tiers_subrequest_options(
            client=client,
            tier=StandardBlobTier.Archive,
            rehydrate_priority=RehydratePriority.standard,
            if_tags=if_tags,
        )

        assert query_parameters == {'comp': 'tier'}
        assert header_parameters == {
            'x-ms-access-tier': StandardBlobTier.Archive,
            'x-ms-rehydrate-priority': RehydratePriority.standard,
            'x-ms-if-tags': if_tags,
        }
        assert client._serialize.header_calls == [
            ('tier', StandardBlobTier.Archive, 'str'),
            ('rehydrate_priority', RehydratePriority.standard, 'str'),
            ('if_tags', if_tags, 'str'),
        ]


class _SetTiersFakeSerializer(object):
    @staticmethod
    def _serialize_value(value):
        return str(getattr(value, "value", value))

    def query(self, name, value, data_type, **kwargs):
        return self._serialize_value(value)

    def header(self, name, value, data_type):
        return self._serialize_value(value)


class _SetTiersFakeClient(object):
    def __init__(self):
        self._serialize = _SetTiersFakeSerializer()


class TestContainerClientHelpersSetTiersOptionsGaps(object):

    def test_generate_set_tiers_subrequest_options_when_tier_provided_adds_access_tier_header(self):
        client = _SetTiersFakeClient()

        query_parameters, header_parameters = _generate_set_tiers_subrequest_options(
            client=client,
            tier=StandardBlobTier.Cool,
        )

        assert query_parameters == {"comp": "tier"}
        assert header_parameters == {"x-ms-access-tier": "Cool"}

    def test_generate_set_tiers_options_when_blob_has_rehydrate_priority_adds_rehydrate_priority_header(self):
        client = _SetTiersFakeClient()

        reqs, batch_options = _generate_set_tiers_options(
            "?sig=foo",
            "container",
            None,
            client,
            {
                "name": "blob",
                "blob_tier": StandardBlobTier.Archive,
                "rehydrate_priority": RehydratePriority.high,
            },
        )

        parsed_query = parse_qs(urlparse(reqs[0].url).query)
        assert parsed_query == {"sig": ["foo"], "comp": ["tier"]}
        assert reqs[0].headers["x-ms-access-tier"] == "Archive"
        assert reqs[0].headers["x-ms-rehydrate-priority"] == RehydratePriority.high.value
        assert batch_options["raise_on_any_failure"] is True

    def test_generate_set_tiers_options_when_blob_has_lease_access_conditions_adds_lease_header(self):
        client = _SetTiersFakeClient()
        lease_id = "00000000-1111-2222-3333-444444444444"

        reqs, batch_options = _generate_set_tiers_options(
            "?sig=foo",
            "container",
            StandardBlobTier.Hot,
            client,
            {
                "name": "blob",
                "lease_id": get_access_conditions(lease_id),
            },
        )

        parsed_query = parse_qs(urlparse(reqs[0].url).query)
        assert parsed_query == {"sig": ["foo"], "comp": ["tier"]}
        assert reqs[0].headers["x-ms-access-tier"] == "Hot"
        assert reqs[0].headers["x-ms-lease-id"] == lease_id
        assert batch_options["path"] == "container"

    def test_generate_set_tiers_options_when_timeout_provided_formats_timeout_in_request_and_options(self):
        client = _SetTiersFakeClient()

        reqs, batch_options = _generate_set_tiers_options(
            "?sig=foo",
            "container",
            StandardBlobTier.Cool,
            client,
            {"name": "blob"},
            timeout=9,
        )

        parsed_query = parse_qs(urlparse(reqs[0].url).query)
        assert parsed_query == {"sig": ["foo"], "timeout": ["9"], "comp": ["tier"]}
        assert reqs[0].headers["x-ms-access-tier"] == "Cool"
        assert batch_options["timeout"] == "&timeout=9"

    def test_generate_set_tiers_options_when_raise_on_any_failure_false_updates_batch_options(self):
        client = _SetTiersFakeClient()

        reqs, batch_options = _generate_set_tiers_options(
            "?sig=foo",
            "container",
            StandardBlobTier.Hot,
            client,
            "blob",
            raise_on_any_failure=False,
        )

        parsed_query = parse_qs(urlparse(reqs[0].url).query)
        assert parsed_query == {"sig": ["foo"], "comp": ["tier"]}
        assert reqs[0].headers["x-ms-access-tier"] == "Hot"
        assert batch_options["raise_on_any_failure"] is False
        assert batch_options["sas"] == "&sig=foo"
