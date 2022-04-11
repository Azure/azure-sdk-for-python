# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------


class ProgressTracker:
    def __init__(self, total: int, step: int):
        self.total = total
        self.step = step
        self.current = 0

    def assert_progress(self, current: int, total: int):
        print(current, total)
        if self.current != self.total:
            self.current += self.step

        assert self.total == total
        assert self.current == current

    def assert_complete(self):
        assert self.total == self.current
