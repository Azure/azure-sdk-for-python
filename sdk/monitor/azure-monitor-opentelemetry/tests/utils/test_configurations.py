# Copyright The OpenTelemetry Authors
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

from os import environ
from unittest import TestCase
from unittest.mock import patch

from opentelemetry.instrumentation.environment_variables import (
    OTEL_PYTHON_DISABLED_INSTRUMENTATIONS,
)
from azure.monitor.opentelemetry._utils.configurations import (
    SAMPLING_RATIO_ENV_VAR,
    _get_configurations,
)
from opentelemetry.environment_variables import (
    OTEL_LOGS_EXPORTER,
    OTEL_METRICS_EXPORTER,
    OTEL_TRACES_EXPORTER,
)
from opentelemetry.sdk.environment_variables import OTEL_EXPERIMENTAL_RESOURCE_DETECTORS
from opentelemetry.sdk.resources import Resource, Attributes

from azure.monitor.opentelemetry._version import VERSION


TEST_DEFAULT_RESOURCE = Resource({
    "test.attributes.1": "test_value_1",
    "test.attributes.2": "test_value_2"
})
TEST_CUSTOM_RESOURCE = Resource({
    "test.attributes.2": "test_value_4",
    "test.attributes.3": "test_value_3"
})
TEST_MERGED_RESOURCE = Resource({
    "test.attributes.1": "test_value_1",
    "test.attributes.2": "test_value_4",
    "test.attributes.3": "test_value_3"
})


