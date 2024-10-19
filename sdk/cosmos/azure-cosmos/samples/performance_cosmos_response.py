import json
import uuid
import random
import timeit
from decimal import Decimal
from typing import Any, Dict, Iterable, Mapping
from azure.core.utils import CaseInsensitiveDict

class CosmosDictResponse(dict):
    def __init__(self, original_dict: Mapping[str, Any], /, *, response_headers: CaseInsensitiveDict) -> None:
        if original_dict is None:
            original_dict = {}
        super().__init__(original_dict)
        self._response_headers = response_headers

    @property
    def response_headers(self) -> CaseInsensitiveDict:
        """Returns the response headers associated to this result

        :return: Dict of response headers
        :rtype: ~azure.core.CaseInsensitiveDict
        """
        return self._response_headers


class CosmosListResponse(list):
    def __init__(self, original_list: Iterable[Dict[str, Any]], /, *,
                 response_headers: CaseInsensitiveDict) -> None:
        if original_list is None:
            original_list = []
        super().__init__(original_list)
        self._response_headers = response_headers

    @property
    def response_headers(self) -> CaseInsensitiveDict:
        """Returns the response headers associated to this result

        :return: Dict of response headers
        :rtype: ~azure.core.CaseInsensitiveDict
        """
        return self._response_headers


def get_small_item():
    item = {"id": str(uuid.uuid4()),
            "property": "something",
            "value": random.randint(0, 1000000)}
    return item


def get_nested_item():
    item = {"id": str(uuid.uuid4()),
            "property": "something",
            "value": random.randint(0, 1000000),
            "address": {
                "country": "USA",
                "state": "Georgia",
                "city": "Atlanta",
                "zipcode": 30313,
                "street": {
                    "name": "some_street",
                    "number": 3333
                }
            },
            "phone_number": "123456789",
            "username": "",
            "company": "Microsoft"
            }
    return item


def get_vector():
    vector = []
    for i in range(1000):
        vector.append(round(random.uniform(0, 1), 6))
    return vector


def get_vector_item():
    item = get_nested_item()
    item['vector'] = get_vector()
    return item


headers = {'Content-Length': '1371','Date': 'Wed, 31 Jul 2024 21:07:56 GMT','Content-Type': 'application/json',
            'Server': 'Compute','x-ms-gatewayversion': '2.0.0','x-ms-activity-id': '0ffd6fba-297b-4ac9-a65a-3da7e1e6jd19',
            'x-ms-last-state-change-utc': 'Wed, 31 Jul 2024 15:35:22.506 GMT',
            'x-ms-continuation': '[{"token":"-RID:~BZ9XAOSxDKmEhB4AAAAABA==#RT:1#TRC:4#ISV:2#IEO:65567#QCF:8","range":{"min":"0FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF","max":"1FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFE"}}]',
            'x-ms-resource-quota': 'documentSize=51200;documentsSize=52428800;documentsCount=-1;collectionSize=52428800;',
            'x-ms-resource-usage': 'documentSize=0;documentsSize=0;documentsCount=5;collectionSize=0;',
            'x-ms-schemaversion': '1.18', 'lsn': '6', 'x-ms-item-count': '4', 'x-ms-request-charge': '2.31',
            'x-ms-alt-content-path': 'dbs/63134e99-3ca5-4244-bee7-70d5f4d4249d/colls/af0a40ca-97c2-45d4-a698-0248462e1899',
            'x-ms-content-path': 'BZ9XAOSxDKk=', 'x-ms-documentdb-partitionkeyrangeid': '1', 'x-ms-xp-role': '1',
            'x-ms-cosmos-query-execution-info': '{"reverseRidEnabled":false,"reverseIndexScan":false}',
            'x-ms-global-Committed-lsn': '6', 'x-ms-number-of-read-regions': '1', 'x-ms-transport-request-id': '2',
            'x-ms-cosmos-llsn': '6', 'x-ms-session-token': '1:0#6#7=-1', 'x-ms-request-duration-ms': '0.408',
            'x-ms-serviceversion': 'version=2.14.0.0', 'x-ms-cosmos-is-partition-key-delete-pending': 'false',
            'x-ms-cosmos-physical-partition-id': '1', 'x-ms-throttle-retry-count': '0', 'x-ms-throttle-retry-wait-time-ms': '0'}
case_insensitive_headers = CaseInsensitiveDict(headers)
vector_item = get_vector_item()
nest_item = get_nested_item()
small_item = get_small_item()
list_items = []
for i in range(100):
    list_items.append(get_nested_item())
small_serialized = CosmosDictResponse(small_item, response_headers=case_insensitive_headers)
vector_serialized = CosmosDictResponse(vector_item, response_headers=case_insensitive_headers)
nest_serialized = CosmosDictResponse(nest_item, response_headers=case_insensitive_headers)
list_serialized = CosmosListResponse(list_items, response_headers=case_insensitive_headers)



def serialize_nested():
    return CosmosDictResponse(nest_item, response_headers=case_insensitive_headers)
def baseline_nested():
    return nest_item
def serialize_small():
    return CosmosDictResponse(small_item, response_headers=case_insensitive_headers)
def baseline_small():
    return small_item
def serialize_vector():
    return CosmosDictResponse(vector_item, response_headers=case_insensitive_headers)
def baseline_vector():
    return vector_item
def serialize_list():
    return CosmosListResponse(list_items, response_headers=case_insensitive_headers)
def baseline_list():
    return list_items
def response_json_dump():
    return json.dumps(nest_serialized)
