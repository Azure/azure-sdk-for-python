# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import Any, Dict, List, Optional

from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    DiagnoseRequestProperties as RestDiagnoseRequestProperties,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import DiagnoseResponseResult as RestDiagnoseResponseResult
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    DiagnoseResponseResultValue as RestDiagnoseResponseResultValue,
)
from azure.ai.ml._restclient.v2023_04_01_preview.models import DiagnoseResult as RestDiagnoseResult
from azure.ai.ml._restclient.v2023_04_01_preview.models import (
    DiagnoseWorkspaceParameters as RestDiagnoseWorkspaceParameters,
)


class DiagnoseRequestProperties:
    """DiagnoseRequestProperties."""

    def __init__(
        self,
        *,
        udr: Optional[Dict[str, Any]] = None,
        nsg: Optional[Dict[str, Any]] = None,
        resource_lock: Optional[Dict[str, Any]] = None,
        dns_resolution: Optional[Dict[str, Any]] = None,
        storage_account: Optional[Dict[str, Any]] = None,
        key_vault: Optional[Dict[str, Any]] = None,
        container_registry: Optional[Dict[str, Any]] = None,
        application_insights: Optional[Dict[str, Any]] = None,
        others: Optional[Dict[str, Any]] = None,
    ):
        self.udr = udr
        self.nsg = nsg
        self.resource_lock = resource_lock
        self.dns_resolution = dns_resolution
        self.storage_account = storage_account
        self.key_vault = key_vault
        self.container_registry = container_registry
        self.application_insights = application_insights
        self.others = others

    @classmethod
    def _from_rest_object(cls, rest_obj: RestDiagnoseRequestProperties) -> "DiagnoseRequestProperties":
        return cls(
            udr=rest_obj.udr,
            nsg=rest_obj.nsg,
            resource_lock=rest_obj.resource_lock,
            dns_resolution=rest_obj.dns_resolution,
            storage_account=rest_obj.storage_account,
            key_vault=rest_obj.key_vault,
            container_registry=rest_obj.container_registry,
            application_insights=rest_obj.application_insights,
            others=rest_obj.others,
        )

    def _to_rest_object(self) -> RestDiagnoseRequestProperties:
        return RestDiagnoseRequestProperties(
            udr=self.udr,
            nsg=self.nsg,
            resource_lock=self.resource_lock,
            dns_resolution=self.dns_resolution,
            storage_account=self.storage_account,
            key_vault=self.key_vault,
            container_registry=self.container_registry,
            application_insights=self.application_insights,
            others=self.others,
        )


class DiagnoseResponseResult:
    """DiagnoseResponseResult."""

    def __init__(
        self,
        *,
        value: Optional["DiagnoseResponseResultValue"] = None,
    ):
        self.value = value

    @classmethod
    def _from_rest_object(cls, rest_obj: RestDiagnoseResponseResult) -> "DiagnoseResponseResult":
        val = None
        if rest_obj and rest_obj.value and isinstance(rest_obj.value, RestDiagnoseResponseResultValue):
            # pylint: disable=protected-access
            val = DiagnoseResponseResultValue._from_rest_object(rest_obj.value)
        return cls(value=val)

    def _to_rest_object(self) -> RestDiagnoseResponseResult:
        return RestDiagnoseResponseResult(value=self.value)


class DiagnoseResponseResultValue:
    """DiagnoseResponseResultValue."""

    def __init__(
        self,
        *,
        user_defined_route_results: Optional[List["DiagnoseResult"]] = None,
        network_security_rule_results: Optional[List["DiagnoseResult"]] = None,
        resource_lock_results: Optional[List["DiagnoseResult"]] = None,
        dns_resolution_results: Optional[List["DiagnoseResult"]] = None,
        storage_account_results: Optional[List["DiagnoseResult"]] = None,
        key_vault_results: Optional[List["DiagnoseResult"]] = None,
        container_registry_results: Optional[List["DiagnoseResult"]] = None,
        application_insights_results: Optional[List["DiagnoseResult"]] = None,
        other_results: Optional[List["DiagnoseResult"]] = None,
    ):
        self.user_defined_route_results = user_defined_route_results
        self.network_security_rule_results = network_security_rule_results
        self.resource_lock_results = resource_lock_results
        self.dns_resolution_results = dns_resolution_results
        self.storage_account_results = storage_account_results
        self.key_vault_results = key_vault_results
        self.container_registry_results = container_registry_results
        self.application_insights_results = application_insights_results
        self.other_results = other_results

    @classmethod
    def _from_rest_object(cls, rest_obj: RestDiagnoseResponseResultValue) -> "DiagnoseResponseResultValue":
        return cls(
            user_defined_route_results=rest_obj.user_defined_route_results,
            network_security_rule_results=rest_obj.network_security_rule_results,
            resource_lock_results=rest_obj.resource_lock_results,
            dns_resolution_results=rest_obj.dns_resolution_results,
            storage_account_results=rest_obj.storage_account_results,
            key_vault_results=rest_obj.key_vault_results,
            container_registry_results=rest_obj.container_registry_results,
            application_insights_results=rest_obj.application_insights_results,
            other_results=rest_obj.other_results,
        )

    def _to_rest_object(self) -> RestDiagnoseResponseResultValue:
        return RestDiagnoseResponseResultValue(
            user_defined_route_results=self.user_defined_route_results,
            network_security_rule_results=self.network_security_rule_results,
            resource_lock_results=self.resource_lock_results,
            dns_resolution_results=self.dns_resolution_results,
            storage_account_results=self.storage_account_results,
            key_vault_results=self.key_vault_results,
            container_registry_results=self.container_registry_results,
            application_insights_results=self.application_insights_results,
            other_results=self.other_results,
        )


class DiagnoseResult:
    """Result of Diagnose."""

    def __init__(
        self,
        *,
        code: Optional[str] = None,
        level: Optional[str] = None,
        message: Optional[str] = None,
    ):
        self.code = code
        self.level = level
        self.message = message

    @classmethod
    def _from_rest_object(cls, rest_obj: RestDiagnoseResult) -> "DiagnoseResult":
        return cls(
            code=rest_obj.code,
            level=rest_obj.level,
            message=rest_obj.message,
        )

    def _to_rest_object(self) -> RestDiagnoseResult:
        return RestDiagnoseResult(
            code=self.code,
            level=self.level,
            message=self.message,
        )


class DiagnoseWorkspaceParameters:
    """Parameters to diagnose a workspace."""

    def __init__(
        self,
        *,
        value: Optional["DiagnoseRequestProperties"] = None,
    ):
        self.value = value

    @classmethod
    def _from_rest_object(cls, rest_obj: RestDiagnoseWorkspaceParameters) -> "DiagnoseWorkspaceParameters":
        val = None
        if rest_obj.value and isinstance(rest_obj.value, DiagnoseRequestProperties):
            # pylint: disable=protected-access
            val = rest_obj.value._from_rest_object()
        return cls(value=val)

    def _to_rest_object(self) -> RestDiagnoseWorkspaceParameters:
        val = None
        if self.value and isinstance(self.value, DiagnoseRequestProperties):
            # pylint: disable=protected-access
            val = self.value._to_rest_object()
        return RestDiagnoseWorkspaceParameters(value=val)