class TestConfigurations(TestCase):
    @patch.dict("os.environ", {}, clear=True)
    @patch("azure.monitor.opentelemetry._utils.configurations._PREVIEW_INSTRUMENTED_LIBRARIES", ("previewlib1", "previewlib2"))
    @patch("opentelemetry.sdk.resources.Resource.create", return_value=TEST_MERGED_RESOURCE)
    def test_get_configurations(self, resource_create_mock):
        configurations = _get_configurations(
            connection_string="test_cs",
            credential="test_credential",
            resource=TEST_CUSTOM_RESOURCE,
            storage_directory="test_directory",
            sampling_ratio=0.5,
            instrumentation_options={
                "flask": {
                    "enabled": False,
                }
            },
            enable_live_metrics=True,
            views=["test_view"],
            logger_name="test_logger",
            span_processors=["test_processor"],
        )

        self.assertEqual(configurations["connection_string"], "test_cs")
        self.assertEqual(configurations["distro_version"], VERSION)
        self.assertEqual(configurations["disable_logging"], False)
        self.assertEqual(configurations["disable_metrics"], False)
        self.assertEqual(configurations["disable_tracing"], False)
        self.assertEqual(configurations["resource"].attributes, TEST_MERGED_RESOURCE.attributes)
        self.assertEqual(environ[OTEL_EXPERIMENTAL_RESOURCE_DETECTORS], "azure_app_service,azure_vm")
        resource_create_mock.assert_called_once_with(TEST_CUSTOM_RESOURCE.attributes)
        self.assertEqual(configurations["sampling_ratio"], 1.0)
        self.assertEqual(configurations["credential"], "test_credential")
        self.assertEqual(configurations["instrumentation_options"], {
            "azure_sdk" : {"enabled": True},
            "django": {"enabled": True},
            "fastapi": {"enabled": True},
            "flask": {"enabled": False},
            "psycopg2": {"enabled": True},
            "requests": {"enabled": True},
            "urllib": {"enabled": True},
            "urllib3": {"enabled": True},
            "previewlib1": {"enabled": False},
            "previewlib2": {"enabled": False},
        })
        self.assertEqual(configurations["storage_directory"], "test_directory")
        self.assertEqual(configurations["enable_live_metrics"], True)
        self.assertEqual(configurations["views"], ["test_view"])
        self.assertEqual(configurations["logger_name"], "test_logger")
        self.assertEqual(configurations["span_processors"], ["test_processor"])

    @patch.dict("os.environ", {}, clear=True)
    @patch("opentelemetry.sdk.resources.Resource.create", return_value=TEST_DEFAULT_RESOURCE)
    def test_get_configurations_defaults(self, resource_create_mock):
        configurations = _get_configurations()

        self.assertTrue("connection_string" not in configurations)
        self.assertEqual(configurations["disable_logging"], False)
        self.assertEqual(configurations["disable_metrics"], False)
        self.assertEqual(configurations["disable_tracing"], False)
        self.assertEqual(configurations["instrumentation_options"], {
            "azure_sdk" : {"enabled": True},
            "django" : {"enabled": True},
            "fastapi" : {"enabled": True},
            "flask" : {"enabled": True},
            "psycopg2" : {"enabled": True},
            "requests": {"enabled": True},
            "urllib": {"enabled": True},
            "urllib3": {"enabled": True},
        })
        self.assertEqual(configurations["resource"].attributes, TEST_DEFAULT_RESOURCE.attributes)
        self.assertEqual(environ[OTEL_EXPERIMENTAL_RESOURCE_DETECTORS], "azure_app_service,azure_vm")
        resource_create_mock.assert_called_once_with()
        self.assertEqual(configurations["sampling_ratio"], 1.0)
        self.assertTrue("credential" not in configurations)
        self.assertTrue("storage_directory" not in configurations)
        self.assertEqual(configurations["enable_live_metrics"], False)
        self.assertEqual(configurations["logger_name"], "")
        self.assertEqual(configurations["span_processors"], [])
        self.assertEqual(configurations["views"], [])

    @patch.dict(
        "os.environ",
        {
            OTEL_PYTHON_DISABLED_INSTRUMENTATIONS: "flask,requests,fastapi,azure_sdk",
            SAMPLING_RATIO_ENV_VAR: "0.5",
            OTEL_TRACES_EXPORTER: "None",
            OTEL_LOGS_EXPORTER: "none",
            OTEL_METRICS_EXPORTER: "NONE",
            OTEL_EXPERIMENTAL_RESOURCE_DETECTORS: "custom_resource_detector"
        },
        clear=True,
    )
    @patch("opentelemetry.sdk.resources.Resource.create", return_value=TEST_DEFAULT_RESOURCE)
    def test_get_configurations_env_vars(self, resource_create_mock):
        configurations = _get_configurations()

        self.assertTrue("connection_string" not in configurations)
        self.assertEqual(configurations["disable_logging"], True)
        self.assertEqual(configurations["disable_metrics"], True)
        self.assertEqual(configurations["disable_tracing"], True)
        self.assertEqual(configurations["instrumentation_options"], {
            "azure_sdk" : {"enabled": False},
            "django" : {"enabled": True},
            "fastapi" : {"enabled": False},
            "flask" : {"enabled": False},
            "psycopg2" : {"enabled": True},
            "requests": {"enabled": False},
            "urllib": {"enabled": True},
            "urllib3": {"enabled": True},
        })
        self.assertEqual(configurations["resource"].attributes, TEST_DEFAULT_RESOURCE.attributes)
        self.assertEqual(environ[OTEL_EXPERIMENTAL_RESOURCE_DETECTORS], "custom_resource_detector")
        resource_create_mock.assert_called_once_with()
        self.assertEqual(configurations["sampling_ratio"], 0.5)

    @patch.dict(
        "os.environ",
        {
            SAMPLING_RATIO_ENV_VAR: "Half",
            OTEL_TRACES_EXPORTER: "False",
            OTEL_LOGS_EXPORTER: "no",
            OTEL_METRICS_EXPORTER: "True",
        },
        clear=True,
    )
    @patch("opentelemetry.sdk.resources.Resource.create", return_value=TEST_DEFAULT_RESOURCE)
    def test_get_configurations_env_vars_validation(self, resource_create_mock):
        configurations = _get_configurations()

        self.assertTrue("connection_string" not in configurations)
        self.assertEqual(configurations["disable_logging"], False)
        self.assertEqual(configurations["disable_metrics"], False)
        self.assertEqual(configurations["disable_tracing"], False)
        self.assertEqual(configurations["sampling_ratio"], 1.0)

    @patch.dict(
        "os.environ",
        {
            OTEL_PYTHON_DISABLED_INSTRUMENTATIONS: "django , urllib3,previewlib1,azure_sdk",
        },
        clear=True,
    )
    @patch("opentelemetry.sdk.resources.Resource.create", return_value=TEST_DEFAULT_RESOURCE)
    @patch("azure.monitor.opentelemetry._utils.configurations._PREVIEW_INSTRUMENTED_LIBRARIES", ("previewlib1", "previewlib2"))
    def test_merge_instrumentation_options_conflict(self, resource_create_mock):
        configurations = _get_configurations(
            instrumentation_options = {
                "azure_sdk" : {"enabled": True},
                "django" : {"enabled": True},
                "fastapi" : {"enabled": True},
                "flask" : {"enabled": False},
                "previewlib1": {"enabled": True},
            }
        )

        self.assertEqual(configurations["instrumentation_options"], {
            "azure_sdk" : {"enabled": True}, # Explicit configuration takes priority
            "django" : {"enabled": True}, # Explicit configuration takes priority
            "fastapi" : {"enabled": True},
            "flask" : {"enabled": False},
            "psycopg2" : {"enabled": True},
            "previewlib1": {"enabled": True}, # Explicit configuration takes priority
            "previewlib2": {"enabled": False},
            "requests": {"enabled": True},
            "urllib": {"enabled": True},
            "urllib3": {"enabled": False},
        })

    @patch.dict("os.environ", {}, clear=True)
    @patch("azure.monitor.opentelemetry._utils.configurations._PREVIEW_INSTRUMENTED_LIBRARIES", ("previewlib1", "previewlib2"))
    @patch("opentelemetry.sdk.resources.Resource.create", return_value=TEST_DEFAULT_RESOURCE)
    def test_merge_instrumentation_options_extra_args(self, resource_create_mock):
        configurations = _get_configurations(
            instrumentation_options = {
                "django" : {"enabled": True},
                "fastapi" : {"enabled": True, "foo": "bar"},
                "flask" : {"enabled": False, "foo": "bar"},
                "psycopg2" : {"foo": "bar"},
                "previewlib1": {"enabled": True, "foo": "bar"},
                "previewlib2": {"foo": "bar"},
            }
        )

        self.assertEqual(configurations["instrumentation_options"], {
            "azure_sdk" : {"enabled": True},
            "django" : {"enabled": True},
            "fastapi" : {"enabled": True, "foo": "bar"},
            "flask" : {"enabled": False, "foo": "bar"},
            "psycopg2" : {"enabled": True, "foo": "bar"},
            "previewlib1": {"enabled": True, "foo": "bar"},
            "previewlib2": {"enabled": False, "foo": "bar"},
            "requests": {"enabled": True},
            "urllib": {"enabled": True},
            "urllib3": {"enabled": True},
        })