def baseline_json_dump():
    return json.dumps(nest_item)
def response_value_set():
    nest_serialized['new_value'] = "new_value"
    return nest_serialized
def baseline_value_set():
    nest_item['new_value'] = "new_value"
    return nest_item
def response_access():
    return nest_serialized['address']
def baseline_access():
    return nest_item['address']
def response_keys():
    return nest_serialized.keys()
def baseline_keys():
    return nest_item.keys()
def response_values():
    return nest_serialized.values()
def baseline_values():
    return nest_item.values()
def response_items():
    return nest_serialized.items()
def baseline_items():
    return nest_item.items()
def response_dict_comprehension():
    return dict(nest_serialized)
def baseline_dict_comprehension():
    return dict(nest_item)
def response_list_comprehension():
    return list(list_serialized)
def baseline_list_comprehension():
    return list(list_items)


def check_times():
    time_1 = timeit.timeit("baseline_small()", globals=globals(), number=1000)
    time_2 = timeit.timeit("serialize_small()", globals=globals(), number=1000)
    time_3 = timeit.timeit("baseline_nested()", globals=globals(), number=1000)
    time_4 = timeit.timeit("serialize_nested()", globals=globals(), number=1000)
    time_5 = timeit.timeit("baseline_vector()", globals=globals(), number=1000)
    time_6 = timeit.timeit("serialize_vector()", globals=globals(), number=1000)
    time_7 = timeit.timeit("baseline_list()", globals=globals(), number=1000)
    time_8 = timeit.timeit("serialize_list()", globals=globals(), number=1000)
    time_9 = timeit.timeit("baseline_json_dump()", globals=globals(), number=1000)
    time_10 = timeit.timeit("response_json_dump()", globals=globals(), number=1000)
    time_11 = timeit.timeit("baseline_value_set()", globals=globals(), number=1000)
    time_12 = timeit.timeit("response_value_set()", globals=globals(), number=1000)
    time_13 = timeit.timeit("baseline_access()", globals=globals(), number=1000)
    time_14 = timeit.timeit("response_access()", globals=globals(), number=1000)
    time_15 = timeit.timeit("baseline_keys()", globals=globals(), number=1000)
    time_16 = timeit.timeit("response_keys()", globals=globals(), number=1000)
    time_17 = timeit.timeit("baseline_values()", globals=globals(), number=1000)
    time_18 = timeit.timeit("response_values()", globals=globals(), number=1000)
    time_19 = timeit.timeit("baseline_items()", globals=globals(), number=1000)
    time_20 = timeit.timeit("response_items()", globals=globals(), number=1000)
    time_21 = timeit.timeit("baseline_dict_comprehension()", globals=globals(), number=1000)
    time_22 = timeit.timeit("response_dict_comprehension()", globals=globals(), number=1000)
    time_23 = timeit.timeit("baseline_list_comprehension()", globals=globals(), number=1000)
    time_24 = timeit.timeit("response_list_comprehension()", globals=globals(), number=1000)

    print("---------  EXECUTION TIMES  -----------")
    print(f"Execution time of baseline_small: {Decimal(time_1)} seconds")
    print(f"Execution time of serialize_small: {Decimal(time_2)} seconds")
    print("-------------------------------------------------------------")
    print(f"Execution time of baseline_nested: {Decimal(time_3)} seconds")
    print(f"Execution time of serialize_nested: {Decimal(time_4)} seconds")
    print("-------------------------------------------------------------")
    print(f"Execution time of baseline_vector: {Decimal(time_5)} seconds")
    print(f"Execution time of serialize_vector: {Decimal(time_6)} seconds")
    print("-------------------------------------------------------------")
    print(f"Execution time of baseline_list: {Decimal(time_7)} seconds")
    print(f"Execution time of serialize_list: {Decimal(time_8)} seconds")
    print("-------------------------------------------------------------")
    print(f"Execution time of baseline_json_dump: {Decimal(time_9)} seconds")
    print(f"Execution time of response_json_dump: {Decimal(time_10)} seconds")
    print("-------------------------------------------------------------")
    print(f"Execution time of baseline_value_set: {Decimal(time_11)} seconds")
    print(f"Execution time of response_value_set: {Decimal(time_12)} seconds")
    print("-------------------------------------------------------------")
    print(f"Execution time of baseline_access: {Decimal(time_13)} seconds")
    print(f"Execution time of response_access: {Decimal(time_14)} seconds")
    print("-------------------------------------------------------------")
    print(f"Execution time of baseline_keys: {Decimal(time_15)} seconds")
    print(f"Execution time of response_keys: {Decimal(time_16)} seconds")
    print("-------------------------------------------------------------")
    print(f"Execution time of baseline_values: {Decimal(time_17)} seconds")
    print(f"Execution time of response_values: {Decimal(time_18)} seconds")
    print("-------------------------------------------------------------")
    print(f"Execution time of baseline_items: {Decimal(time_19)} seconds")
    print(f"Execution time of response_items: {Decimal(time_20)} seconds")
    print("-------------------------------------------------------------")
    print(f"Execution time of baseline_dict_comprehension: {Decimal(time_21)} seconds")
    print(f"Execution time of response_dict_comprehension: {Decimal(time_22)} seconds")
    print("-------------------------------------------------------------")
    print(f"Execution time of baseline_list_comprehension: {Decimal(time_23)} seconds")
    print(f"Execution time of response_list_comprehension: {Decimal(time_24)} seconds")
    print("-------------------------------------------------------------")


if __name__ == "__main__":
    check_times()
