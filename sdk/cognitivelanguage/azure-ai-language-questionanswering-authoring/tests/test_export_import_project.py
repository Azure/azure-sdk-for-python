from helpers import AuthoringTestHelper
from testcase import QuestionAnsweringAuthoringTestCase

from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering.authoring import QuestionAnsweringAuthoringClient, models as _models



class TestExportAndImport(QuestionAnsweringAuthoringTestCase):
    def test_export_project(self, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        AuthoringTestHelper.create_test_project(
            client, project_name=project_name, polling_interval=0 if self.is_playback else None # pylint: disable=using-constant-test
        )
        export_poller = client.begin_export(
            project_name=project_name,
            file_format="json",
            polling_interval=0 if self.is_playback else None, # pylint: disable=using-constant-test
        )
        export_poller.result()  # LROPoller[None]; ensure no exception
        assert export_poller.done()

    def test_import_project(self, qna_authoring_creds):  # type: ignore[name-defined]
        client = QuestionAnsweringAuthoringClient(
            qna_authoring_creds["endpoint"], AzureKeyCredential(qna_authoring_creds["key"])
        )
        project_name = "IsaacNewton"
        # Create project without deleting it; we just need it present for import.
        AuthoringTestHelper.create_test_project(
            client,
            project_name=project_name,
            get_export_url=False,
            delete_old_project=False,
            polling_interval=0 if self.is_playback else None, # pylint: disable=using-constant-test
        )
        # Wait briefly until project is visible (eventual consistency safeguard)
        visible = any(p.get("projectName") == project_name for p in client.list_projects())
        if not visible:
            import time

            for _ in range(5):
                time.sleep(1)
                if any(p.get("projectName") == project_name for p in client.list_projects()):
                    visible = True
                    break
        assert visible, "Project not visible for import"
        # Provide a minimal valid ImportJobOptions with one QnA to avoid empty list validation failure.
        project_payload = _models.ImportJobOptions(
            assets=_models.Assets(
                qnas=[
                    _models.ImportQnaRecord(
                        id=1,
                        answer="Gravity is a force of attraction.",
                        source="https://wikipedia.org/wiki/Isaac_Newton",
                        questions=["What is gravity?"],
                    )
                ]
            )
        )
        import_poller = client.begin_import_assets(
            project_name=project_name,
            body=project_payload,
            file_format="json",
            polling_interval=0 if self.is_playback else None, # pylint: disable=using-constant-test
        )
        import_poller.result()  # LROPoller[None]; ensure completion
        assert import_poller.done()
        assert any(p.get("projectName") == project_name for p in client.list_projects())
