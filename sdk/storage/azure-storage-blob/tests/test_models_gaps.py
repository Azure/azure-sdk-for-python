# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from types import SimpleNamespace

import pytest

from azure.storage.blob._deserialize import service_properties_deserialize
from azure.storage.blob._models import parse_page_list
from devtools_testutils.storage import StorageRecordedTestCase


class TestModelsGaps(StorageRecordedTestCase):
    def _build_generated_retention_policy(self, enabled=True, days=7):
        return SimpleNamespace(enabled=enabled, days=days)

    def _build_generated_logging(self):
        return SimpleNamespace(
            version='9.9',
            delete=True,
            read=True,
            write=True,
            retention_policy=self._build_generated_retention_policy(enabled=True, days=5)
        )

    def _build_generated_metrics(self):
        return SimpleNamespace(
            version='9.9',
            enabled=True,
            include_apis=True,
            retention_policy=self._build_generated_retention_policy(enabled=True, days=6)
        )

    def _build_generated_static_website(self):
        return SimpleNamespace(
            enabled=True,
            index_document='index.html',
            error_document404_path='errors/404.html',
            default_index_document_path='home/index.html'
        )

    def _build_generated_service_properties(self, **kwargs):
        generated = SimpleNamespace(
            logging=self._build_generated_logging(),
            hour_metrics=self._build_generated_metrics(),
            minute_metrics=self._build_generated_metrics(),
            cors=None,
            default_service_version='2020-10-02',
            delete_retention_policy=self._build_generated_retention_policy(enabled=True, days=3),
            static_website=self._build_generated_static_website()
        )
        for key, value in kwargs.items():
            setattr(generated, key, value)
        return generated

    def test_parse_page_list_when_clear_ranges_none_raises_value_error(self):
        page_list = SimpleNamespace(
            page_range=[SimpleNamespace(start=0, end=511)],
            clear_range=None
        )

        with pytest.raises(ValueError) as error:
            parse_page_list(page_list)

        assert str(error.value) == "PageList's 'clear_ranges' is malformed or None."

    def test_service_properties_deserialize_when_delete_retention_policy_none_returns_default_policy(self):
        generated = self._build_generated_service_properties(delete_retention_policy=None)

        props = service_properties_deserialize(generated)

        assert props['delete_retention_policy'].enabled is False
        assert props['delete_retention_policy'].days is None
        assert props['target_version'] == '2020-10-02'

    def test_service_properties_deserialize_when_logging_none_returns_default_analytics_logging(self):
        generated = self._build_generated_service_properties(logging=None)

        props = service_properties_deserialize(generated)

        assert props['analytics_logging'].version == '1.0'
        assert props['analytics_logging'].delete is False
        assert props['analytics_logging'].read is False
        assert props['analytics_logging'].write is False
        assert props['analytics_logging'].retention_policy.enabled is False
        assert props['analytics_logging'].retention_policy.days is None

    def test_service_properties_deserialize_when_hour_metrics_none_returns_default_metrics(self):
        generated = self._build_generated_service_properties(hour_metrics=None)

        props = service_properties_deserialize(generated)

        assert props['hour_metrics'].version == '1.0'
        assert props['hour_metrics'].enabled is False
        assert props['hour_metrics'].include_apis is None
        assert props['hour_metrics'].retention_policy.enabled is False
        assert props['hour_metrics'].retention_policy.days is None

    def test_service_properties_deserialize_when_static_website_none_returns_disabled_website(self):
        generated = self._build_generated_service_properties(static_website=None)

        props = service_properties_deserialize(generated)

        assert props['static_website'].enabled is False
        assert props['static_website'].index_document is None
        assert props['static_website'].error_document404_path is None
        assert props['static_website'].default_index_document_path is None
