# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

VERSION = "12.2.0"

_API_VERSION_PARAMETER_COMPATIBILITY = {
    'create_append_blob': {'2019-07-07': 'cpk_scope_info'},
    'append_block': {'2019-07-07': 'cpk_scope_info'},
    'append_block_from_url': {'2019-07-07': 'cpk_scope_info'},
    'create_page_blob': {'2019-07-07': 'cpk_scope_info'},
    'upload_page': {'2019-07-07': 'cpk_scope_info'},
    'upload_pages_from_url': {'2019-07-07': 'cpk_scope_info'},
    'clear_page': {'2019-07-07': 'cpk_scope_info'},
    'resize_blob': {'2019-07-07': 'cpk_scope_info'},
}