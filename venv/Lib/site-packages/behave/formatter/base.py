# -*- coding: utf-8 -*-

# UNUSED: import sys
# UNUSED: import codecs
import os.path
from behave.textutil import select_best_encoding, \
    ensure_stream_with_encoder as _ensure_stream_with_encoder


class StreamOpener(object):
    """Provides a transport vehicle to open the formatter output stream
    when the formatter needs it.
    In addition, it provides the formatter with more control:

      * when a stream is opened
      * if a stream is opened at all
      * the name (filename/dirname) of the output stream
      * let it decide if directory mode is used instead of file mode
    """
    # FORMER: default_encoding = "UTF-8"
    default_encoding = select_best_encoding()

    def __init__(self, filename=None, stream=None, encoding=None):
        if not encoding:
            encoding = self.default_encoding
        if stream:
            stream = self.ensure_stream_with_encoder(stream, encoding)
        self.name = filename
        self.stream = stream
        self.encoding = encoding
        self.should_close_stream = not stream   # Only for not pre-opened ones.

    @staticmethod
    def ensure_dir_exists(directory):
        if directory and not os.path.isdir(directory):
            os.makedirs(directory)

    @classmethod
    def ensure_stream_with_encoder(cls, stream, encoding=None):
        return _ensure_stream_with_encoder(stream, encoding)

    def open(self):
        if not self.stream or self.stream.closed:
            self.ensure_dir_exists(os.path.dirname(self.name))
            stream = open(self.name, "w")
            # stream = codecs.open(self.name, "w", encoding=self.encoding)
            stream = self.ensure_stream_with_encoder(stream, self.encoding)
            self.stream = stream  # -- Keep stream for house-keeping.
            self.should_close_stream = True
            assert self.should_close_stream
        return self.stream

    def close(self):
        """
        Close the stream, if it was opened by this stream_opener.
        Skip closing for sys.stdout and pre-opened streams.
        :return: True, if stream was closed.
        """
        closed = False
        if self.stream and self.should_close_stream:
            closed = getattr(self.stream, "closed", False)
            if not closed:
                self.stream.close()
                closed = True
            self.stream = None
        return closed


class Formatter(object):
    """
    Base class for all formatter classes.
    A formatter is an extension point (variation point) for the runner logic.
    A formatter is called while processing model elements.

    Processing Logic (simplified, without ScenarioOutline and skip logic)::

        for feature in runner.features:
            formatter = make_formatters(...)
            formatter.uri(feature.filename)
            formatter.feature(feature)
            for scenario in feature.scenarios:
                formatter.scenario(scenario)
                for step in scenario.all_steps:
                    formatter.step(step)
                    step_match = step_registry.find_match(step)
                    formatter.match(step_match)
                    if step_match:
                        step_match.run()
                    else:
                        step.status = Status.undefined
                    formatter.result(step.status)
            formatter.eof() # -- FEATURE-END
        formatter.close()
    """
    name = None
    description = None

    def __init__(self, stream_opener, config):
        self.stream_opener = stream_opener
        self.stream = stream_opener.stream
        self.config = config

    @property
    def stdout_mode(self):
        return not self.stream_opener.name

    def open(self):
        """
        Ensure that the output stream is open.
        Triggers the stream opener protocol (if necessary).

        :return: Output stream to use (just opened or already open).
        """
        if not self.stream:
            self.stream = self.stream_opener.open()
        return self.stream

    def uri(self, uri):
        """Called before processing a file (normally a feature file).

        :param uri:  URI or filename (as string).
        """
        pass

    def feature(self, feature):
        """Called before a feature is executed.

        :param feature:  Feature object (as :class:`behave.model.Feature`)
        """
        pass

    def background(self, background):
        """Called when a (Feature) Background is provided.
        Called after :method:`feature()` is called.
        Called before processing any scenarios or scenario outlines.

        :param background:  Background object (as :class:`behave.model.Background`)
        """
        pass

    def scenario(self, scenario):
        """Called before a scenario is executed (or ScenarioOutline scenarios).

        :param scenario:  Scenario object (as :class:`behave.model.Scenario`)
        """
        pass

    def step(self, step):
        """Called before a step is executed (and matched).
        NOTE: Normally called before scenario is executed for all its steps.

        :param step: Step object (as :class:`behave.model.Step`)
        """
        pass

    def match(self, match):
        """Called when a step was matched against its step implementation.

        :param match:  Registered step (as Match), undefined step (as NoMatch).
        """
        pass

    def result(self, step):
        """Called after processing a step (when the step result is known).

        :param step:  Step object with result (after being executed/skipped).
        """
        pass

    def eof(self):
        """Called after processing a feature (or a feature file)."""
        pass

    def close(self):
        """Called before the formatter is no longer used
        (stream/io compatibility).
        """
        self.close_stream()

    def close_stream(self):
        """Close the stream, but only if this is needed.
        This step is skipped if the stream is sys.stdout.
        """
        if self.stream:
            # -- DELEGATE STREAM-CLOSING: To stream_opener
            assert self.stream is self.stream_opener.stream
            self.stream_opener.close()
        self.stream = None      # -- MARK CLOSED.
