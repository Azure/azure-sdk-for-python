# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import datetime
import os
import platform
import time
import unittest

from azure.monitor.opentelemetry.exporter import _utils
from azure.monitor.opentelemetry.exporter._generated.models import TelemetryItem
from opentelemetry.sdk.resources import Resource
from unittest.mock import patch


TEST_AI_DEVICE_ID = "TEST_AI_DEVICE_ID"
TEST_AI_DEVICE_LOCALE = "TEST_AI_DEVICE_LOCALE"
TEST_SDK_VERSION_PREFIX = "TEST_AZURE_SDK_VERSION_PREFIX"
TEST_AZURE_MONITOR_CONTEXT = {
    "ai.device.id": TEST_AI_DEVICE_ID,
    "ai.device.locale": TEST_AI_DEVICE_LOCALE,
    "ai.device.type": "Other",
    "ai.internal.sdkVersion": "{}py1.2.3:otel4.5.6:ext7.8.9".format(
        TEST_SDK_VERSION_PREFIX,
    ),
}
TEST_TIMESTAMP = "TEST_TIMESTAMP"
TEST_TIME = "TEST_TIME"
TEST_WEBSITE_SITE_NAME = "TEST_WEBSITE_SITE_NAME"
TEST_KUBERNETES_SERVICE_HOST = "TEST_KUBERNETES_SERVICE_HOST"
TEST_AKS_ARM_NAMESPACE_ID = "TEST_AKS_ARM_NAMESPACE_ID"


