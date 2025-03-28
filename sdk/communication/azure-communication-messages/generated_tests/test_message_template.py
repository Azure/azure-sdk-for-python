# coding=utf-8
import pytest
from devtools_testutils import recorded_by_proxy
from testpreparer import MessageTemplateClientTestBase, MessageTemplatePreparer


@pytest.mark.skip("you may need to update the auto-generated test case before run it")
class TestMessageTemplate(MessageTemplateClientTestBase):
    @MessageTemplatePreparer()
    @recorded_by_proxy
    def test_list_templates(self, messagetemplate_endpoint):
        client = self.create_client(endpoint=messagetemplate_endpoint)
        response = client.list_templates(
            channel_id="str",
        )
        result = [r for r in response]
        # please add some check logic here by yourself
        # ...
