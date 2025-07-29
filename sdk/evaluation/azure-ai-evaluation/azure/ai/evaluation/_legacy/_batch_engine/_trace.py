# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

# Pretty much all this code will be removed

from typing import Any, Dict, Optional


def start_trace(
    *,
    resource_attributes: Optional[Dict] = None,
    collection: Optional[str] = None,
    **kwargs: Any,
) -> None:
    """Starts a trace.

    :param resource_attributes: Specify the resource attributes for current process.
    :type resource_attributes: typing.Optional[dict]
    :param collection: Specify the collection for current tracing.
    :type collection: typing.Optional[str]
    """
    pass

    # res_attrs: Dict[str, str] = {"service.name": "promptflow"}
    # if resource_attributes:
    #     logging.debug("specified resource attributes: %s", resource_attributes)
    #     res_attrs.update(resource_attributes)

    # # determine collection
    # collection_user_specified = collection is not None
    # if not collection_user_specified:
    #     collection = kwargs.get("_collection", _get_collection_from_cwd())
    #    logging.debug("collection is not user specified")
    #     if is_collection_writeable():
    #         # internal parameter for devkit call
    #         _collection = kwargs.get("_collection", None)
    #         if _collection is not None:
    #             logging.debug("received internal parameter _collection: %s, will use this", _collection)
    #             collection = _collection
    #         else:
    #             logging.debug("trying to get from current working directory...")
    #             collection = _get_collection_from_cwd()
    #     # TODO ralphe: OpenTelemetry dependency. This is a future task to resolve.
    #     # else:
    #     #     logging.debug("collection is protected, will directly use that...")
    #     #     tracer_provider: TracerProvider = trace.get_tracer_provider()
    #     #     collection = tracer_provider.resource.attributes["collection"]
    # logging.info("collection: %s", collection)
    # res_attrs["collection"] = collection or "default"
    # logging.info("resource attributes: %s", res_attrs)

    # # if user specifies collection, we will add a flag on tracer provider to avoid override
    # _set_tracer_provider(res_attrs, protected_collection=collection_user_specified)

    # Rest of code is removed since we are removing promptflow-devkit dependency


# def is_collection_writeable() -> bool:
#     # TODO ralphe: This has OpenTelemetry dependency. That is a future task to resolve.
#     # return not getattr(trace.get_tracer_provider(), TRACER_PROVIDER_PROTECTED_COLLECTION_ATTR, False)
#     return True


# def _get_collection_from_cwd() -> str:
#     """Try to use cwd folder name as collection name; will fall back to default value if run into exception."""
#     cur_folder_name = ""
#     try:
#         cwd = os.getcwd()
#         cur_folder_name = os.path.basename(cwd)
#     except Exception:  # pylint: disable=broad-except
#         # possible exception: PermissionError, FileNotFoundError, OSError, etc.
#         pass
#     collection = cur_folder_name or "default"
#     return collection


# def _set_tracer_provider(res_attrs: Dict[str, str], protected_collection: bool) -> None:
#     # TODO ralphe: OpenTelemetry dependency. This is a future task to resolve.
#     # res = Resource(attributes=res_attrs)
#     # tracer_provider = TracerProvider(resource=res)

#     # cur_tracer_provider = trace.get_tracer_provider()
#     # if isinstance(cur_tracer_provider, TracerProvider):
#     #     logging.info("tracer provider is already set, will merge the resource attributes...")
#     #     cur_res = cur_tracer_provider.resource
#     #     logging.debug("current resource: %s", cur_res.attributes)
#     #     new_res = cur_res.merge(res)
#     #     cur_tracer_provider._resource = new_res
#     #     logging.info("tracer provider is updated with resource attributes: %s", new_res.attributes)
#     # else:
#     #     trace.set_tracer_provider(tracer_provider)
#     #     logging.info("tracer provider is set with resource attributes: %s", res.attributes)

#     # if protected_collection:
#     #     logging.info("user specifies collection, will add a flag on tracer provider to avoid override...")
#     #     setattr(trace.get_tracer_provider(), TRACER_PROVIDER_PROTECTED_COLLECTION_ATTR, True)
