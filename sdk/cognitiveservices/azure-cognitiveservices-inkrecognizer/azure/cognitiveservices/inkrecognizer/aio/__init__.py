#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import platform
if platform.python_version() < "3.5.3":
    raise ImportError("Asynchronous client supports Python 3.5.3+ only.")

from .._enums import (  # pylint:disable=wrong-import-position
    ApplicationKind,
    InkPointUnit,
    InkRecognitionUnitKind,
    ShapeKind,
    InkStrokeKind,
    ServiceVersion
)
from ._client_async import InkRecognizerClient  # pylint:disable=wrong-import-position
from .._ink_stroke import (  # pylint:disable=wrong-import-position
    IInkPoint,
    IInkStroke
)
from .._models import (  # pylint:disable=wrong-import-position
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
from .._version import VERSION  # pylint:disable=wrong-import-position

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
