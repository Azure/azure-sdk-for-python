# --------------------------------------------------------------------------
#
# Copyright (c) Microsoft Corporation. All rights reserved.
#
# The MIT License (MIT)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the ""Software""), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED *AS IS*, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# --------------------------------------------------------------------------
import os

import pytest

# module under test
import azure.core.settings as m


class TestPrioritizedSetting(object):
    def test_everything_unset_raises(self):
        ps = m.PrioritizedSetting("foo")
        with pytest.raises(RuntimeError):
            ps()

    def test_implict_default(self):
        ps = m.PrioritizedSetting("foo", default=10)
        assert ps() == 10

    def test_implict_default_converts(self):
        ps = m.PrioritizedSetting("foo", convert=int, default="10")
        assert ps() == 10

    def test_system_hook(self):
        ps = m.PrioritizedSetting("foo", system_hook=lambda: 20)
        assert ps() == 20

    def test_system_hook_converts(self):
        ps = m.PrioritizedSetting("foo", convert=int, system_hook=lambda: "20")
        assert ps() == 20

    def test_env_var(self):
        os.environ["AZURE_FOO"] = "30"
        ps = m.PrioritizedSetting("foo", env_var="AZURE_FOO")
        assert ps() == "30"
        del os.environ["AZURE_FOO"]

    def test_env_var_converts(self):
        os.environ["AZURE_FOO"] = "30"
        ps = m.PrioritizedSetting("foo", convert=int, env_var="AZURE_FOO")
        assert ps() == 30
        del os.environ["AZURE_FOO"]

    def test_user_set(self):
        ps = m.PrioritizedSetting("foo")
        ps.set_value(40)
        assert ps() == 40

    def test_user_set_converts(self):
        ps = m.PrioritizedSetting("foo", convert=int)
        ps.set_value("40")
        assert ps() == 40

    def test_immediate(self):
        ps = m.PrioritizedSetting("foo")
        assert ps(50) == 50

    def test_immediate_converts(self):
        ps = m.PrioritizedSetting("foo", convert=int)
        assert ps("50") == 50

    def test_precedence(self):
        # 0. implicit default
        ps = m.PrioritizedSetting("foo", env_var="AZURE_FOO", convert=int, default=10)
        assert ps() == 10

        # 1. system value
        ps = m.PrioritizedSetting(
            "foo", env_var="AZURE_FOO", convert=int, default=10, system_hook=lambda: 20
        )
        assert ps() == 20

        # 2. environment variable
        os.environ["AZURE_FOO"] = "30"
        assert ps() == 30

        # 3. previously user-set value
        ps.set_value(40)
        assert ps() == 40

        # 4. immediate values
        assert ps(50) == 50

        del os.environ["AZURE_FOO"]

    def test___str__(self):
        ps = m.PrioritizedSetting("foo")
        assert str(ps) == "PrioritizedSetting(%r)" % "foo"

    def test_descriptors(self):
        class FakeSettings(object):
            foo = m.PrioritizedSetting("foo", env_var="AZURE_FOO")
            bar = m.PrioritizedSetting("bar", env_var="AZURE_BAR", default=10)

        s = FakeSettings()
        assert s.foo is FakeSettings.foo

        assert s.bar() == 10
        s.bar = 20
        assert s.bar() == 20
