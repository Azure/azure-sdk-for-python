# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

import json
import os
import hashlib
import logging
# from opencensus.ext.azure.log_exporter import AzureLogHandler

log = logging.getLogger(__name__)


def create_catalog_stub():
    """
    Function that creates a json stub of the form: {'HashAlgorithm': 'SHA256', 'CatalogItems': {}}.
    """
    json_stub = {}
    json_stub["HashAlgorithm"] = "SHA256"
    json_stub["CatalogItems"] = {}
    return json_stub


def create_SHA_256_hash_of_file(file):
    """
    Function that returns the SHA 256 hash of 'file'.\n
    Logic taken from https://www.quickprogrammingtips.com/python/how-to-calculate-sha256-hash-of-a-file-in-python.html
    """
    sha256_hash = hashlib.sha256()
    with open(file, "rb") as f:
        # Read and update hash string value in blocks of 4K
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
        # Converting to upper case because that's what is required by the policy
        # service. See their code:
        # https://dev.azure.com/msasg/Bing_and_IPG/_git/Aether?path=/src/aether/platform/backendV2/BlueBox/PolicyService/Microsoft.MachineLearning.PolicyService/Workers/CatalogValidation.cs
        return sha256_hash.hexdigest().upper()


def add_file_to_catalog(file_for_catalog, catalog, absolute_path_to_remove):
    """
    Function that adds an entry for 'file_for_catalog' to the 'catalog'.\n
    Specifically, {<Relative path of file>: <Hash of file>} will be added to the "CatalogItems" dictionary of the 'catalog' json, where <Hash of file> is computed with the create_SHA_256_hash_of_file() function, and <Relative path of file> is obtained by removing 'absolute_path_to_remove' from the full 'file_for_catalog' path
    """
    hash_of_file = create_SHA_256_hash_of_file(file_for_catalog)
    relative_path = file_for_catalog.split(absolute_path_to_remove)[1]
    catalog["CatalogItems"][relative_path] = hash_of_file
    return catalog


def write_two_catalog_files(catalog, path):
    """
    Function that writes 'catalog' into 2 duplicate files: "path/config.json" and "path/config.json.sig".
    """
    with open(os.path.join(path, "catalog.json"), "w") as jsonFile1:
        json.dump(catalog, jsonFile1)
    with open(os.path.join(path, "catalog.json.sig"), "w") as jsonFile2:
        json.dump(catalog, jsonFile2)


def delete_two_catalog_files(path):
    """
    Function that deletes the "catalog.json" and "catalog.json.sig" files located at 'path', if they exist
    """
    # catalog.json
    file_path_json = os.path.join(path, "catalog.json")
    if os.path.exists(file_path_json):
        log.warning(f"{file_path_json} already exists. Deleting it")
        os.remove(file_path_json)
    # catalog.json.sig
    file_path_json_sig = os.path.join(path, "catalog.json.sig")
    if os.path.exists(file_path_json_sig):
        log.warning(f"{file_path_json_sig} already exists. Deleting it")
        os.remove(file_path_json_sig)


# class TelemetryLogger:
#     """Utils class for opencensus azure monitor"""

#     def __init__(
#         self, enable_telemetry=True, instrumentation_key=None, level=logging.INFO
#     ):
#         self.logger = logging.getLogger("telemetry_logger")
#         self.logger.setLevel(level)
#         self.enable_telemetry = enable_telemetry
#         # Why is it okay to include this key directly in the source code?
#         # For any client-side tool, there is a fundamental problem with protecting instrumentation
#         # keys. You want the published tool to be able to collect telemetry, but the only way
#         # it can do this is if it has some kind of instrumentation key.
#         #
#         # For an authoritative example, the dotnet CLI contains their telemetry key in a
#         # public GitHub repository:
#         # https://github.com/dotnet/cli/blob/master/src/dotnet/Telemetry/Telemetry.cs
#         #
#         # The underlying Azure resource is called `aml1p-ml-tooling`.
#         self.instrumentation_key = (
#             "aaefce9e-d109-4fac-bb9f-8277c68e91ac"
#             if instrumentation_key is None
#             else instrumentation_key
#         )
#         handler = AzureLogHandler(
#                 connection_string=f"InstrumentationKey={self.instrumentation_key}"
#             )
#         handler.add_telemetry_processor(self.scrubber_function)
#         self.logger.addHandler(handler)

#     def log_trace(self, message, properties={}, level=logging.INFO):
#         if self.enable_telemetry:
#             try:
#                 if level == logging.INFO:
#                     self.logger.info(message, extra=properties)
#                 elif level == logging.WARNING:
#                     self.logger.warning(message, extra=properties)
#                 elif level == logging.ERROR:
#                     self.logger.error(message, extra=properties)
#                 elif level == logging.CRITICAL:
#                     self.logger.critical(message, extra=properties)
#                 else:
#                     log.error("The logging level is not expected!")
#             except Exception as ex:
#                 log.warning("Send telemetry exception: %s", str(ex))
#         else:
#             log.info(
#                 "Sending trace log messages to application insight has been disabled."
#             )
    
#     # Callback function to scrub some columns
#     def scrubber_function(self, envelope):
#         envelope.tags['ai.cloud.roleInstance'] = 'cloud_RoleInstance_Scrubbed'
#         envelope.tags["ai.location.ip"] = "IP_Scrubbed"
