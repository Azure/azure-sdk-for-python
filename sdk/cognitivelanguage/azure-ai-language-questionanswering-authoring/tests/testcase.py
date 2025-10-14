from devtools_testutils import AzureRecordedTestCase


class QuestionAnsweringAuthoringTestCase(AzureRecordedTestCase):
    @property
    def kwargs_for_polling(self):
        if self.is_playback:
            return {"polling_interval": 0}
        return {}
