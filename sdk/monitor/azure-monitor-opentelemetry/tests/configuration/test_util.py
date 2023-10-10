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

from unittest import TestCase
from unittest.mock import patch

from opentelemetry.instrumentation.environment_variables import (
    OTEL_PYTHON_DISABLED_INSTRUMENTATIONS,
)
from azure.monitor.opentelemetry._util.configurations import (
    SAMPLING_RATIO_ENV_VAR,
    _get_configurations,
)
from opentelemetry.environment_variables import (
    OTEL_LOGS_EXPORTER,
    OTEL_METRICS_EXPORTER,
    OTEL_TRACES_EXPORTER,
)


class TestUtil(TestCase):
    @patch.dict("os.environ", {}, clear=True)
    @patch("azure.monitor.opentelemetry._util.configurations._PREVIEW_INSTRUMENTED_LIBRARIES", ("previewlib1", "previewlib2"))
    def test_get_configurations(self):
        configurations = _get_configurations(
            connection_string="test_cs",
            credential="test_credential",
        )

        self.assertEqual(configurations["connection_string"], "test_cs")
        self.assertEqual(configurations["disable_logging"], False)
        self.assertEqual(configurations["disable_metrics"], False)
        self.assertEqual(configurations["disable_tracing"], False)
        self.assertEqual(configurations["sampling_ratio"], 1.0)
        self.assertEqual(configurations["credential"], ("test_credential"))
        self.assertEqual(configurations["instrumentation_options"], {
            "azure_sdk" : {"enabled": True},
            "django": {"enabled": True},
            "fastapi": {"enabled": True},
            "flask": {"enabled": True},
            "psycopg2": {"enabled": True},
            "requests": {"enabled": True},
            "urllib": {"enabled": True},
            "urllib3": {"enabled": True},
            "previewlib1": {"enabled": False},
            "previewlib2": {"enabled": False},
        })
        self.assertTrue("storage_directory" not in configurations)

    @patch.dict("os.environ", {}, clear=True)
    def test_get_configurations_defaults(self):
        configurations = _get_configurations()

        self.assertTrue("connection_string" not in configurations)
        self.assertEqual(configurations["disable_logging"], False)
        self.assertEqual(configurations["disable_metrics"], False)
        self.assertEqual(configurations["disable_tracing"], False)
        self.assertEqual(configurations["sampling_ratio"], 1.0)
        self.assertTrue("credential" not in configurations)
        self.assertTrue("storage_directory" not in configurations)

    @patch.dict(
        "os.environ",
        {
            OTEL_PYTHON_DISABLED_INSTRUMENTATIONS: "flask , requests,fastapi,azure_sdk",
            SAMPLING_RATIO_ENV_VAR: "0.5",
            OTEL_TRACES_EXPORTER: "None",
            OTEL_LOGS_EXPORTER: "none",
            OTEL_METRICS_EXPORTER: "NONE",
        },
        clear=True,
    )
    def test_get_configurations_env_vars(self):
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
    def test_get_configurations_env_vars_validation(self):
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
    @patch("azure.monitor.opentelemetry._util.configurations._PREVIEW_INSTRUMENTED_LIBRARIES", ("previewlib1", "previewlib2"))
    def test_merge_instrumentation_options_conflict(self):
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
    @patch("azure.monitor.opentelemetry._util.configurations._PREVIEW_INSTRUMENTED_LIBRARIES", ("previewlib1", "previewlib2"))
    def test_merge_instrumentation_options_extra_args(self):
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