class TestUtils(unittest.TestCase):
    def setUp(self):
        self._valid_instrumentation_key = "1234abcd-5678-4efa-8abc-1234567890ab"

    def test_nanoseconds_to_duration(self):
        ns_to_duration = _utils.ns_to_duration
        self.assertEqual(ns_to_duration(0), "0.00:00:00.000")
        self.assertEqual(ns_to_duration(500000), "0.00:00:00.001")  # Rounding
        self.assertEqual(ns_to_duration(1000000), "0.00:00:00.001")
        self.assertEqual(ns_to_duration(1500000), "0.00:00:00.002")  # Rounding
        self.assertEqual(ns_to_duration(1000000000), "0.00:00:01.000")
        self.assertEqual(ns_to_duration(60 * 1000000000), "0.00:01:00.000")
        self.assertEqual(ns_to_duration(3600 * 1000000000), "0.01:00:00.000")
        self.assertEqual(ns_to_duration(86400 * 1000000000), "1.00:00:00.000")

    @patch("time.time")
    def test_ticks_since_dot_net_epoch(self, time_mock):
        current_time = time.time()
        shift_time = int(
            (datetime.datetime(1970, 1, 1, 0, 0, 0) - datetime.datetime(1, 1, 1, 0, 0, 0)).total_seconds()
        ) * (10**7)
        time_mock.return_value = current_time
        ticks = _utils._ticks_since_dot_net_epoch()
        expected_ticks = int(current_time * (10**7)) + shift_time
        self.assertEqual(ticks, expected_ticks)

    def test_populate_part_a_fields(self):
        resource = Resource(
            {
                "service.name": "testServiceName",
                "service.namespace": "testServiceNamespace",
                "service.instance.id": "testServiceInstanceId",
                "device.id": "testDeviceId",
                "device.model.name": "testDeviceModel",
                "device.manufacturer": "testDeviceMake",
                "service.version": "testApplicationVer",
            }
        )
        tags = _utils._populate_part_a_fields(resource)
        self.assertIsNotNone(tags)
        self.assertEqual(tags.get("ai.cloud.role"), "testServiceNamespace.testServiceName")
        self.assertEqual(tags.get("ai.cloud.roleInstance"), "testServiceInstanceId")
        self.assertEqual(tags.get("ai.internal.nodeName"), "testServiceInstanceId")
        self.assertEqual(tags.get("ai.device.id"), "testDeviceId")
        self.assertEqual(tags.get("ai.device.model"), "testDeviceModel")
        self.assertEqual(tags.get("ai.device.oemName"), "testDeviceMake")
        self.assertEqual(tags.get("ai.application.ver"), "testApplicationVer")

    # Default service.name fields should be used when kubernetes values are not present
    def test_populate_part_a_fields_unknown_service(self):
        resource = Resource(
            {
                "service.name": "unknown_servicefoobar",
                "service.namespace": "testServiceNamespace",
                "service.instance.id": "testServiceInstanceId",
                "device.id": "testDeviceId",
                "device.model.name": "testDeviceModel",
                "device.manufacturer": "testDeviceMake",
                "service.version": "testApplicationVer",
            }
        )
        tags = _utils._populate_part_a_fields(resource)
        self.assertIsNotNone(tags)
        self.assertEqual(tags.get("ai.cloud.role"), "testServiceNamespace.unknown_servicefoobar")
        self.assertEqual(tags.get("ai.cloud.roleInstance"), "testServiceInstanceId")
        self.assertEqual(tags.get("ai.internal.nodeName"), "testServiceInstanceId")
        self.assertEqual(tags.get("ai.device.id"), "testDeviceId")
        self.assertEqual(tags.get("ai.device.model"), "testDeviceModel")
        self.assertEqual(tags.get("ai.device.oemName"), "testDeviceMake")
        self.assertEqual(tags.get("ai.application.ver"), "testApplicationVer")

    def test_populate_part_a_fields_default(self):
        resource = Resource({"service.name": "testServiceName"})
        tags = _utils._populate_part_a_fields(resource)
        self.assertIsNotNone(tags)
        self.assertEqual(tags.get("ai.cloud.role"), "testServiceName")
        self.assertEqual(tags.get("ai.cloud.roleInstance"), platform.node())
        self.assertEqual(tags.get("ai.internal.nodeName"), tags.get("ai.cloud.roleInstance"))

    def test_populate_part_a_fields_aks(self):
        resource = Resource(
            {
                "k8s.deployment.name": "testDeploymentName",
                "k8s.replicaset.name": "testReplicaSetName",
                "k8s.statefulset.name": "testStatefulSetName",
                "k8s.job.name": "testJobName",
                "k8s.cronJob.name": "testCronJobName",
                "k8s.daemonset.name": "testDaemonSetName",
                "k8s.pod.name": "testPodName",
            }
        )
        tags = _utils._populate_part_a_fields(resource)
        self.assertIsNotNone(tags)
        self.assertEqual(tags.get("ai.cloud.role"), "testDeploymentName")
        self.assertEqual(tags.get("ai.cloud.roleInstance"), "testPodName")
        self.assertEqual(tags.get("ai.internal.nodeName"), tags.get("ai.cloud.roleInstance"))

    def test_populate_part_a_fields_aks_replica(self):
        resource = Resource(
            {
                "k8s.replicaset.name": "testReplicaSetName",
                "k8s.statefulset.name": "testStatefulSetName",
                "k8s.job.name": "testJobName",
                "k8s.cronjob.name": "testCronJobName",
                "k8s.daemonset.name": "testDaemonSetName",
                "k8s.pod.name": "testPodName",
            }
        )
        tags = _utils._populate_part_a_fields(resource)
        self.assertIsNotNone(tags)
        self.assertEqual(tags.get("ai.cloud.role"), "testReplicaSetName")
        self.assertEqual(tags.get("ai.cloud.roleInstance"), "testPodName")
        self.assertEqual(tags.get("ai.internal.nodeName"), tags.get("ai.cloud.roleInstance"))

    def test_populate_part_a_fields_aks_stateful(self):
        resource = Resource(
            {
                "k8s.statefulset.name": "testStatefulSetName",
                "k8s.job.name": "testJobName",
                "k8s.cronjob.name": "testCronJobName",
                "k8s.daemonset.name": "testDaemonSetName",
                "k8s.pod.name": "testPodName",
            }
        )
        tags = _utils._populate_part_a_fields(resource)
        self.assertIsNotNone(tags)
        self.assertEqual(tags.get("ai.cloud.role"), "testStatefulSetName")
        self.assertEqual(tags.get("ai.cloud.roleInstance"), "testPodName")
        self.assertEqual(tags.get("ai.internal.nodeName"), tags.get("ai.cloud.roleInstance"))

    def test_populate_part_a_fields_aks_job(self):
        resource = Resource(
            {
                "k8s.job.name": "testJobName",
                "k8s.cronjob.name": "testCronJobName",
                "k8s.daemonset.name": "testDaemonSetName",
                "k8s.pod.name": "testPodName",
            }
        )
        tags = _utils._populate_part_a_fields(resource)
        self.assertIsNotNone(tags)
        self.assertEqual(tags.get("ai.cloud.role"), "testJobName")
        self.assertEqual(tags.get("ai.cloud.roleInstance"), "testPodName")
        self.assertEqual(tags.get("ai.internal.nodeName"), tags.get("ai.cloud.roleInstance"))

    def test_populate_part_a_fields_aks_cronjob(self):
        resource = Resource(
            {
                "k8s.cronjob.name": "testCronJobName",
                "k8s.daemonset.name": "testDaemonSetName",
                "k8s.pod.name": "testPodName",
            }
        )
        tags = _utils._populate_part_a_fields(resource)
        self.assertIsNotNone(tags)
        self.assertEqual(tags.get("ai.cloud.role"), "testCronJobName")
        self.assertEqual(tags.get("ai.cloud.roleInstance"), "testPodName")
        self.assertEqual(tags.get("ai.internal.nodeName"), tags.get("ai.cloud.roleInstance"))

    def test_populate_part_a_fields_aks_daemon(self):
        resource = Resource(
            {
                "k8s.daemonset.name": "testDaemonSetName",
                "k8s.pod.name": "testPodName",
            }
        )
        tags = _utils._populate_part_a_fields(resource)
        self.assertIsNotNone(tags)
        self.assertEqual(tags.get("ai.cloud.role"), "testDaemonSetName")
        self.assertEqual(tags.get("ai.cloud.roleInstance"), "testPodName")
        self.assertEqual(tags.get("ai.internal.nodeName"), tags.get("ai.cloud.roleInstance"))

    # Test that undefined fields are ignored.
    def test_populate_part_a_fields_aks_undefined(self):
        resource = Resource(
            {
                "k8s.deployment.name": "",
                "k8s.replicaset.name": None,
                "k8s.statefulset.name": "",
                "k8s.job.name": None,
                "k8s.cronJob.name": "",
                "k8s.daemonset.name": "testDaemonSetName",
                "k8s.pod.name": "testPodName",
            }
        )
        tags = _utils._populate_part_a_fields(resource)
        self.assertIsNotNone(tags)
        self.assertEqual(tags.get("ai.cloud.role"), "testDaemonSetName")
        self.assertEqual(tags.get("ai.cloud.roleInstance"), "testPodName")
        self.assertEqual(tags.get("ai.internal.nodeName"), tags.get("ai.cloud.roleInstance"))

    def test_populate_part_a_fields_aks_with_service(self):
        resource = Resource(
            {
                "service.name": "testServiceName",
                "service.instance.id": "testServiceInstanceId",
                "k8s.deployment.name": "testDeploymentName",
                "k8s.replicaset.name": "testReplicaSetName",
                "k8s.statefulset.name": "testStatefulSetName",
                "k8s.job.name": "testJobName",
                "k8s.cronjob.name": "testCronJobName",
                "k8s.daemonset.name": "testDaemonSetName",
                "k8s.pod.name": "testPodName",
            }
        )
        tags = _utils._populate_part_a_fields(resource)
        self.assertIsNotNone(tags)
        self.assertEqual(tags.get("ai.cloud.role"), "testServiceName")
        self.assertEqual(tags.get("ai.cloud.roleInstance"), "testServiceInstanceId")
        self.assertEqual(tags.get("ai.internal.nodeName"), tags.get("ai.cloud.roleInstance"))

    # Default service.name fields should be ignored when kubernetes values are present
    def test_populate_part_a_fields_aks_with_unknown_service(self):
        resource = Resource(
            {
                "service.name": "unknown_servicefoobar",
                "k8s.deployment.name": "testDeploymentName",
                "k8s.replicaset.name": "testReplicaSetName",
                "k8s.statefulset.name": "testStatefulSetName",
                "k8s.job.name": "testJobName",
                "k8s.cronjob.name": "testCronJobName",
                "k8s.daemonset.name": "testDaemonSetName",
                "k8s.pod.name": "testPodName",
            }
        )
        tags = _utils._populate_part_a_fields(resource)
        self.assertIsNotNone(tags)
        self.assertEqual(tags.get("ai.cloud.role"), "testDeploymentName")
        self.assertEqual(tags.get("ai.cloud.roleInstance"), "testPodName")
        self.assertEqual(tags.get("ai.internal.nodeName"), tags.get("ai.cloud.roleInstance"))

    @patch("azure.monitor.opentelemetry.exporter._utils.ns_to_iso_str", return_value=TEST_TIME)
    @patch("azure.monitor.opentelemetry.exporter._utils.azure_monitor_context", TEST_AZURE_MONITOR_CONTEXT)
    def test_create_telemetry_item(self, mock_ns_to_iso_str):
        result = _utils._create_telemetry_item(TEST_TIMESTAMP)
        expected_tags = dict(TEST_AZURE_MONITOR_CONTEXT)
        expected = TelemetryItem(
            name="",
            instrumentation_key="",
            tags=expected_tags,
            time=TEST_TIME,
        )
        self.assertEqual(result, expected)

    # Unknown SDK Version Prefix

    @patch("azure.monitor.opentelemetry.exporter._utils._is_attach_enabled", return_value=False)
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="")
    def test_get_sdk_version_prefix(self, mock_system, mock_isdir):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "uum_")

    @patch("azure.monitor.opentelemetry.exporter._utils._is_attach_enabled", return_value=False)
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Linux")
    def test_get_sdk_version_prefix_linux(self, mock_system, mock_isdir):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "ulm_")

    @patch("azure.monitor.opentelemetry.exporter._utils._is_attach_enabled", return_value=False)
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Windows")
    def test_get_sdk_version_prefix_windows(self, mock_system, mock_isdir):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "uwm_")

    @patch("azure.monitor.opentelemetry.exporter._utils._is_attach_enabled", return_value=True)
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="")
    def test_get_sdk_version_prefix_attach(self, mock_system, mock_isdir):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "uui_")

    @patch("azure.monitor.opentelemetry.exporter._utils._is_attach_enabled", return_value=True)
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Linux")
    def test_get_sdk_version_prefix_attach_linux(self, mock_system, mock_isdir):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "uli_")

    @patch("azure.monitor.opentelemetry.exporter._utils._is_attach_enabled", return_value=True)
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Windows")
    def test_get_sdk_version_prefix_attach_windows(self, mock_system, mock_isdir):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "uwi_")

    # App Service SDK Version Prefix

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ", {"WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME}, clear=True
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.isdir", return_value=False)
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="")
    def test_get_sdk_version_prefix_app_service(self, mock_system, mock_isdir):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "aum_")

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ", {"WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME}, clear=True
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.isdir", return_value=False)
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Linux")
    def test_get_sdk_version_prefix_app_service_linux(self, mock_system, mock_isdir):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "alm_")

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ", {"WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME}, clear=True
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.isdir", return_value=False)
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Windows")
    def test_get_sdk_version_prefix_app_service_windows(self, mock_system, mock_isdir):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "awm_")

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ", {"WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME}, clear=True
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.isdir", return_value=True)
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="")
    def test_get_sdk_version_prefix_app_service_attach(self, mock_system, mock_isdir):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "aui_")

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ", {"WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME}, clear=True
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.isdir", return_value=True)
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Linux")
    def test_get_sdk_version_prefix_app_service_linux_attach(self, mock_system, mock_isdir):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "ali_")

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ", {"WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME}, clear=True
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.isdir", return_value=True)
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Windows")
    def test_get_sdk_version_prefix_app_service_windows_attach(self, mock_system, mock_isdir):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "awi_")

    # Function SDK Version Prefix

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ",
        {
            "FUNCTIONS_WORKER_RUNTIME": TEST_WEBSITE_SITE_NAME,
            "WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME,
        },
        clear=True,
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="")
    def test_get_sdk_version_prefix_function(self, mock_system):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "fum_")

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ",
        {
            "FUNCTIONS_WORKER_RUNTIME": TEST_WEBSITE_SITE_NAME,
            "WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME,
        },
        clear=True,
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Linux")
    def test_get_sdk_version_prefix_function_linux(self, mock_system):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "flm_")

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ",
        {
            "FUNCTIONS_WORKER_RUNTIME": TEST_WEBSITE_SITE_NAME,
            "WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME,
        },
        clear=True,
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Windows")
    def test_get_sdk_version_prefix_function_windows(self, mock_system):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "fwm_")

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ",
        {
            "FUNCTIONS_WORKER_RUNTIME": TEST_WEBSITE_SITE_NAME,
            "WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME,
            "PYTHON_APPLICATIONINSIGHTS_ENABLE_TELEMETRY": "true",
        },
        clear=True,
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="")
    def test_get_sdk_version_prefix_function_attach(self, mock_system):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "fui_")

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ",
        {
            "FUNCTIONS_WORKER_RUNTIME": TEST_WEBSITE_SITE_NAME,
            "WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME,
            "PYTHON_APPLICATIONINSIGHTS_ENABLE_TELEMETRY": "true",
        },
        clear=True,
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Linux")
    def test_get_sdk_version_prefix_function_linux_attach(self, mock_system):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "fli_")

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ",
        {
            "FUNCTIONS_WORKER_RUNTIME": TEST_WEBSITE_SITE_NAME,
            "WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME,
            "PYTHON_APPLICATIONINSIGHTS_ENABLE_TELEMETRY": "true",
        },
        clear=True,
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Windows")
    def test_get_sdk_version_prefix_function_windows_attach(self, mock_system):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "fwi_")

    # AKS SDK Version Prefix

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ",
        {
            "KUBERNETES_SERVICE_HOST": TEST_KUBERNETES_SERVICE_HOST,
        },
        clear=True,
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="")
    def test_get_sdk_version_prefix_aks(self, mock_system):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "kum_")

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ",
        {
            "KUBERNETES_SERVICE_HOST": TEST_KUBERNETES_SERVICE_HOST,
        },
        clear=True,
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Linux")
    def test_get_sdk_version_prefix_aks_linux(self, mock_system):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "klm_")

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ",
        {
            "KUBERNETES_SERVICE_HOST": TEST_KUBERNETES_SERVICE_HOST,
        },
        clear=True,
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Windows")
    def test_get_sdk_version_prefix_aks_windows(self, mock_system):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "kwm_")

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ",
        {
            "AKS_ARM_NAMESPACE_ID": TEST_AKS_ARM_NAMESPACE_ID,
        },
        clear=True,
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="")
    def test_get_sdk_version_prefix_aks_attach(self, mock_system):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "kui_")

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ",
        {
            "AKS_ARM_NAMESPACE_ID": TEST_AKS_ARM_NAMESPACE_ID,
        },
        clear=True,
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Linux")
    def test_get_sdk_version_prefix_aks_linux_attach(self, mock_system):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "kli_")

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ",
        {
            "AKS_ARM_NAMESPACE_ID": TEST_AKS_ARM_NAMESPACE_ID,
        },
        clear=True,
    )
    @patch("azure.monitor.opentelemetry.exporter._utils.platform.system", return_value="Windows")
    def test_get_sdk_version_prefix_aks_windows_attach(self, mock_system):
        result = _utils._get_sdk_version_prefix()
        self.assertEqual(result, "kwi_")

    # Attach

    @patch(
        "azure.monitor.opentelemetry.exporter._utils.isdir",
        return_value=True,
    )
    @patch.dict("azure.monitor.opentelemetry.exporter._utils.environ", {"WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME})
    def test_attach_enabled(self, mock_isdir):
        self.assertEqual(_utils._is_attach_enabled(), True)

    @patch(
        "azure.monitor.opentelemetry.exporter._utils.isdir",
        return_value=False,
    )
    @patch.dict("azure.monitor.opentelemetry.exporter._utils.environ", {"WEBSITE_SITE_NAME": TEST_WEBSITE_SITE_NAME})
    def test_attach_app_service_disabled(self, mock_isdir):
        self.assertEqual(_utils._is_attach_enabled(), False)

    @patch(
        "azure.monitor.opentelemetry.exporter._utils.isdir",
        return_value=True,
    )
    @patch.dict("azure.monitor.opentelemetry.exporter._utils.environ", {}, clear=True)
    def test_attach_off_app_service_with_agent(self, mock_isdir):
        # This is not an expected scenario and just tests the default
        self.assertFalse(_utils._is_attach_enabled())

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ",
        {
            "KUBERNETES_SERVICE_HOST": TEST_KUBERNETES_SERVICE_HOST,
            "AKS_ARM_NAMESPACE_ID": TEST_AKS_ARM_NAMESPACE_ID,
        },
        clear=True,
    )
    def test_attach_aks(self):
        # This is not an expected scenario and just tests the default
        self.assertTrue(_utils._is_attach_enabled())

    @patch.dict(
        "azure.monitor.opentelemetry.exporter._utils.environ",
        {
            "KUBERNETES_SERVICE_HOST": TEST_KUBERNETES_SERVICE_HOST,
        },
        clear=True,
    )
    def test_aks_no_attach(self):
        # This is not an expected scenario and just tests the default
        self.assertFalse(_utils._is_attach_enabled())

    # Synthetic

    def test_is_synthetic_source_bot(self):
        properties = {"user_agent.synthetic.type": "bot"}
        self.assertTrue(_utils._is_synthetic_source(properties))

    def test_is_synthetic_source_test(self):
        properties = {"user_agent.synthetic.type": "test"}
        self.assertTrue(_utils._is_synthetic_source(properties))

    def test_is_synthetic_source_none(self):
        properties = {}
        self.assertFalse(_utils._is_synthetic_source(properties))

    def test_is_synthetic_source_other(self):
        properties = {"user_agent.synthetic.type": "user"}
        self.assertFalse(_utils._is_synthetic_source(properties))

    def test_is_synthetic_load_always_on_legacy(self):
        properties = {"http.user_agent": "Mozilla/5.0 AlwaysOn"}
        self.assertTrue(_utils._is_synthetic_load(properties))

    def test_is_synthetic_load_always_on_new_convention(self):
        properties = {"user_agent.original": "Azure-Load-Testing/1.0 AlwaysOn"}
        self.assertTrue(_utils._is_synthetic_load(properties))

    def test_is_synthetic_load_always_on_case_sensitive(self):
        properties = {"http.user_agent": "Mozilla/5.0 alwayson"}
        self.assertFalse(_utils._is_synthetic_load(properties))

    def test_is_synthetic_load_no_user_agent(self):
        properties = {}
        self.assertFalse(_utils._is_synthetic_load(properties))

    def test_is_synthetic_load_normal_user_agent(self):
        properties = {"http.user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        self.assertFalse(_utils._is_synthetic_load(properties))

    def test_is_any_synthetic_source_bot(self):
        properties = {"user_agent.synthetic.type": "bot"}
        self.assertTrue(_utils._is_any_synthetic_source(properties))

    def test_is_any_synthetic_source_always_on(self):
        properties = {"http.user_agent": "Azure-Load-Testing/1.0 AlwaysOn"}
        self.assertTrue(_utils._is_any_synthetic_source(properties))

    def test_is_any_synthetic_source_both(self):
        properties = {"user_agent.synthetic.type": "bot", "http.user_agent": "Azure-Load-Testing/1.0 AlwaysOn"}
        self.assertTrue(_utils._is_any_synthetic_source(properties))

    def test_is_any_synthetic_source_none(self):
        properties = {"http.user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        self.assertFalse(_utils._is_any_synthetic_source(properties))
