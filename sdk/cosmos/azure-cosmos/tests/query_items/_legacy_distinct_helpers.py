# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
"""Self-contained DISTINCT helpers copied from tests/test_config.py."""

import collections


class DistinctConfig:
    @classmethod
    def _get_query_result_string(cls, query_result, fields):
        if type(query_result) is not dict:
            return str(query_result)
        res = str(query_result[fields[0]] if fields[0] in query_result else None)
        if len(fields) == 2:
            res = res + "," + str(query_result[fields[1]] if fields[1] in query_result else None)

        return res

    @classmethod
    async def _validate_distinct(cls, created_collection, query, results, is_select, fields):
        query_iterable = created_collection.query_items(query=query)
        query_results = [item async for item in query_iterable]

        assert len(results) == len(query_results)
        query_results_strings = []
        result_strings = []
        for i in range(len(results)):
            query_results_strings.append(cls._get_query_result_string(query_results[i], fields))
            result_strings.append(str(results[i]))
        if is_select:
            query_results_strings = sorted(query_results_strings)
            result_strings = sorted(result_strings)
        assert result_strings == query_results_strings

    @classmethod
    def _pad_with_none(cls, documents_param, field):
        for doc in documents_param:
            if field not in doc:
                doc[field] = None
        return documents_param

    @classmethod
    def _get_distinct_docs(cls, documents_param, field1, field2, is_order_by_or_value):
        if field2 is None:
            res = collections.OrderedDict.fromkeys(doc[field1] for doc in documents_param)
            if is_order_by_or_value:
                res = filter(lambda x: False if x is None else True, res)
        else:
            res = collections.OrderedDict.fromkeys(str(doc[field1]) + "," + str(doc[field2]) for doc in documents_param)
        return list(res)
