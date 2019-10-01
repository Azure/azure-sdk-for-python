#-------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
#--------------------------------------------------------------------------

import abc
try:
    from abc import ABC
except ImportError:
    # python <= 2.7
    from abc import ABCMeta
    class ABC(object):
        __metaclass__ = ABCMeta


class IInkPoint(ABC):
    """
    Interface for an InkPoint. An InkPoint represents a single position on the
    path of an ink stroke. Clients of the Ink Recognizer Service can implement
    this interface to store points in InkStroke instances.
    """

    @abc.abstractproperty
    def x(self):
        """ X-axis coordinate of the point. Should be float. """

    @abc.abstractproperty
    def y(self):
        """ Y-axis coordinate of the point. Should be float. """


class IInkStroke(ABC):
    """
    Interface of InkStroke. An InkStroke represents an ink stroke: a collection
    of IInkPoints from the time user places his writing instrument on the writing
    surface until the the instrument is lifted.
    Clients of the Ink Recognizer Service can implement this interface. An
    InkRecognizerClient instance accepts an iterable of IInkStroke instances,
    translate them to JSON and deliver to the Ink Recognizer Service.
    """
    @abc.abstractproperty
    def id(self):
        """ An integer stroke id. The numerical order (ascending) of stroke
        ids indicates the order of strokes.
        For example, there are three strokes s_0, s_1, s_2, where
        s_0.id = 0, s_1.id = 1, s_2.id = 2.
        No matter what order they are sent into InkRecognizerClient, they will
        be re-ordered as (s_0, s_1, s_2) when doing ink recognition.

        :rtype: int
        """

    @abc.abstractproperty
    def points(self):
        """ An iterable of <IInkPoint> of this stroke.

        :rtype: List[IInkPoint]
        """

    @abc.abstractproperty
    def kind(self):
        """
        InkStrokeKind of the stroke.

        :rtype: InkStrokeKind
        """

    @abc.abstractproperty
    def language(self):
        """
        IETF BCP-47 language code (e.g. "en-US") of the stroke.

        :rtype: str
        """
        