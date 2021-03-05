from azure.iot.deviceupdate.models import ImportUpdateInput, ImportManifestMetadata, FileImportMetadata
from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_blob_sas, PublicAccess, BlobSasPermissions
from samples.consts import FILE_NAME

import json
import tempfile
import hashlib
import base64
import os
import uuid


class ContentFactory:
    def __init__(self, storage_name, storage_key, blob_container):
        self._storage_name = storage_name
        self._storage_key = storage_key
        self._connection_string = \
            f"DefaultEndpointsProtocol=https;AccountName={storage_name};AccountKey={storage_key};EndpointSuffix=core.windows.net"
        self._blob_container = blob_container

    def create_import_update(self, manufacturer, name, version):
        payload_file_id = self._generate_storage_id()
        payload_local_file = self._create_adu_payload_file(FILE_NAME, payload_file_id)
        payload_file_size = self._get_file_size(payload_local_file)
        payload_file_hash = self._get_file_hash(payload_local_file)
        payload_url = self._upload_file(payload_local_file, payload_file_id)

        import_manifest_file_id = self._generate_storage_id()
        import_manifest_file = self._create_import_manifest(
            manufacturer, name, version, 
            FILE_NAME, payload_file_size, payload_file_hash,
            [{"DeviceManufacturer": manufacturer.lower(), "DeviceModel": name.lower()}],
            import_manifest_file_id)
        import_manifest_file_size = self._get_file_size(import_manifest_file)
        import_manifest_file_hash = self._get_file_hash(import_manifest_file)
        import_manifest_url = self._upload_file(import_manifest_file, import_manifest_file_id)
        
        return self._create_import_body(import_manifest_url, import_manifest_file_size, import_manifest_file_hash,
                                        FILE_NAME, payload_url)

    def _create_adu_payload_file(self, filename, file_id):
        content = {"Scenario": "DeviceUpdateClientSample",
                   "Timestamp": datetime.utcnow().strftime("%m/%d/%Y, %H:%M:%S")}
        file_path = f"{tempfile.gettempdir()}\\{file_id}"
        file = open(file_path, "w+")
        file.write(json.dumps(content))
        file.close()
        return file_path

    def _create_import_manifest(self, manufacturer, name, version, file_name, file_size, file_hash, compatibility_ids,
                                file_id):
        content = {"UpdateId": {"Provider": manufacturer, "Name": name, "Version": version},
                   "CreatedDateTime": f"{datetime.utcnow().isoformat()}Z",
                   "Files": [{"FileName": file_name, "SizeInBytes": file_size, "Hashes": {"SHA256": file_hash}}],
                   "Compatibility": compatibility_ids, "ManifestVersion": "2.0", "InstalledCriteria": "1.2.3.4",
                   "UpdateType": "microsoft/swupdate:1"}
        file_path = f"{tempfile.gettempdir()}\\{file_id}"
        file = open(file_path, "w+")
        file.write(json.dumps(content))
        file.close()
        return file_path

    def _create_import_body(self, import_manifest_url, import_manifest_file_size, import_manifest_file_hash,
                            file_name, payload_url):
        return ImportUpdateInput(
            import_manifest=ImportManifestMetadata(
                url=import_manifest_url,
                size_in_bytes=import_manifest_file_size,
                hashes={"SHA256": import_manifest_file_hash}),
            files=[FileImportMetadata(filename=file_name, url=payload_url)])


    def _get_file_size(self, file_path):
        return os.path.getsize(file_path)

    def _get_file_hash(self, file_path):
        with open(file_path, "rb") as f:
            bytes = f.read()  # read entire file as bytes
            return base64.b64encode(hashlib.sha256(bytes).digest()).decode("utf-8")

    def _generate_storage_id(self):
        return uuid.uuid4().hex

    def _upload_file(self, file_path, storage_id):
        blob_service_client = BlobServiceClient.from_connection_string(conn_str=self._connection_string)
        try:
            blob_service_client.create_container(self._blob_container, public_access=PublicAccess.Container)
        except:
            pass
        blob_client = blob_service_client.get_blob_client(container=self._blob_container, blob=storage_id)

        with open(file_path, "rb") as data:
            blob_client.upload_blob(data)

        token = generate_blob_sas(
            account_name=self._storage_name,
            account_key=self._storage_key,
            container_name=self._blob_container,
            blob_name=storage_id,
            permission=BlobSasPermissions(read=True),
            expiry=datetime.utcnow() + timedelta(hours=1))
        return f"{blob_client.url}?{token}"

