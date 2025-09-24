from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient

from .helpers import AuthoringTestHelper
from .testcase import QuestionAnsweringAuthoringTestCase


class TestExportAndImport(QuestionAnsweringAuthoringTestCase):
    def test_export_project(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"]))
        project_name = "IsaacNewton"
        AuthoringTestHelper.create_test_project(client, project_name=project_name, **self.kwargs_for_polling)
        export_poller = client.begin_export(
            project_name=project_name, file_format="json", **self.kwargs_for_polling
        )
        result = export_poller.result()
        assert result["status"] == "succeeded"
        assert result["resultUrl"]

    def test_import_project(self, recorded_test, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"]))
        project_name = "IsaacNewton"
        AuthoringTestHelper.create_test_project(
            client,
            project_name=project_name,
            get_export_url=True,
            delete_old_project=True,
            **self.kwargs_for_polling,
        )
        project_payload = {
            "Metadata": {
                "ProjectName": project_name,
                "Description": "Biography of Sir Isaac Newton",
                "Language": "en",
                "MultilingualResource": False,
                "Settings": {"DefaultAnswer": "no answer"},
            }
        }
        import_poller = client.begin_import_assets(
            project_name=project_name, options=project_payload, **self.kwargs_for_polling
        )
        job_state = import_poller.result()
        assert job_state["jobId"]
        assert any(p.get("projectName") == project_name for p in client.list_projects())
