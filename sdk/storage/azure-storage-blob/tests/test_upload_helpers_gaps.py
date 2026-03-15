# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from unittest import mock

import pytest
from azure.core.exceptions import ResourceExistsError, ResourceModifiedError
from azure.storage.blob import StorageErrorCode
from azure.storage.blob._upload_helpers import _convert_mod_error

from devtools_testutils.storage import StorageRecordedTestCase


class TestUploadHelpersGaps(StorageRecordedTestCase):

    def _get_modified_error(self, message):
        # Tests defensive branch — requires mock.
        response = mock.Mock()
        response.status_code = 412
        error = ResourceModifiedError(message=message, response=response)
        return error, response

    def test_convert_mod_error_when_condition_not_met_phrase_present_replaces_message(self):
        error, _ = self._get_modified_error(
            "The condition specified using HTTP conditional header(s) is not met.")

        with pytest.raises(ResourceExistsError) as exc:
            _convert_mod_error(error)

        assert exc.value.message == "The specified blob already exists."

    def test_convert_mod_error_when_condition_not_met_code_present_replaces_error_code_text(self):
        error, _ = self._get_modified_error("ConditionNotMet")

        with pytest.raises(ResourceExistsError) as exc:
            _convert_mod_error(error)

        assert exc.value.message == "BlobAlreadyExists"

    def test_convert_mod_error_when_called_creates_resource_exists_error(self):
        error, response = self._get_modified_error("already failed")

        with pytest.raises(ResourceExistsError) as exc:
            _convert_mod_error(error)

        assert type(exc.value) is ResourceExistsError
        assert exc.value.response is response

    def test_convert_mod_error_when_called_sets_blob_already_exists_error_code(self):
        error, _ = self._get_modified_error("already failed")

        with pytest.raises(ResourceExistsError) as exc:
            _convert_mod_error(error)

        assert exc.value.error_code == StorageErrorCode.blob_already_exists

    def test_convert_mod_error_when_called_raises_transformed_exception(self):
        error, _ = self._get_modified_error("already failed")

        with pytest.raises(ResourceExistsError) as exc:
            _convert_mod_error(error)

        assert exc.value.message == "already failed"
