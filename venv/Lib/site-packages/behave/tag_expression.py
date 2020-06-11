# -*- coding: utf-8 -*-

import six

class TagExpression(object):
    """
    Tag expression, as logical boolean expression, to select
    (include or exclude) model elements.

    BOOLEAN LOGIC := (or_expr1) and (or_expr2) and ...
    with or_exprN := [not] tag1 or [not] tag2 or ...
    """

    def __init__(self, tag_expressions):
        self.ands = []
        self.limits = {}

        for expr in tag_expressions:
            self.store_and_extract_limits(self.normalized_tags_from_or(expr))

    @staticmethod
    def normalize_tag(tag):
        """
        Normalize a tag for a tag expression:

          * strip whitespace
          * strip '@' char
          * convert '~' (tilde) into '-' (minus sign)

        :param tag:  Tag (as string).
        :return: Normalized tag (as string).
        """
        tag = tag.strip()
        if tag.startswith('@'):
            tag = tag[1:]
        elif tag.startswith('-@') or tag.startswith('~@'):
            tag = '-' + tag[2:]
        elif tag.startswith('~'):
            tag = '-' + tag[1:]
        return tag

    @classmethod
    def normalized_tags_from_or(cls, expr):
        """
        Normalizes all tags in an OR expression (and return it as list).

        :param expr:  OR expression to normalize and split (as string).
        :return: Generator of normalized tags (as string)
        """
        for tag in expr.strip().split(','):
            yield cls.normalize_tag(tag)

    def store_and_extract_limits(self, tags):
        tags_with_negation = []

        for tag in tags:
            negated = tag.startswith('-')
            tag = tag.split(':')
            tag_with_negation = tag.pop(0)
            tags_with_negation.append(tag_with_negation)

            if tag:
                limit = int(tag[0])
                if negated:
                    tag_without_negation = tag_with_negation[1:]
                else:
                    tag_without_negation = tag_with_negation
                limited = tag_without_negation in self.limits
                if limited and self.limits[tag_without_negation] != limit:
                    msg = "Inconsistent tag limits for {0}: {1:d} and {2:d}"
                    msg = msg.format(tag_without_negation,
                                     self.limits[tag_without_negation], limit)
                    raise Exception(msg)
                self.limits[tag_without_negation] = limit

        if tags_with_negation:
            self.ands.append(tags_with_negation)

    def check(self, tags):
        """
        Checks if this tag expression matches the tags of a model element.

        :param tags:  List of tags of a model element.
        :return: True, if tag expression matches. False, otherwise.
        """
        if not self.ands:
            return True

        element_tags = set(tags)

        def test_tag(xtag):
            if xtag.startswith('-'): # -- or xtag.startswith('~'):
                return xtag[1:] not in element_tags
            return xtag in element_tags

        # -- EVALUATE: (or_expr1) and (or_expr2) and ...
        return all(any(test_tag(xtag) for xtag in ors)  for ors in self.ands)

    def __len__(self):
        return len(self.ands)

    def __str__(self):
        """Conversion back into string that represents this tag expression."""
        and_parts = []
        for or_terms in self.ands:
            and_parts.append(u",".join(or_terms))
        return u" ".join(and_parts)

    if six.PY2:
        __unicode__ = __str__
        __str__ = lambda self: self.__unicode__().encode("utf-8")
