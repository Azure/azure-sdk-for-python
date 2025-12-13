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
        # Separate polling keyword (if present) from feature flags to avoid accidental binding confusions
        polling_interval = kwargs.pop("polling_interval", None)
        client.create_project(
            project_name=project_name,
            options={
                "description": "Biography of Sir Isaac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {"defaultAnswer": "no answer"},
            },
        )
        source_kwargs = {"polling_interval": polling_interval} if polling_interval is not None else {}
        if is_deployable or add_sources:
            AuthoringTestHelper.add_sources(client, project_name, **source_kwargs)
        if get_export_url:
            return AuthoringTestHelper.export_project(
                client, project_name, delete_project=delete_old_project, **source_kwargs
            )

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
        # begin_export poller is typed as LROPoller[None]; generator currently discards
        # the final body so result() returns None. We only validate successful completion.
        export_poller = client.begin_export(project_name=project_name, file_format="json", **kwargs)
        export_poller.result()  # ensure completion (raises on failure)
        if delete_project:
            delete_poller = client.begin_delete_project(project_name=project_name, **kwargs)
            delete_poller.result()
        # No export URL available due to None payload; caller should not depend on return value.
        return None


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
        polling_interval = kwargs.pop("polling_interval", None)
        await client.create_project(
            project_name=project_name,
            options={
                "description": "Biography of Sir Isaac Newton",
                "language": "en",
                "multilingualResource": True,
                "settings": {"defaultAnswer": "no answer"},
            },
        )
        source_kwargs = {"polling_interval": polling_interval} if polling_interval is not None else {}
        if is_deployable or add_sources:
            await AuthoringAsyncTestHelper.add_sources(client, project_name, **source_kwargs)
        if get_export_url:
            return await AuthoringAsyncTestHelper.export_project(
                client, project_name, delete_project=delete_old_project, **source_kwargs
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
        await export_poller.result()
        if delete_project:
            delete_poller = await client.begin_delete_project(project_name=project_name, **kwargs)
            await delete_poller.result()
        return None
