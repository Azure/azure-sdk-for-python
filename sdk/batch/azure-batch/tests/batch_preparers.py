from collections import namedtuple
import io
import os
import time
import zipfile
from urllib.parse import parse_qs, urlsplit

import requests

from devtools_testutils import (
    AzureMgmtPreparer,
    AzureTestError,
    ResourceGroupPreparer,
    StorageAccountPreparer,
    FakeResource,
    add_general_regex_sanitizer,
    add_general_string_sanitizer,
    add_body_key_sanitizer,
)
from devtools_testutils.fake_credentials import BATCH_TEST_PASSWORD
from devtools_testutils.resource_testcase import RESOURCE_GROUP_PARAM

import azure.core.exceptions
import azure.mgmt.batch
from azure.mgmt.batch import models
import azure.batch
import azure.batch.models
from azure.core.credentials import AzureNamedKeyCredential

AZURE_ARM_ENDPOINT = "https://management.azure.com"
BATCH_ACCOUNT_PARAM = "batch_account"
STORAGE_ACCOUNT_PARAM = "storage_account"
FakeAccount = namedtuple("FakeResource", ["name", "account_endpoint"])
PLAYBACK_LOG_CONTAINER_URL = "https://computecontainer.blob.core.windows.net/"


class BatchStorageAccountPreparer(StorageAccountPreparer):
    def _create_account(self, resource_group_name, account_name):
        return self.client.storage_accounts.begin_create(
            resource_group_name,
            account_name,
            {
                "sku": {"name": self.sku},
                "location": self.location,
                "kind": self.kind,
                "enable_https_traffic_only": True,
                "allow_blob_public_access": False,
            },
        )


def load_application_package():
    package_path = os.environ.get("BATCH_TEST_APP_ZIP")
    if package_path:
        with open(package_path, "rb") as package_file:
            content = package_file.read()
        if not zipfile.is_zipfile(io.BytesIO(content)):
            raise AzureTestError("BATCH_TEST_APP_ZIP must reference a valid ZIP application package.")
        return content
    with io.BytesIO() as package_file:
        with zipfile.ZipFile(package_file, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            archive.writestr("readme.txt", "Azure Batch SDK test application package.")
        return package_file.getvalue()


def get_log_container_url(live):
    if not live:
        return PLAYBACK_LOG_CONTAINER_URL
    url = os.environ.get("BATCH_LOG_CONTAINER_SAS_URL")
    if not url:
        raise AzureTestError("Set BATCH_LOG_CONTAINER_SAS_URL to a writable container SAS URL for live log uploads.")
    try:
        parsed = urlsplit(url)
        query = parse_qs(parsed.query)
        valid = (
            parsed.scheme == "https"
            and bool(parsed.hostname)
            and bool(parsed.path.strip("/"))
            and "sig" in query
            and "w" in query.get("sp", [""])[0]
            and query.get("sr") == ["c"]
        )
    except ValueError:
        valid = False
    if not valid:
        raise AzureTestError("BATCH_LOG_CONTAINER_SAS_URL must be an HTTPS container SAS URL with write permission.")
    add_general_string_sanitizer(target=url, value=PLAYBACK_LOG_CONTAINER_URL)
    add_body_key_sanitizer(json_path="$..containerUrl", value=PLAYBACK_LOG_CONTAINER_URL)
    return url


class AccountPreparer(AzureMgmtPreparer):
    creds_parameter = "credential"
    parameter_name_for_location = "location"

    def __init__(
        self,
        name_prefix="batch",
        location="westus",
        parameter_name=BATCH_ACCOUNT_PARAM,
        resource_group_parameter_name=RESOURCE_GROUP_PARAM,
        disable_recording=True,
        playback_fake_resource=None,
        batch_environment=None,  # Set to "pilotprod1" or "pilotprod2" if testing in PPE
        client_kwargs=None,
        existing_account_name=None,
        existing_resource_group=None,
    ):
        super(AccountPreparer, self).__init__(
            name_prefix,
            24,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
        )
        self.location = location
        self.resource_group_parameter_name = resource_group_parameter_name
        self.parameter_name = parameter_name
        self.resource_moniker = name_prefix
        self.batch_environment = batch_environment
        self.existing_account_name = existing_account_name
        self.existing_resource_group = existing_resource_group

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs[self.resource_group_parameter_name]
        except KeyError as exc:
            template = (
                "To create a batch account a resource group is required. Please add "
                "decorator @{} in front of this storage account preparer."
            )
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__)) from exc

    def _get_storage_account(self, **kwargs):
        return kwargs.get(STORAGE_ACCOUNT_PARAM)

    def _add_app_package(self, group_name, batch_name):
        content = load_application_package()
        self.client.application.create(group_name, batch_name, "application_id")
        package_ref = self.client.application_package.create(group_name, batch_name, "application_id", "v1.0")
        try:
            headers = {"x-ms-blob-type": "BlockBlob"}
            upload = requests.put(package_ref.storage_url, headers=headers, data=content, timeout=60)
            if not upload:
                raise ValueError("Upload failed with HTTP status {}".format(upload.status_code))
        except (requests.RequestException, ValueError) as err:
            raise AzureTestError(
                "Failed to upload the test application package ({})".format(type(err).__name__)
            ) from None
        self.client.application_package.activate(
            group_name, batch_name, "application_id", "v1.0", {"format": "zip"}
        )

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self.create_mgmt_client(azure.mgmt.batch.BatchManagementClient, base_url=AZURE_ARM_ENDPOINT)

            if self.existing_account_name:
                self.resource = self.client.batch_account.get(self.existing_resource_group, self.existing_account_name)
                # keys = self.client.batch_account.get_keys(
                #    self.existing_resource_group, self.existing_account_name
                # )
                # credentials = AzureNamedKeyCredential(keys.account_name, keys.primary)

                return {self.parameter_name: self.resource}

            group = self._get_resource_group(**kwargs)
            batch_account = models.BatchAccountCreateParameters(
                location=self.location,
            )
            storage = self._get_storage_account(**kwargs)
            if storage:
                storage_resource = (
                    "/subscriptions/{}/resourceGroups/{}/providers/Microsoft.Storage/storageAccounts/{}".format(
                        os.environ.get("AZURE_SUBSCRIPTION_ID"), group.name, storage.name
                    )
                )
                batch_account.auto_storage = models.AutoStorageBaseProperties(storage_account_id=storage_resource)
            account_setup = self.client.batch_account.begin_create(group.name, name, batch_account)
            self.resource = account_setup.result()
            keys = self.client.batch_account.get_keys(group.name, name)
            credentials = AzureNamedKeyCredential(keys.account_name, keys.primary)
            if storage:
                self._add_app_package(group.name, name)
            add_general_regex_sanitizer(regex=name, value=self.moniker)
        else:
            # If using pilotprod, need to prefix the region with the environment.
            # IE: myaccount.pilotprod1.eastus.batch.azure.com
            env_prefix = "" if self.batch_environment is None else ".{}".format(self.batch_environment)
            self.resource = FakeAccount(
                name=name, account_endpoint="https://{}{}.{}.batch.azure.com".format(name, env_prefix, self.location)
            )
            credentials = AzureNamedKeyCredential(name, "ZmFrZV9hY29jdW50X2tleQ==")
        return {self.parameter_name: self.resource, self.creds_parameter: credentials}

    def remove_resource(self, name, **kwargs):
        if self.is_live and not self.existing_account_name:
            group = self._get_resource_group(**kwargs)
            deleting = self.client.batch_account.begin_delete(group.name, name)
            try:
                deleting.wait()
            except:
                pass


