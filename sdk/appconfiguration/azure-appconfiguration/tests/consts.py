# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
PAGE_SIZE = 100
KEY_UUID = "test_key_a6af8952-54a6-11e9-b600-2816a84d0309"
LABEL_UUID = "1d7b2b28-549e-11e9-b51c-2816a84d0309"
KEY = "PYTHON_UNIT_" + KEY_UUID
LABEL = "test_label1_" + LABEL_UUID
LABEL_RESERVED_CHARS = "test_label2_*, \\" + LABEL_UUID  # contains reserved chars *,\
TEST_CONTENT_TYPE = "test content type"
TEST_VALUE = "test value"
APPCONFIGURATION_CONNECTION_STRING = "Endpoint=https://fake_app_config.azconfig-test.io;Id=0-l4-s0:h5htBaY5Z1LwFz50bIQv;Secret=lamefakesecretlamefakesecretlamefakesecrett="  # pylint:disable=line-too-long
