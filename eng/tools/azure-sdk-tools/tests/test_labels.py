# Used to test the individual functions in the gh_tools module of azure-sdk-tools

from typing import List

import pytest

from gh_tools.vnext_issue_creator import get_labels


@pytest.mark.parametrize(
    "package_name, service, expected_labels",
    [
        ("corehttp", "core", ["Core.Http"]),
        ("azure-core", "core", ["Azure.Core"]),
        ("azure-confidentialledger", "confidentialledger", ["Confidential Ledger"]),
        ("azure-monitor-ingestion", "monitor", ["Monitor"]),
        ("azure-ai-ml", "ml", ["Machine Learning"]),
        ("azure-ai-translation-document", "translation", ["Cognitive - Translator"]),
        ("azure-storage-blob", "storage", ["Storage"]),
        ("azure-ai-agents", "ai", ["AI Agents"]),
        ("azure-ai-projects", "ai", ["AI Projects"]),
        ("azure-ai-inference", "ai", ["AI Model Inference"]),
        ("azure-mgmt-appconfiguration", "appconfiguration", ["Mgmt", "App Configuration"]),
        ("azure-mgmt-webpubsub", "webpubsub", ["Mgmt", "WebPubSub"]),
        ("azure-unknown", "unknown", []),
        ("azure-mgmt-unknown", "unknown", ["Mgmt"]),
    ],
)
def test_get_labels_for_gh_vnext_issues(package_name: str, service: str, expected_labels: List[str]):
    labels = get_labels(package_name, service)

    assert labels == expected_labels
