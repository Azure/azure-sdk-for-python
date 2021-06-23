
# coding: utf-8
# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------
from .._generated_query._rest import (
    question_answering_knowledgebase,
    question_answering_text
)
from .._generated_author.rest import question_answering_projects

__all__ = [
    'question_answering_text',
    'question_answering_knowledgebase',
    'question_answering_projects'
]
