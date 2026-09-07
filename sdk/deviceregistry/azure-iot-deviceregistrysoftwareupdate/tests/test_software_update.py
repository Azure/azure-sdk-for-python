# coding: utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from azure.iot.deviceregistrysoftwareupdate.models import (
    FileImportMetadata,
    ImportManifestMetadata,
    ImportUpdateInputItem,
    ImportUpdateRequest,
    Update,
)
from devtools_testutils import recorded_by_proxy

from testcase import DeviceRegistrySoftwareUpdatePreparer, DeviceRegistrySoftwareUpdateTest


class TestSoftwareUpdate(DeviceRegistrySoftwareUpdateTest):
    @DeviceRegistrySoftwareUpdatePreparer()
    @recorded_by_proxy
    def test_import_update(
        self,
        deviceregistrysoftwareupdate_endpoint,
        deviceregistrysoftwareupdate_manifest_url,
        deviceregistrysoftwareupdate_file_url,
    ):
        client = self.create_client(deviceregistrysoftwareupdate_endpoint)
        provider = "Contoso"
        name = "Toaster"
        version = "1.0"
        imported = False

        request = ImportUpdateRequest(
            import_update_input=[
                ImportUpdateInputItem(
                    import_manifest=ImportManifestMetadata(
                        url=deviceregistrysoftwareupdate_manifest_url.secret,
                        size_in_bytes=712,
                        hashes={"sha256": "PHuSWFOX73yLXeaIrSo9gtsiGGKOKY6fw5n6/6rFFh4="},
                    ),
                    files=[
                        FileImportMetadata(
                            file_name="README.md",
                            url=deviceregistrysoftwareupdate_file_url.secret,
                        )
                    ],
                )
            ]
        )

        try:
            poller = client.software_update.begin_import_update(request)
            imported = True
            result = poller.result()

            assert result is None
            assert poller.done()
            assert poller.status() == "Succeeded"

            update = client.software_update.get_update(provider, name, version)
            assert isinstance(update, Update)
            assert update.manifest_version == "4.0"
        finally:
            if imported:
                delete_poller = client.software_update.begin_delete_update(provider, name, version)
                delete_result = delete_poller.result()

                assert delete_result is None
                assert delete_poller.done()
                assert delete_poller.status() == "Succeeded"

    @DeviceRegistrySoftwareUpdatePreparer()
    @recorded_by_proxy
    def test_list_updates(self, deviceregistrysoftwareupdate_endpoint):
        client = self.create_client(deviceregistrysoftwareupdate_endpoint)

        updates = list(client.software_update.list_updates())

        assert all(isinstance(update, Update) for update in updates)

    @DeviceRegistrySoftwareUpdatePreparer()
    @recorded_by_proxy
    def test_list_providers(self, deviceregistrysoftwareupdate_endpoint):
        client = self.create_client(deviceregistrysoftwareupdate_endpoint)

        providers = list(client.software_update.list_providers())

        assert all(isinstance(provider, str) for provider in providers)