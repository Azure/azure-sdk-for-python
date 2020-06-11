# -*- coding: utf-8 -*-
"""
Read behave's JSON output files and store retrieved information in
:mod:`behave.model` elements.

Utility to retrieve runtime information from behave's JSON output.

REQUIRES: Python >= 2.6 (json module is part of Python standard library)
"""

from __future__ import absolute_import
import codecs
from behave import model
from behave.model_core import Status
try:
    import json
except ImportError:
    # -- PYTHON 2.5 backward compatible: Use simplejson module.
    import simplejson as json


__author__ = "Jens Engel"


# ----------------------------------------------------------------------------
# FUNCTIONS:
# ----------------------------------------------------------------------------
def parse(json_filename, encoding="UTF-8"):
    """
    Reads behave JSON output file back in and stores information in
    behave model elements.

    :param json_filename:  JSON filename to process.
    :return: List of feature objects.
    """
    with codecs.open(json_filename, "rU", encoding=encoding) as input_file:
        json_data = json.load(input_file, encoding=encoding)
        json_processor = JsonParser()
        features = json_processor.parse_features(json_data)
        return features


# ----------------------------------------------------------------------------
# CLASSES:
# ----------------------------------------------------------------------------
class JsonParser(object):

    def __init__(self):
        self.current_scenario_outline = None

    def parse_features(self, json_data):
        assert isinstance(json_data, list)
        features = []
        json_features = json_data
        for json_feature in json_features:
            feature = self.parse_feature(json_feature)
            features.append(feature)
        return features

    def parse_feature(self, json_feature):
        name = json_feature.get("name", u"")
        keyword = json_feature.get("keyword", None)
        tags = json_feature.get("tags", [])
        description = json_feature.get("description", [])
        location = json_feature.get("location", u"")
        filename, line = location.split(":")
        feature = model.Feature(filename, line, keyword, name, tags, description)

        json_elements = json_feature.get("elements", [])
        for json_element in json_elements:
            self.add_feature_element(feature, json_element)
        return feature


    def add_feature_element(self, feature, json_element):
        datatype = json_element.get("type", u"")
        category = datatype.lower()
        if category == "background":
            background = self.parse_background(json_element)
            feature.background = background
        elif category == "scenario":
            scenario = self.parse_scenario(json_element)
            feature.add_scenario(scenario)
        elif category == "scenario_outline":
            scenario_outline = self.parse_scenario_outline(json_element)
            feature.add_scenario(scenario_outline)
            self.current_scenario_outline = scenario_outline
        # elif category == "examples":
        #     examples = self.parse_examples(json_element)
        #     self.current_scenario_outline.examples = examples
        else:
            raise KeyError("Invalid feature-element keyword: %s" % category)


    def parse_background(self, json_element):
        """
        self.add_feature_element({
            'keyword': background.keyword,
            'location': background.location,
            'steps': [],
        })
        """
        keyword = json_element.get("keyword", u"")
        name = json_element.get("name", u"")
        location = json_element.get("location", u"")
        json_steps = json_element.get("steps", [])
        steps = self.parse_steps(json_steps)
        filename, line = location.split(":")
        background = model.Background(filename, line, keyword, name, steps)
        return background

    def parse_scenario(self, json_element):
        """
        self.add_feature_element({
            'keyword': scenario.keyword,
            'name': scenario.name,
            'tags': scenario.tags,
            'location': scenario.location,
            'steps': [],
        })
        """
        keyword = json_element.get("keyword", u"")
        name = json_element.get("name", u"")
        description = json_element.get("description", [])
        tags = json_element.get("tags", [])
        location = json_element.get("location", u"")
        json_steps = json_element.get("steps", [])
        steps = self.parse_steps(json_steps)
        filename, line = location.split(":")
        scenario = model.Scenario(filename, line, keyword, name, tags, steps)
        scenario.description = description
        return scenario

    def parse_scenario_outline(self, json_element):
        """
        self.add_feature_element({
            'keyword': scenario_outline.keyword,
            'name': scenario_outline.name,
            'tags': scenario_outline.tags,
            'location': scenario_outline.location,
            'steps': [],
            'examples': [],
        })
        """
        keyword = json_element.get("keyword", u"")
        name = json_element.get("name", u"")
        description = json_element.get("description", [])
        tags = json_element.get("tags", [])
        location = json_element.get("location", u"")
        json_steps = json_element.get("steps", [])
        json_examples = json_element.get("examples", [])
        steps = self.parse_steps(json_steps)
        examples = []
        if json_examples:
            # pylint: disable=redefined-variable-type
            examples = self.parse_examples(json_examples)
        filename, line = location.split(":")
        scenario_outline = model.ScenarioOutline(filename, line, keyword, name,
                                                 tags=tags, steps=steps,
                                                 examples=examples)
        scenario_outline.description = description
        return scenario_outline

    def parse_steps(self, json_steps):
        steps = []
        for json_step in json_steps:
            step = self.parse_step(json_step)
            steps.append(step)
        return steps

    def parse_step(self, json_element):
        """
        s = {
            'keyword': step.keyword,
            'step_type': step.step_type,
            'name': step.name,
            'location': step.location,
        }

        if step.text:
            s['text'] = step.text
        if step.table:
            s['table'] = self.make_table(step.table)
        element = self.current_feature_element
        element['steps'].append(s)
        """
        keyword = json_element.get("keyword", u"")
        name = json_element.get("name", u"")
        step_type = json_element.get("step_type", u"")
        location = json_element.get("location", u"")
        text = json_element.get("text", None)
        if isinstance(text, list):
            text = "\n".join(text)
        table = None
        json_table = json_element.get("table", None)
        if json_table:
            table = self.parse_table(json_table)
        filename, line = location.split(":")
        step = model.Step(filename, line, keyword, step_type, name)
        step.text = text
        step.table = table
        json_result = json_element.get("result", None)
        if json_result:
            self.add_step_result(step, json_result)
        return step

    @staticmethod
    def add_step_result(step, json_result):
        """
        steps = self.current_feature_element['steps']
        steps[self._step_index]['result'] = {
            'status': result.status.name,
            'duration': result.duration,
        }
        """
        status_name = json_result.get("status", u"")
        duration = json_result.get("duration", 0)
        error_message = json_result.get("error_message", None)
        if isinstance(error_message, list):
            error_message = "\n".join(error_message)
        step.status = Status.from_name(status_name)
        step.duration = duration
        step.error_message = error_message

    @staticmethod
    def parse_table(json_table):
        """
        table_data = {
            'headings': table.headings,
            'rows': [ list(row) for row in table.rows ]
        }
        return table_data
        """
        headings = json_table.get("headings", [])
        rows = json_table.get("rows", [])
        table = model.Table(headings, rows=rows)
        return table


    def parse_examples(self, json_element):
        """
        e = {
            'keyword': examples.keyword,
            'name': examples.name,
            'location': examples.location,
        }

        if examples.table:
            e['table'] = self.make_table(examples.table)

        element = self.current_feature_element
        element['examples'].append(e)
        """
        keyword = json_element.get("keyword", u"")
        name = json_element.get("name", u"")
        location = json_element.get("location", u"")

        table = None
        json_table = json_element.get("table", None)
        if json_table:
            table = self.parse_table(json_table)
        filename, line = location.split(":")
        examples = model.Examples(filename, line, keyword, name, table)
        return examples
