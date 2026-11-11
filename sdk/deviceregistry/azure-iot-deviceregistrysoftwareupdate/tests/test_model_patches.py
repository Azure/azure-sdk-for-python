# coding: utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

from azure.iot.deviceregistrysoftwareupdate.models import ImportUpdateRequest, UpdateId


def test_model_copy_preserves_type_and_data():
    model = UpdateId(provider="contoso", name="firmware", version="1.0")

    copied_model = model.copy()

    assert isinstance(copied_model, UpdateId)
    assert copied_model == model
    assert copied_model is not model
    assert dict(copied_model) == dict(model)

    copied_model.version = "2.0"

    assert model.version == "1.0"


def test_enable_scan_defaults_to_false():
    model = ImportUpdateRequest(import_update_input=[])

    assert model.enable_scan is False
    assert dict(model)["enableScan"] is False
