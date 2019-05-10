# -------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# --------------------------------------------------------------------------

from enum import Enum


class BlobType(str, Enum):

    BlockBlob = "blockblob"
    PageBlob = "pageblob"
    AppendBlob = "appendblob"


class BlockState(str, Enum):
    """Block blob block types."""

    Committed = 'Committed'  #: Committed blocks.
    Latest = 'Latest'  #: Latest blocks.
    Uncommitted = 'Uncommitted'  #: Uncommitted blocks.


class StandardBlobTier(str, Enum):
    """
    Specifies the blob tier to set the blob to. This is only applicable for
    block blobs on standard storage accounts.
    """

    Archive = 'Archive'  #: Archive
    Cool = 'Cool'  #: Cool
    Hot = 'Hot'  #: Hot


class PremiumPageBlobTier(str, Enum):
    """
    Specifies the page blob tier to set the blob to. This is only applicable to page
    blobs on premium storage accounts. Please take a look at:
    https://docs.microsoft.com/en-us/azure/storage/storage-premium-storage#scalability-and-performance-targets
    for detailed information on the corresponding IOPS and throughtput per PageBlobTier.
    """

    P4 = 'P4'  #: P4 Tier
    P6 = 'P6'  #: P6 Tier
    P10 = 'P10'  #: P10 Tier
    P20 = 'P20'  #: P20 Tier
    P30 = 'P30'  #: P30 Tier
    P40 = 'P40'  #: P40 Tier
    P50 = 'P50'  #: P50 Tier
    P60 = 'P60'  #: P60 Tier


class SequenceNumberAction(str, Enum):
    """Sequence number actions."""

    Increment = 'increment'
    """
    Increments the value of the sequence number by 1. If specifying this option,
    do not include the x-ms-blob-sequence-number header.
    """

    Max = 'max'
    """
    Sets the sequence number to be the higher of the value included with the
    request and the value currently stored for the blob.
    """

    Update = 'update'
    """Sets the sequence number to the value included with the request."""
