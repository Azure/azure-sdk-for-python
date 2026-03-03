class AuthoringTestHelper:
    """Utility helper for creating and exporting authoring test projects."""

    _SURFACE_BOOK_GUIDE_URL = "https://download.microsoft.com/download/7/B/1/7B10C82E-F520-4080-8516-5CF0D803EEE0/surface-book-user-guide-EN.pdf"
    _SURFACE_BOOK_GUIDE_DISPLAY_NAME = "surface-book-user-guide-EN"

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
        return None

    @staticmethod
    def add_sources(client, project_name, **kwargs):
        poller = client.begin_update_sources(
            project_name=project_name,
            sources=[
                {
                    "op": "add",
                    "value": {
                        "displayName": AuthoringTestHelper._SURFACE_BOOK_GUIDE_DISPLAY_NAME,
                        "source": AuthoringTestHelper._SURFACE_BOOK_GUIDE_URL,
                        "sourceUri": AuthoringTestHelper._SURFACE_BOOK_GUIDE_URL,
                        "sourceKind": "url",
                        "contentStructureKind": "unstructured",
                        "refresh": False,
                    },
                }
            ],
            **kwargs,
        )
        poller.result()

    @staticmethod
    def export_project(client, project_name, delete_project=True, **kwargs): # pylint: disable=useless-return
        # begin_export poller is typed as LROPoller[None]; generator currently discards
        # the final body so result() returns None. We only validate successful completion.
        export_poller = client.begin_export(project_name=project_name, file_format="json", **kwargs)
        export_poller.result()  # ensure completion (raises on failure)
        if delete_project:
            delete_poller = client.begin_delete_project(project_name=project_name, **kwargs)
            delete_poller.result()
        return None

class AuthoringAsyncTestHelper:
    """Async utility helper for creating and exporting authoring test projects."""

    _SURFACE_BOOK_GUIDE_URL = AuthoringTestHelper._SURFACE_BOOK_GUIDE_URL
    _SURFACE_BOOK_GUIDE_DISPLAY_NAME = AuthoringTestHelper._SURFACE_BOOK_GUIDE_DISPLAY_NAME

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
                        "displayName": AuthoringAsyncTestHelper._SURFACE_BOOK_GUIDE_DISPLAY_NAME,
                        "source": AuthoringAsyncTestHelper._SURFACE_BOOK_GUIDE_URL,
                        "sourceUri": AuthoringAsyncTestHelper._SURFACE_BOOK_GUIDE_URL,
                        "sourceKind": "url",
                        "contentStructureKind": "unstructured",
                        "refresh": False,
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
