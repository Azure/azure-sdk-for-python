# ------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# -------------------------------------------------------------------------
from ._featurefilters import FeatureFilter

import random

class RandomFilter(FeatureFilter):

    def evaluate(self, context, **kwargs):
        """Determain if the feature flag is enabled for the given context"""
        if context.parameters.get('Value', 0) < random.randint(0, 100):
            return True
        else:
            return False
