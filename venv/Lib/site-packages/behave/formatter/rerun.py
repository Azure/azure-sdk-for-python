# -*- coding: utf-8 -*-
"""
Provides a formatter that simplifies to rerun the failing scenarios
of the last test run. It writes a text file with the file locations of
the failing scenarios, like:

    # -- file:rerun.features
    # RERUN: Failing scenarios during last test run.
    features/alice.feature:10
    features/alice.feature:42
    features/bob.feature:67

To rerun the failing scenarios, use:

    behave @rerun_failing.features

Normally, you put the RerunFormatter into the behave configuration file:

    # -- file:behave.ini
    [behave]
    format   = rerun
    outfiles = rerun_failing.features
"""

from __future__ import absolute_import
from datetime import datetime
from os.path import relpath
import os
from behave.formatter.base import Formatter
from behave.model_core import Status


# -----------------------------------------------------------------------------
# CLASS: RerunFormatter
# -----------------------------------------------------------------------------
class RerunFormatter(Formatter):
    """
    Provides formatter class that emits a summary which scenarios failed
    during the last test run. This output can be used to rerun the tests
    with the failed scenarios.
    """
    name = "rerun"
    description = "Emits scenario file locations of failing scenarios"

    show_timestamp = False
    show_failed_scenarios_descriptions = False

    def __init__(self, stream_opener, config):
        super(RerunFormatter, self).__init__(stream_opener, config)
        self.failed_scenarios = []
        self.current_feature = None

    def reset(self):
        self.failed_scenarios = []
        self.current_feature = None

    # -- FORMATTER API:
    def feature(self, feature):
        self.current_feature = feature

    def eof(self):
        """Called at end of a feature."""
        if self.current_feature and self.current_feature.status == Status.failed:
            # -- COLLECT SCENARIO FAILURES:
            for scenario in self.current_feature.walk_scenarios():
                if scenario.status == Status.failed:
                    self.failed_scenarios.append(scenario)

        # -- RESET:
        self.current_feature = None
        assert self.current_feature is None

    def close(self):
        """Called at end of test run."""
        stream_name = self.stream_opener.name
        if self.failed_scenarios:
            # -- ENSURE: Output stream is open.
            self.stream = self.open()
            self.report_scenario_failures()
        elif stream_name and os.path.exists(stream_name):
            # -- ON SUCCESS: Remove last rerun file with its failures.
            os.remove(self.stream_opener.name)

        # -- FINALLY:
        self.close_stream()

    # -- SPECIFIC-API:
    def report_scenario_failures(self):
        assert self.failed_scenarios
        # -- SECTION: Banner
        message = u"# -- RERUN: %d failing scenarios during last test run.\n"
        self.stream.write(message % len(self.failed_scenarios))
        if self.show_timestamp:
            now = datetime.now().replace(microsecond=0)
            self.stream.write("# NOW: %s\n"% now.isoformat(" "))

        # -- SECTION: Textual summary in comments.
        if self.show_failed_scenarios_descriptions:
            current_feature = None
            for index, scenario in enumerate(self.failed_scenarios):
                if current_feature != scenario.filename:
                    if current_feature is not None:
                        self.stream.write(u"#\n")
                    current_feature = scenario.filename
                    short_filename = relpath(scenario.filename, os.getcwd())
                    self.stream.write(u"# %s\n" % short_filename)
                self.stream.write(u"#  %4d:  %s\n" % \
                                  (scenario.line, scenario.name))
            self.stream.write("\n")

        # -- SECTION: Scenario file locations, ala: "alice.feature:10"
        for scenario in self.failed_scenarios:
            self.stream.write(u"%s\n" % scenario.location)
        self.stream.write("\n")
