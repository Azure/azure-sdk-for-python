# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from blinker import Namespace


cloudmachine_events = Namespace()

FILE_UPLOADED = cloudmachine_events.signal('Microsoft.Storage.BlobCreated')
FILE_DELETED = cloudmachine_events.signal('Microsoft.Storage.BlobDeleted')
FILE_RENAMED = cloudmachine_events.signal('Microsoft.Storage.BlobRenamed')
