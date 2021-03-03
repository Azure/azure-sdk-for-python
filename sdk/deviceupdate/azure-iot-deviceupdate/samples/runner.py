from azure.core.exceptions import HttpResponseError
from azure.iot.deviceupdate import DeviceUpdateClient
from azure.iot.deviceupdate.models import *
from azure.identity import ClientSecretCredential
from datetime import datetime, timezone
import json
import time
from samples.contentfactory import ContentFactory
from samples.consts import MANUFACTURER, MODEL, BLOB_CONTAINER, DEFAULT_RETRY_AFTER


class SampleRunner:
    def __init__(self, tenant_id, client_id, client_secret, account_endpoint, instance_id, storage_name, storage_key,
                 device_id, device_tag, **kwargs):
        self._tenant_id = tenant_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._storage_name = storage_name
        self._storage_key = storage_key
        self._device_id = device_id
        self._device_tag = device_tag
        self._account_endpoint = account_endpoint
        self._instance_id = instance_id
        self._delete = kwargs.pop('delete', False)

        credentials = ClientSecretCredential(
            tenant_id=tenant_id,
            client_id=client_id,
            client_secret=client_secret
        )
        self._client = DeviceUpdateClient(credentials, account_endpoint, instance_id)

    def run(self):
        version = datetime.now().strftime("%Y.%#m%d.%#H%M.%#S")

        # Create new update and import it into ADU
        job_id = self._import_update_step(version)

        # Let's retrieve the existing (newly imported) update
        self._retrieve_update_step(MANUFACTURER, MODEL, version, 200)

        # Create deployment/device group
        group_id = self._create_deployment_group_step()

        # Check that device group contains devices that can be updated with our new update
        self._check_group_devices_are_up_to_date_step(group_id, MANUFACTURER, MODEL, version, False)

        # Create deployment for our device group to deploy our new update
        deployment_id = self._deploy_update_step(MANUFACTURER, MODEL, version, group_id)

        # Check device and wait until the new update is installed there
        self._check_device_updates_step(MANUFACTURER, MODEL, version)

        # Check that device group contains *NO* devices that can be updated with our new update
        self._check_group_devices_are_up_to_date_step(group_id, MANUFACTURER, MODEL, version, True)

        if self._delete:
            # Delete the update
            self._delete_update_step(MANUFACTURER, MODEL, version);

            # Let's retrieve the deleted update (newly imported) update and expect 404 (not found response)
            self._retrieve_update_step(MANUFACTURER, MODEL, version, 404)

        # Dump test data to be used for unit-testing
        self._output_test_data(version, job_id, deployment_id)

    def _import_update_step(self, version):
        content_factory = ContentFactory(self._storage_name, self._storage_key, BLOB_CONTAINER)
        update = content_factory.create_import_update(MANUFACTURER, MODEL, version)

        print("Importing updates...")
        _, _, headers = self._client.updates.import_update(update, cls=callback)
        operation_id = self._get_operation_id(headers["Location"])
        print(f"Import operation id: {operation_id}")

        print("(this may take a minute or two)")
        repeat = True
        while repeat:
            _, operation, headers = self._client.updates.get_operation(operation_id, cls=callback)
            if operation.status == "Succeeded":
                print(operation.status)
                repeat = False
            elif operation.status == "Failed":
                error = operation.errors[0]
                raise ImportError("Import failed with response: \n" +
                                  json.dumps(error.__dict__, default=as_dict, sort_keys=True, indent=2))
            else:
                print(".", end="", flush=True)
                time.sleep(self._get_retry_after(headers))
        print()
        return operation_id

    def _retrieve_update_step(self, provider, name, version, expected_status):
        print("Retrieving update...")
        value = None
        try:
            response, value, _ = self._client.updates.get_update(provider, name, version, cls=callback)
            status_code = response.http_response.status_code
        except HttpResponseError as e:
            status_code = e.status_code
        if status_code == expected_status:
            print(f"Received an expected status code: {expected_status}")
            if value is not None:
                print(json.dumps(value.__dict__, default=as_dict, sort_keys=True, check_circular=False, indent=2))
            else:
                print()
        else:
            raise Exception(f"Service returned status code: {response.http_response.status_code}")
        print()

    def _create_deployment_group_step(self):
        group_id = self._device_tag
        create_new_group = False

        print("Querying deployment group...")
        try:
            _ = self._client.devices.get_group(group_id)
            print(f"Deployment group {group_id} already exists.")
        except HttpResponseError as e:
            if e.status_code == 404:
                create_new_group = True

        if create_new_group:
            print("Creating deployment group...")
            group = self._client.devices.create_or_update_group(
                group_id,
                Group(
                    group_id=group_id,
                    group_type=GroupType.IO_T_HUB_TAG,
                    tags=[group_id],
                    created_date_time=datetime.utcnow().isoformat()
                ))
            if group is not None:
                print(f"Group {group_id} created.")
                print()

                print("Waiting for the group to be populated with devices...")
                print("(this may take about five minutes to complete)")
                repeat = True
                while repeat:
                    group = self._client.devices.get_group(group_id)
                    if group.device_count > 0:
                        print(f"Deployment group {group_id} now has {group.device_count} devices.")
                        repeat = False
                    else:
                        print(".", end="", flush=True)
                        time.sleep(DEFAULT_RETRY_AFTER)
        print()
        return group_id

    def _check_group_devices_are_up_to_date_step(self, group_id, provider, name, version, is_compliant):
        print(f"Check group {group_id} device compliance with update {provider}/{name}/{version}...")
        update_found = False
        counter = 0

        while not update_found and counter <= 6:
            response = self._client.devices.get_group_best_updates(group_id)
            group_devices = list(response)
            for updatableDevices in group_devices:
                update = updatableDevices.update_id
                if update.provider == provider and update.name == name and update.version == version:
                    update_found = True
                    if is_compliant:
                        if updatableDevices.device_count == 0:
                            print("All devices within the group have this update installed.")
                        else:
                            print(f"There are still {updatableDevices.device_count} devices that can be updated to " +
                                  f"update {provider}/{name}/{version}.")
                    else:
                        print(f"There are {updatableDevices.device_count} devices that can be updated to update " +
                              f"{provider}/{name}/{version}.")
            counter = counter + 1
            if not update_found:
                print(".", end="", flush=True)
                time.sleep(DEFAULT_RETRY_AFTER)

        if not update_found:
            print("(Update is still not available for any group device.)")
        print()

    def _deploy_update_step(self, provider, name, version, group_id):
        print("Deploying the update to a device...")
        deployment_id = f"{self._device_id}.{version.replace('.', '-')}"
        _ = self._client.deployments.create_or_update_deployment(
            deployment_id=deployment_id,
            deployment=Deployment(
                deployment_id=deployment_id,
                deployment_type=DeploymentType.complete,
                start_date_time=datetime.now(timezone.utc),
                device_group_type=DeviceGroupType.DEVICE_GROUP_DEFINITIONS,
                device_group_definition=[group_id],
                update_id=UpdateId(provider=provider, name=name, version=version)))
        print(f"Deployment '{deployment_id}' created.")
        time.sleep(DEFAULT_RETRY_AFTER)

        print("Checking the deployment status...")
        status = self._client.deployments.get_deployment_status(deployment_id)
        print(f"  {status.deployment_state}")
        print()
        return deployment_id

    def _check_device_updates_step(self, provider, name, version):
        print(f"Checking device {self._device_id} status...")
        print("Waiting for the update to be installed...")
        repeat = True
        while repeat:
            device = self._client.devices.get_device(self._device_id)
            installed_update = device.installed_update_id
            if installed_update.provider == provider and installed_update.name == name and installed_update.version == version:
                repeat = False
            else:
                print(".", end="", flush=True)
                time.sleep(DEFAULT_RETRY_AFTER)

        print("\n")

    def _delete_update_step(self, provider, name, version):
        print("Deleting the update...")
        _, _, headers = self._client.updates.delete_update(provider, name, version, cls=callback)
        operation_id = self._get_operation_id(headers["Operation-Location"])
        print(f"Delete operation id: {operation_id}")

        print("Waiting for delete to finish...")
        print("(this may take a minute or two)")
        repeat = True
        while repeat:
            _, operation, headers = self._client.updates.get_operation(operation_id, cls=callback)
            if operation.status == "Succeeded":
                print(operation.status)
                repeat = False
            elif operation.status == "Failed":
                error = operation.errors[0]
                raise ImportError("Delete failed with response: \n" +
                                  json.dumps(error.__dict__, default=as_dict, sort_keys=True, indent=2))
            else:
                print(".", end="", flush=True)
                time.sleep(self._get_retry_after(headers))
        print()

    def _get_operation_id(self, operation_location):
        return operation_location.split("/")[-1]

    def _get_retry_after(self, headers):
        if headers is not None and headers["Retry-After"] is not None:
            return int(headers["Retry-After"])
        else:
            return DEFAULT_RETRY_AFTER

    def _output_test_data(self, version, job_id, deployment_id):
        print("Test data to use when running SDK unit tests:")
        print(f'DEVICEUPDATE_TENANT_ID="{self._tenant_id}"')
        print(f'DEVICEUPDATE_CLIENT_ID="{self._client_id}"')
        print(f'DEVICEUPDATE_CLIENT_SECRET="{self._client_secret}"')
        print(f'DEVICEUPDATE_ACCOUNT_ENDPOINT="{self._account_endpoint}"')
        print(f'DEVICEUPDATE_INSTANCE_ID="{self._instance_id}"')
        print(f'DEVICEUPDATE_VERSION="{version}"')
        print(f'DEVICEUPDATE_OPERATION_ID="{job_id}"')
        print(f'DEVICEUPDATE_DEVICE_ID="{self._device_id}"')
        print(f'DEVICEUPDATE_DEPLOYMENT_ID="{deployment_id}"')
        print(f'DEVICEUPDATE_PROVIDER="{MANUFACTURER}"')
        print(f'DEVICEUPDATE_MODEL="{MODEL}"')
        print(f'DEVICEUPDATE_DEVICE_CLASS_ID="b83e3c87fbf98063c20c3269f1c9e58d255906dd"')
        print()
        print("Set these environment variables in your '.env' file before opening and running SDK unit tests.")
        pass


def callback(response, value, headers):
    return response, value, headers


def as_dict(o):
    try:
        return o.__dict__
    except:
        return "???"
