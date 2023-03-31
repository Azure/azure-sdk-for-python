# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

class TestHelper():
    def distance(self, s1, s2, n1, n2):
        if n1 == 0:
            return n2

        if n2 == 0:
            return n1

        if s1[n1 - 1] == s2[n2 - 1]:
            return self.distance(s1, s2, n1 - 1, n2 - 1)

        nums = [self.distance(s1, s2, n1, n2 - 1),
                self.distance(s1, s2, n1 - 1, n2),
                self.distance(s1, s2, n1 - 1, n2 - 1)]
        return 1 + min(nums)

    def edit_distance(self, s1, s2):
        n1 = len(s1)
        n2 = len(s2)
        return self.distance(s1, s2, n1, n2)
