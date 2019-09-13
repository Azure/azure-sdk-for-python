#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import platform
if platform.python_version() < "3.5.3":
    raise ImportError("Asynchronous client supports Python 3.5.3+ only.")

from .._enums import (
    ApplicationKind,
    InkPointUnit,
    InkRecognitionUnitKind,
    ShapeKind,
    InkStrokeKind,
    ServiceVersion
)
from ._client_async import InkRecognizerClient
from .._ink_stroke import (
    IInkPoint,
    IInkStroke
)
from .._models import (
    Point,
    Rectangle,
    InkRecognitionUnit,
    InkBullet,
    InkDrawing,
    Line,
    Paragraph,
    InkWord,
    WritingRegion,
    ListItem,
    InkRecognitionRoot
)
from .._version import VERSION

__all__ = [
    #enums
    "ApplicationKind",
    "InkPointUnit",
    "InkRecognitionUnitKind",
    "ShapeKind",
    "InkStrokeKind",
    "ServiceVersion",
    # client
    "InkRecognizerClient",
    # interfaces
    "IInkPoint",
    "IInkStroke",
    # models
    "Point",
    "Rectangle",
    "InkRecognitionUnit",
    "InkBullet",
    "InkDrawing",
    "Line",
    "Paragraph",
    "InkWord",
    "WritingRegion",
    "ListItem",
    "InkRecognitionRoot"
]

__version__ = VERSION
