# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package
from devtools_testutils import AzureMgmtTestCase

class TemplateTest(AzureMgmtTestCase):
    def setUp(self):
        super(TemplateTest, self).setUp()

    def test_case_default(self):
        self.assertEqual(True, True)
