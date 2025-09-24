class AuthoringTestHelper:
    """Utility helper for creating and exporting authoring test projects."""

    @staticmethod
    def create_test_project(
        client,
        project_name="IsaacNewton",
        is_deployable=False,
        add_sources=False,
        get_export_url=False,
        delete_old_project=False,
        **kwargs,
    ):
        client.create_project(
            project_name=project_name,
            options={
                "description": "Biography of Sir Isaac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {"defaultAnswer": "no answer"},
            },
        )
        if is_deployable or add_sources:
            AuthoringTestHelper.add_sources(client, project_name, **kwargs)
        if get_export_url:
            return AuthoringTestHelper.export_project(client, project_name, delete_project=delete_old_project, **kwargs)

    @staticmethod
    def add_sources(client, project_name, **kwargs):
        poller = client.begin_update_sources(
            project_name=project_name,
            sources=[
                {
                    "op": "add",
                    "value": {
                        "displayName": "Isaac Newton Bio",
                        "sourceUri": "https://wikipedia.org/wiki/Isaac_Newton",
                        "sourceKind": "url",
                    },
                }
            ],
            **kwargs,
        )
        poller.result()

    @staticmethod
    def export_project(client, project_name, delete_project=True, **kwargs):
        export_poller = client.begin_export(project_name=project_name, file_format="json", **kwargs)
        result = export_poller.result()
        if delete_project:
            delete_poller = client.begin_delete_project(project_name=project_name, **kwargs)
            delete_poller.result()
        return result["resultUrl"]


class AuthoringAsyncTestHelper:
    """Async utility helper for creating and exporting authoring test projects."""

    @staticmethod
    async def create_test_project(
        client,
        project_name="IsaacNewton",
        is_deployable=False,
        add_sources=False,
        get_export_url=False,
        delete_old_project=False,
        **kwargs,
    ):
        await client.create_project(
            project_name=project_name,
            options={
                "description": "Biography of Sir Isaac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {"defaultAnswer": "no answer"},
            },
        )
        if is_deployable or add_sources:
            await AuthoringAsyncTestHelper.add_sources(client, project_name, **kwargs)
        if get_export_url:
            return await AuthoringAsyncTestHelper.export_project(
                client, project_name, delete_project=delete_old_project, **kwargs
            )

    @staticmethod
    async def add_sources(client, project_name, **kwargs):
        poller = await client.begin_update_sources(
            project_name=project_name,
            sources=[
                {
                    "op": "add",
                    "value": {
                        "displayName": "Isaac Newton Bio",
                        "sourceUri": "https://wikipedia.org/wiki/Isaac_Newton",
                        "sourceKind": "url",
                    },
                }
            ],
            **kwargs,
        )
        await poller.result()

    @staticmethod
    async def export_project(client, project_name, delete_project=True, **kwargs):
        export_poller = await client.begin_export(project_name=project_name, file_format="json", **kwargs)
        result = await export_poller.result()
        if delete_project:
            delete_poller = await client.begin_delete_project(project_name=project_name, **kwargs)
            await delete_poller.result()
        return result["resultUrl"]

