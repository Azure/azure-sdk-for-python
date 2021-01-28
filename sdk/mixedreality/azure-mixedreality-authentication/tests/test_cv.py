# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from azure.mixedreality.authentication.utils._cv import _generate_cv_base

class TestCv:
    def test_generate_cv_base(self):
        cv = _generate_cv_base()

        assert cv is not None
        assert len(cv) == 22

    def test_generate_cv_base_are_random(self):
        cv1 = _generate_cv_base()
        cv2 = _generate_cv_base()

        assert cv1 is not None
        assert cv2 is not None
        assert cv1 != cv2
