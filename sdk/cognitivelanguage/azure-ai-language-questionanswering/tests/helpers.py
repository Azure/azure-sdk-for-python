# coding=utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

class QnaAuthoringHelper:

    def create_test_project(
        client,
        project_name = "IssacNewton",
        is_deployable = False,
        add_sources = False,
        get_export_url = False,
        delete_old_project = False,
        add_qnas = False,
        **kwargs
    ):
        # create project
        client.create_project(
            project_name=project_name,
            options={
                "description": "biography of Sir Issac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {
                    "defaultAnswer": "no answer"
                }
            })

        # add sources
        if is_deployable or add_sources:
            QnaAuthoringHelper.add_sources(client, project_name, **kwargs)

        if get_export_url:
            return QnaAuthoringHelper.export_project(client, project_name, delete_project=delete_old_project, **kwargs)

    def add_sources(client, project_name, **kwargs):
        update_sources_poller = client.begin_update_sources(
            project_name=project_name,
            sources=[
                {
                    "op": "add",
                    "value": {
                        "displayName": "Issac Newton Bio",
                        "sourceUri": "https://wikipedia.org/wiki/Isaac_Newton",
                        "sourceKind": "url"
                    }
                }
            ],
            **kwargs
        )
        update_sources_poller.result()

    def export_project(client, project_name, delete_project=True, **kwargs):
        # export project
        export_poller = client.begin_export(
            project_name=project_name,
            file_format="json",
            **kwargs
        )
        result = export_poller.result()

        # delete old project
        if delete_project:
            delete_poller = client.begin_delete_project(
                project_name=project_name,
                **kwargs
            )
            delete_poller.result()
        return result["resultUrl"]


class QnaAuthoringAsyncHelper:

    async def create_test_project(
        client,
        project_name = "IssacNewton",
        is_deployable = False,
        add_sources = False,
        get_export_url = False,
        delete_old_project = False,
        add_qnas = False,
        **kwargs
    ):
        # create project
        await client.create_project(
            project_name=project_name,
            options={
                "description": "biography of Sir Issac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {
                    "defaultAnswer": "no answer"
                }
            })

        # add sources
        if is_deployable or add_sources:
            await QnaAuthoringAsyncHelper.add_sources(client, project_name, **kwargs)

        if get_export_url:
            return await QnaAuthoringAsyncHelper.export_project(client, project_name, delete_project=delete_old_project, **kwargs)

    async def add_sources(client, project_name, **kwargs):
        update_sources_poller = await client.begin_update_sources(
            project_name=project_name,
            sources=[
                {
                    "op": "add",
                    "value": {
                        "displayName": "Issac Newton Bio",
                        "sourceUri": "https://wikipedia.org/wiki/Isaac_Newton",
                        "sourceKind": "url"
                    }
                }
            ],
            **kwargs
        )
        await update_sources_poller.result()

    async def export_project(client, project_name, delete_project=True, **kwargs):
        # export project
        export_poller = await client.begin_export(
            project_name=project_name,
            file_format="json",
            **kwargs
        )
        result = await export_poller.result()

        # delete old project
        if delete_project:
            delete_poller = await client.begin_delete_project(
                project_name=project_name,
                **kwargs
            )
            await delete_poller.result()
        return result["resultUrl"]
