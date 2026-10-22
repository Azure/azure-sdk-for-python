# coding: utf-8
# -------------------------------------------------------------------------
# Base test case for runtime Question Answering tests
# -------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase


class QuestionAnsweringTestCase(AzureRecordedTestCase):
    @property
    def kwargs_for_polling(self):
        if self.is_playback: # pylint: disable=using-constant-test
            return {"polling_interval": 0}
        return {}