class PoolPreparer(AzureMgmtPreparer):
    def __init__(
        self,
        name_prefix="",
        size=0,
        operating_system="Linux",
        config="iaas",
        parameter_name="batch_pool",
        location=None,
        resource_group_parameter_name=RESOURCE_GROUP_PARAM,
        batch_account_parameter_name=BATCH_ACCOUNT_PARAM,
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        pool_name=None,
    ):
        super(PoolPreparer, self).__init__(
            name_prefix,
            24,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
        )
        self.size = size
        self.os = operating_system
        self.location = location
        self.config = config
        self.resource_group_parameter_name = resource_group_parameter_name
        self.batch_account_parameter_name = batch_account_parameter_name
        self.parameter_name = parameter_name
        self.pool_name = pool_name

    def _get_resource_group(self, **kwargs):
        try:
            return kwargs[self.resource_group_parameter_name]
        except KeyError as exc:
            template = (
                "To create a batch account a resource group is required. Please add "
                "decorator @{} in front of this storage account preparer."
            )
            raise AzureTestError(template.format(ResourceGroupPreparer.__name__)) from exc

    def _get_batch_account(self, **kwargs):
        try:
            return kwargs[self.batch_account_parameter_name]
        except KeyError as exc:
            template = (
                "To create a batch poool, a batch account is required. Please add "
                "decorator @AccountPreparer in front of this pool preparer."
            )
            raise AzureTestError(template) from exc

    def create_resource(self, name, **kwargs):

        if self.pool_name:
            name = self.pool_name

        if self.is_live:

            self.client = self.create_mgmt_client(azure.mgmt.batch.BatchManagementClient, base_url=AZURE_ARM_ENDPOINT)
            group = self._get_resource_group(**kwargs)
            batch_account = self._get_batch_account(**kwargs)
            user = models.UserAccount(
                name="task-user", password=BATCH_TEST_PASSWORD, elevation_level=models.ElevationLevel.admin
            )
            vm_size = "standard_d2s_v3" if self.os == "Windows" else "standard_d2_v2"

            if self.os == "Windows":
                deployment = models.DeploymentConfiguration(
                    virtual_machine_configuration=models.VirtualMachineConfiguration(
                        image_reference=models.ImageReference(
                            publisher="MicrosoftWindowsServer", offer="windowsserver2022", sku="2022-datacenter-g2"
                        ),
                        node_agent_sku_id="batch.node.windows amd64",
                    )
                )
            else:
                deployment = models.DeploymentConfiguration(
                    virtual_machine_configuration=models.VirtualMachineConfiguration(
                        image_reference=models.ImageReference(
                            publisher="Canonical", offer="0001-com-ubuntu-server-jammy", sku="22_04-lts"
                        ),
                        node_agent_sku_id="batch.node.ubuntu 22.04",
                    )
                )
            inboundpool_config = models.InboundNatPool(
                name="ruleName",
                protocol=models.InboundEndpointProtocol.Tcp,
                backend_port=3389,
                frontend_port_range_start=15000,
                frontend_port_range_end=15100,
            )
            parameters = models.Pool(
                display_name="test_pool",
                vm_size=vm_size,
                user_accounts=[user],
                deployment_configuration=deployment,
                scale_settings=models.ScaleSettings(
                    fixed_scale=models.FixedScaleSettings(target_dedicated_nodes=self.size)
                ),
                network_configuration=models.NetworkConfiguration(
                    endpoint_configuration=models.PoolEndpointConfiguration(inbound_nat_pools=[inboundpool_config])
                ),
            )

            self.resource = self.client.pool.create(group.name, batch_account.name, name, parameters)
            while (
                self.resource.allocation_state != models.AllocationState.steady
                and self.resource.current_dedicated_nodes < self.size
            ):
                time.sleep(10)
                self.resource = self.client.pool.get(group.name, batch_account.name, name)
        else:
            self.resource = FakeResource(name=name, id=name)
        return {
            self.parameter_name: self.resource,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            group = self._get_resource_group(**kwargs)
            account = self._get_batch_account(**kwargs)
            deleting = self.client.pool.begin_delete(group.name, account.name, name)
            try:
                deleting.wait()
            except:
                pass


class JobPreparer(AzureMgmtPreparer):
    def __init__(
        self,
        name_prefix="batch",
        parameter_name="batch_job",
        batch_account_parameter_name=BATCH_ACCOUNT_PARAM,
        batch_credentials_parameter_name="credential",
        batch_pool_parameter_name="batch_pool",
        disable_recording=True,
        playback_fake_resource=None,
        client_kwargs=None,
        **extra_args
    ):
        super(JobPreparer, self).__init__(
            name_prefix,
            24,
            disable_recording=disable_recording,
            playback_fake_resource=playback_fake_resource,
            client_kwargs=client_kwargs,
        )
        self.parameter_name = parameter_name
        self.batch_account_parameter_name = batch_account_parameter_name
        self.batch_credentials_parameter_name = batch_credentials_parameter_name
        self.batch_pool_parameter_name = batch_pool_parameter_name
        self.extra_args = extra_args
        self.resource_moniker = name_prefix

    def _get_batch_client(self, **kwargs):
        try:
            account = kwargs[self.batch_account_parameter_name]
            credential = kwargs[self.batch_credentials_parameter_name]
            return azure.batch.BatchClient(credential=credential, endpoint="https://" + account.account_endpoint)
        except KeyError as exc:
            template = (
                "To create a batch job, a batch account is required. Please add "
                "decorator @AccountPreparer in front of this job preparer."
            )
            raise AzureTestError(template) from exc

    def _get_batch_pool_id(self, **kwargs):
        try:
            pool_id = kwargs[self.batch_pool_parameter_name].name
            return azure.batch.models.BatchPoolInfo(pool_id=pool_id)
        except KeyError:
            auto_pool = azure.batch.models.BatchAutoPoolSpecification(
                pool_lifetime_option=azure.batch.models.BatchPoolLifetimeOption.JOB,
                pool=azure.batch.models.BatchPoolSpecification(
                    vm_size="standard_d2_v2",
                    virtual_machine_configuration=azure.batch.models.VirtualMachineConfiguration(
                        image_reference=azure.batch.models.BatchVmImageReference(
                            publisher="Canonical", offer="0001-com-ubuntu-server-jammy", sku="22_04-lts"
                        ),
                        node_agent_sku_id="batch.node.ubuntu 22.04",
                    ),
                ),
            )
            return azure.batch.models.BatchPoolInfo(auto_pool_specification=auto_pool)

    def create_resource(self, name, **kwargs):
        if self.is_live:
            self.client = self._get_batch_client(**kwargs)
            pool = self._get_batch_pool_id(**kwargs)
            self.resource = azure.batch.models.BatchJobCreateOptions(id=name, pool_info=pool, **self.extra_args)
            try:
                self.client.create_job(self.resource)
            except azure.core.exceptions.HttpResponseError as e:
                message = "{}:{} ".format(e.error.code, e.error.message)
                for v in e.error.values:
                    message += "\n{}: {}".format(v.key, v.value)
                raise AzureTestError(message) from e
            add_general_regex_sanitizer(regex=name, value=self.moniker)
        else:
            self.resource = FakeResource(name=name, id=name)
        return {
            self.parameter_name: self.resource,
        }

    def remove_resource(self, name, **kwargs):
        if self.is_live:
            getattr(self.client, "begin_delete_job")(name).result()
