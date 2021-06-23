
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from ._version import VERSION
from ._query_client import QuestionAnsweringClient
from ._author_client import KnowledgebaseAuthoringClient
from ._generated_query.models import (
    TextQueryParameters,
    TextAnswers,
    KnowledgebaseQueryParameters,
    KnowledgebaseAnswerRequestContext,
    RankerType,
    StrictFilters,
    AnswerSpanRequest,
    KnowledgebaseAnswers
)
from ._generated_author.models import (
    ProjectMetadata,
    CreateProjectParameters,
    ExportJobParameters,
    ImportJobParameters,
    Format,
)

__all__ = [
    'QuestionAnsweringClient',
    'KnowledgebaseAuthoringClient',
    'TextQueryParameters',
    'TextAnswers',
    'KnowledgebaseQueryParameters',
    'RankerType',
    'StrictFilters',
    'AnswerSpanRequest',
    'KnowledgebaseAnswers'
    'ProjectMetadata',
    'CreateProjectParameters',
    'ExportJobParameters',
    'ImportJobParameters',
    'Format'
]
__version__ = VERSION
