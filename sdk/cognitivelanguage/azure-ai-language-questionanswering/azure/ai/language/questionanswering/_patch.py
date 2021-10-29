# coding=utf-8
# --------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------

import six
import copy
from .models import TextDocument


def _validate_text_records(records):
    if not records:
        raise ValueError("Input documents can not be empty or None")

    if isinstance(records, six.string_types):
        raise TypeError("Input documents cannot be a string.")

    if isinstance(records, dict):
        raise TypeError("Input documents cannot be a dict")

    if not all(isinstance(x, six.string_types) for x in records):
        if not all(isinstance(x, (dict, TextDocument)) for x in records):
            raise TypeError("Mixing string and dictionary/object document input unsupported.")

    request_batch = []
    for idx, doc in enumerate(records):
        if isinstance(doc, six.string_types):
            record = {"id": str(idx), "text": doc}
            request_batch.append(record)
        else:
            request_batch.append(doc)
    return request_batch


def _get_positional_body(*args, **kwargs):
    """Verify args and kwargs are valid, and then return the positional body, if users passed it in."""
    if len(args) > 1:
        raise TypeError("There can only be one positional argument, which is the POST body of this request.")
    if args and "options" in kwargs:
        raise TypeError(
            "You have already supplied the request body as a positional parameter, "
            "you can not supply it as a keyword argument as well."
        )
    return args[0] if args else None


def _verify_qna_id_and_question(query_knowledgebase_options):
    """For query_knowledge_base we require either `question` or `qna_id`."""
    try:
        qna_id = query_knowledgebase_options.qna_id
        question = query_knowledgebase_options.question
    except AttributeError:
        qna_id = query_knowledgebase_options.get("qna_id") or query_knowledgebase_options.get("qnaId")
        question = query_knowledgebase_options.get("question")
    if not (qna_id or question):
        raise TypeError("You need to pass in either `qna_id` or `question`.")
    if qna_id and question:
        raise TypeError("You can not specify both `qna_id` and `question`.")


def _handle_metadata_filter_conversion(options_input):
    options = copy.deepcopy(options_input)
    filters = options.filters if hasattr(options, "filters") else options.get("filters", {})
    try:
        if filters and filters.metadata_filter and filters.metadata_filter.metadata:
            metadata_input = filters.metadata_filter.metadata
        else:
            metadata_input = None
        in_class = True
    except AttributeError:
        metadata_input = filters.get("metadataFilter", {}).get("metadata")
        in_class = False
    if not metadata_input:
        return options
    try:
        if any(t for t in metadata_input if len(t) != 2):
            raise ValueError("'metadata' must be a sequence of key-value tuples.")
    except TypeError:
        raise ValueError("'metadata' must be a sequence of key-value tuples.")

    metadata_modified = [{"key": m[0], "value": m[1]} for m in metadata_input]
    if in_class:
        filters.metadata_filter.metadata = metadata_modified
    else:
        filters["metadataFilter"]["metadata"] = metadata_modified
    return options
