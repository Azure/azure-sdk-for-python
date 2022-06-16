# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import logging
from copy import deepcopy

from azure.ai.ml.entities import OnlineEndpoint
from azure.ai.ml._ml_exceptions import ValidationException, ErrorTarget, ErrorCategory


module_logger = logging.getLogger(__name__)


class EndpointValidator:
    def __init__(self):
        self._total_updates = 0
        self._base_error_message = (
            "Only one update out of the following is allowed at a time:\n"
            "1. One endpoint traffic change \n"
            "2. One deployment instance_count change\n"
            "3. One deployment setup change (code, model, environment).\n\n"
            "The given update operation is attempting to:\n"
        )

    def validate_updates(self, old_endpoint: OnlineEndpoint, new_endpoint: OnlineEndpoint) -> None:
        self._validate_endpoint_settings_update(old_endpoint=old_endpoint, new_endpoint=new_endpoint)
        self._validate_scale_settings_update(old_endpoint=old_endpoint, new_endpoint=new_endpoint)
        self._validate_deployments_update(old_endpoint=old_endpoint, new_endpoint=new_endpoint)
        if self._total_updates > 1:
            module_logger.warning(self._base_error_message)
            raise ValidationException(
                messsage=self._base_error_message,
                no_personal_data_message=self._base_error_message,
                error_category=ErrorCategory.USER_ERROR,
                target=ErrorTarget.ENDPOINT,
            )

    def _update_error_message(self, error_message: str) -> None:
        if error_message:
            self._base_error_message = self._base_error_message + error_message

    def _validate_endpoint_settings_update(self, old_endpoint: OnlineEndpoint, new_endpoint: OnlineEndpoint) -> None:
        test_new_endpoint = deepcopy(new_endpoint)
        test_old_endpoint = deepcopy(old_endpoint)

        # only check shared deployments for changes - additions or deletion will be checked by
        # _validate_add_and_delete_update()
        old_set = {d.name for d in test_old_endpoint.deployments}
        new_set = {d.name for d in test_new_endpoint.deployments}
        shared_deployments = old_set.intersection(new_set)
        shared_traffic = set(old_endpoint.traffic).intersection(new_endpoint.traffic)

        test_new_endpoint.deployments = [d for d in new_endpoint.deployments if d.name in shared_deployments]
        test_old_endpoint.deployments = [d for d in old_endpoint.deployments if d.name in shared_deployments]
        test_new_endpoint.traffic = {d: new_endpoint.traffic[d] for d in shared_traffic}
        test_old_endpoint.traffic = {d: old_endpoint.traffic[d] for d in shared_traffic}

        if test_old_endpoint != test_new_endpoint:
            msg = "Update endpoint settings including traffic\n"
            self._total_updates += 1
            self._update_error_message(error_message=msg)

    def _validate_scale_settings_update(self, old_endpoint: OnlineEndpoint, new_endpoint: OnlineEndpoint) -> None:
        msg = ""
        for new_deployment in new_endpoint.deployments:
            deployment_name = new_deployment.name
            old_deployment = next((d for d in old_endpoint.deployments if d.name == deployment_name), None)
            if old_deployment:
                if old_deployment.scale_settings != new_deployment.scale_settings:
                    self._total_updates += 1
                    info_message = f"Change {deployment_name}'s' scale_settings\n"
                    msg += info_message
        self._update_error_message(msg)

    def _validate_deployments_update(self, old_endpoint: OnlineEndpoint, new_endpoint: OnlineEndpoint) -> None:
        msg = ""
        for new_deployment in new_endpoint.deployments:
            deployment_name = new_deployment.name
            old_deployment = next((d for d in old_endpoint.deployments if d.name == deployment_name), None)
            if old_deployment:
                # TODO: There is a bug on the service side. The wrong scoring_script is returned. Only
                # when that bug is fixed, we should enabled the scoring_script
                model_is_same = old_deployment.model == new_deployment.model
                code_is_same = (
                    old_deployment.code_configuration is None
                    and new_deployment.code_configuration is None
                    or old_deployment.code_configuration.code == new_deployment.code_configuration.code
                )
                no_changes = code_is_same and model_is_same
                if not no_changes:
                    self._total_updates += 1
                    info_message = f"Change {deployment_name} settings other than scale_settings\n"
                    msg += info_message
        self._update_error_message(error_message=msg)
