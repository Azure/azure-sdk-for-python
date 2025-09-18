# coding: utf-8
# -------------------------------------------------------------------------
# Base test case for runtime Question Answering tests
# -------------------------------------------------------------------------
from devtools_testutils import AzureRecordedTestCase

class QuestionAnsweringTestCase(AzureRecordedTestCase):
    @property
    def kwargs_for_polling(self):  # retained for any future LROs (none expected in runtime only)
        if self.is_playback:
            return {"polling_interval": 0}
        return {}
