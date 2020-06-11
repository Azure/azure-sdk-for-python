# -*- coding: UTF-8 -*-
"""
Provides a summary after each test run.
"""

from __future__ import absolute_import, division
import sys
from behave.model import ScenarioOutline
from behave.model_core import Status
from behave.reporter.base import Reporter
from behave.formatter.base import StreamOpener


# -- DISABLED: optional_steps = ('untested', 'undefined')
optional_steps = (Status.untested,) # MAYBE: Status.undefined
status_order = (Status.passed, Status.failed, Status.skipped,
                Status.undefined, Status.untested)

def format_summary(statement_type, summary):
    parts = []
    for status in status_order:
        if status.name not in summary:
            continue
        counts = summary[status.name]
        if status in optional_steps and counts == 0:
            # -- SHOW-ONLY: For relevant counts, suppress: untested items, etc.
            continue

        if not parts:
            # -- FIRST ITEM: Add statement_type to counter.
            label = statement_type
            if counts != 1:
                label += 's'
            part = u"%d %s %s" % (counts, label, status.name)
        else:
            part = u"%d %s" % (counts, status.name)
        parts.append(part)
    return ", ".join(parts) + "\n"


class SummaryReporter(Reporter):
    show_failed_scenarios = True
    output_stream_name = "stdout"

    def __init__(self, config):
        super(SummaryReporter, self).__init__(config)
        stream = getattr(sys, self.output_stream_name, sys.stderr)
        self.stream = StreamOpener.ensure_stream_with_encoder(stream)
        self.feature_summary = {Status.passed.name: 0, Status.failed.name: 0,
                                Status.skipped.name: 0, Status.untested.name: 0}
        self.scenario_summary = {Status.passed.name: 0, Status.failed.name: 0,
                                 Status.skipped.name: 0, Status.untested.name: 0}
        self.step_summary = {Status.passed.name: 0, Status.failed.name: 0,
                             Status.skipped.name: 0, Status.untested.name: 0,
                             Status.undefined.name: 0}
        self.duration = 0.0
        self.failed_scenarios = []

    def feature(self, feature):
        self.feature_summary[feature.status.name] += 1
        self.duration += feature.duration
        for scenario in feature:
            if isinstance(scenario, ScenarioOutline):
                self.process_scenario_outline(scenario)
            else:
                self.process_scenario(scenario)

    def end(self):
        # -- SHOW FAILED SCENARIOS (optional):
        if self.show_failed_scenarios and self.failed_scenarios:
            self.stream.write("\nFailing scenarios:\n")
            for scenario in self.failed_scenarios:
                self.stream.write(u"  %s  %s\n" % (
                    scenario.location, scenario.name))
            self.stream.write("\n")

        # -- SHOW SUMMARY COUNTS:
        self.stream.write(format_summary("feature", self.feature_summary))
        self.stream.write(format_summary("scenario", self.scenario_summary))
        self.stream.write(format_summary("step", self.step_summary))
        timings = (int(self.duration / 60.0), self.duration % 60)
        self.stream.write('Took %dm%02.3fs\n' % timings)

    def process_scenario(self, scenario):
        if scenario.status == Status.failed:
            self.failed_scenarios.append(scenario)

        self.scenario_summary[scenario.status.name] += 1
        for step in scenario:
            self.step_summary[step.status.name] += 1

    def process_scenario_outline(self, scenario_outline):
        for scenario in scenario_outline.scenarios:
            self.process_scenario(scenario)
