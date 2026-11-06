# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import pytest
import os
import json
import pathlib
import random
from azure.ai.evaluation import evaluate
from azure.ai.evaluation._exceptions import EvaluationException, ErrorBlame, ErrorCategory, ErrorTarget
from azure.ai.evaluation._evaluators._document_retrieval import (
    DocumentRetrievalEvaluator,
    RetrievalGroundTruthDocument,
    RetrievedDocument,
)

random.seed(42)


def _get_file(name):
    """Get the file from the unittest data folder."""
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, name)


@pytest.fixture()
def doc_retrieval_eval_data():
    filename = _get_file("beir_document_retrieval_evaluation.jsonl")
    records = []
    with open(filename) as f:
        records.extend([json.loads(x) for x in f.readlines()])

    return filename, records


@pytest.fixture()
def bad_doc_retrieval_eval_data():
    filename = _get_file("bad_input_document_retrieval_evaluation.jsonl")

    records = []
    with open(filename) as f:
        records.extend([json.loads(x) for x in f.readlines()])

    return filename, records


def test_success(doc_retrieval_eval_data):
    _, records = doc_retrieval_eval_data
    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=3)

    for record in records:
        result = evaluator(**record)

        assert isinstance(result, dict)
        assert "document_retrieval_properties" in result
        assert "ndcg@3" in result["document_retrieval_properties"]


def test_groundtruth_min_gte_max():
    expected_exception_msg = (
        "The ground truth label maximum must be strictly greater than the ground truth label minimum."
    )
    with pytest.raises(EvaluationException) as exc_info:
        DocumentRetrievalEvaluator(ground_truth_label_min=2, ground_truth_label_max=1)

    assert expected_exception_msg in str(exc_info._excinfo[1])

    with pytest.raises(EvaluationException) as exc_info:
        DocumentRetrievalEvaluator(ground_truth_label_max=0, ground_truth_label_min=0)

    assert expected_exception_msg in str(exc_info._excinfo[1])


def test_incorrect_groundtruth_min():
    expected_exception_msg = (
        "A query relevance label less than the configured minimum value was detected in the evaluation input data. "
        "Check the range of ground truth label values in the input data and set the value of ground_truth_label_min to "
        "the appropriate value for your data."
    )
    data_groundtruth_min = 0
    configured_groundtruth_min = 1

    groundtruth_docs = [
        RetrievalGroundTruthDocument({"document_id": f"doc_{x}", "query_relevance_label": x})
        for x in range(data_groundtruth_min, 5)
    ]

    retrieved_docs = [
        RetrievedDocument({"document_id": f"doc_{x}", "relevance_score": random.uniform(-10, 10)})
        for x in range(data_groundtruth_min, 5)
    ]

    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=configured_groundtruth_min, ground_truth_label_max=4)

    with pytest.raises(EvaluationException) as exc_info:
        evaluator(retrieval_ground_truth=groundtruth_docs, retrieved_documents=retrieved_docs)

    assert expected_exception_msg in str(exc_info._excinfo[1])


def test_incorrect_groundtruth_max():
    expected_exception_msg = (
        "A query relevance label greater than the configured maximum value was detected in the evaluation input data. "
        "Check the range of ground truth label values in the input data and set the value of ground_truth_label_max to "
        "the appropriate value for your data."
    )
    data_groundtruth_max = 5
    configured_groundtruth_max = 4

    groundtruth_docs = [
        RetrievalGroundTruthDocument({"document_id": f"doc_{x}", "query_relevance_label": x})
        for x in range(0, data_groundtruth_max + 1)
    ]

    retrieved_docs = [
        RetrievedDocument({"document_id": f"doc_{x}", "relevance_score": random.uniform(-10, 10)})
        for x in range(0, data_groundtruth_max + 1)
    ]

    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=configured_groundtruth_max)

    with pytest.raises(EvaluationException) as exc_info:
        evaluator(retrieval_ground_truth=groundtruth_docs, retrieved_documents=retrieved_docs)

    assert expected_exception_msg in str(exc_info._excinfo[1])


def test_thresholds(doc_retrieval_eval_data):
    _, records = doc_retrieval_eval_data
    record = records[-1]
    custom_threshold_subset = {
        "ndcg_threshold": 0.7,
        "xdcg_threshold": 0.7,
        "fidelity_threshold": 0.7,
    }

    custom_threshold_superset = {
        "ndcg_threshold": 0.7,
        "xdcg_threshold": 0.7,
        "fidelity_threshold": 0.7,
        "top1_relevance_threshold": 70,
        "top3_max_relevance_threshold": 70,
        "total_retrieved_documents_threshold": 10,
        "total_ground_truth_documents_threshold": 10,
    }

    for threshold in [custom_threshold_subset, custom_threshold_superset]:
        evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=2, **threshold)
        results = evaluator(**record)

        expected_keys = [
            "ndcg@3",
            "ndcg@3_passed",
            "ndcg@3_result",
            "ndcg@3_threshold",
            "ndcg@3_higher_is_better",
            "xdcg@3",
            "xdcg@3_passed",
            "xdcg@3_result",
            "xdcg@3_threshold",
            "xdcg@3_higher_is_better",
            "fidelity",
            "fidelity_passed",
            "fidelity_result",
            "fidelity_threshold",
            "fidelity_higher_is_better",
            "top1_relevance",
            "top1_relevance_passed",
            "top1_relevance_result",
            "top1_relevance_threshold",
            "top1_relevance_higher_is_better",
            "top3_max_relevance",
            "top3_max_relevance_passed",
            "top3_max_relevance_result",
            "top3_max_relevance_threshold",
            "top3_max_relevance_higher_is_better",
            "total_retrieved_documents",
            "total_retrieved_documents_passed",
            "total_retrieved_documents_result",
            "total_retrieved_documents_threshold",
            "total_retrieved_documents_higher_is_better",
            "total_ground_truth_documents",
            "total_ground_truth_documents_passed",
            "total_ground_truth_documents_result",
            "total_ground_truth_documents_threshold",
            "total_ground_truth_documents_higher_is_better",
            "holes",
            "holes_passed",
            "holes_result",
            "holes_threshold",
            "holes_higher_is_better",
            "holes_ratio",
            "holes_ratio_passed",
            "holes_ratio_result",
            "holes_ratio_threshold",
            "holes_ratio_higher_is_better",
        ]

        assert "document_retrieval_properties" in results
        assert set(expected_keys) == set(results["document_retrieval_properties"].keys())


def test_invalid_input(bad_doc_retrieval_eval_data):
    filename, records = bad_doc_retrieval_eval_data
    for record in records:
        expected_exception_msg = record.pop("expected_exception")
        with pytest.raises(EvaluationException) as exc_info:
            evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=2)
            evaluator(**record)

        assert expected_exception_msg in str(exc_info._excinfo[1])


def test_qrels_results_limit():
    groundtruth_docs = [
        RetrievalGroundTruthDocument(
            {"document_id": f"doc_{x}", "query_relevance_label": random.choice([0, 1, 2, 3, 4])}
        )
        for x in range(0, 10000)
    ]

    retrieved_docs = [
        RetrievedDocument({"document_id": f"doc_{x}", "relevance_score": random.uniform(-10, 10)})
        for x in range(0, 10000)
    ]

    evaluator = DocumentRetrievalEvaluator()
    evaluator(retrieval_ground_truth=groundtruth_docs, retrieved_documents=retrieved_docs)


def test_qrels_results_exceeds_max_allowed():
    expected_exception_msg = (
        "'retrieval_ground_truth' and 'retrieved_documents' inputs should contain no more than 10000 items."
    )

    groundtruth_docs = [
        RetrievalGroundTruthDocument(
            {"document_id": f"doc_{x}", "query_relevance_label": random.choice([0, 1, 2, 3, 4])}
        )
        for x in range(0, 10001)
    ]

    retrieved_docs = [
        RetrievedDocument({"document_id": f"doc_{x}", "relevance_score": random.uniform(-10, 10)})
        for x in range(0, 10001)
    ]

    evaluator = DocumentRetrievalEvaluator()

    with pytest.raises(EvaluationException) as exc_info:
        evaluator(retrieval_ground_truth=groundtruth_docs, retrieved_documents=retrieved_docs)

    assert expected_exception_msg in str(exc_info._excinfo[1])


def test_no_retrieved_documents():
    groundtruth_docs = [
        RetrievalGroundTruthDocument(
            {"document_id": f"doc_{x}", "query_relevance_label": random.choice([0, 1, 2, 3, 4])}
        )
        for x in range(0, 9)
    ]

    retrieved_docs = []

    evaluator = DocumentRetrievalEvaluator()
    result = evaluator(retrieval_ground_truth=groundtruth_docs, retrieved_documents=retrieved_docs)

    properties = result["document_retrieval_properties"]
    assert properties["ndcg@3"] == 0
    assert properties["holes"] == 0


def test_no_labeled_retrieved_documents():
    groundtruth_docs = [
        RetrievalGroundTruthDocument(
            {"document_id": f"doc_{x}", "query_relevance_label": random.choice([0, 1, 2, 3, 4])}
        )
        for x in range(0, 9)
    ]

    retrieved_docs = [
        RetrievedDocument({"document_id": f"doc_{x}_nolabel", "relevance_score": random.uniform(-10, 10)})
        for x in range(0, 9)
    ]

    evaluator = DocumentRetrievalEvaluator()
    result = evaluator(retrieval_ground_truth=groundtruth_docs, retrieved_documents=retrieved_docs)

    properties = result["document_retrieval_properties"]
    assert properties["ndcg@3"] == 0
    assert properties["holes"] == len(retrieved_docs)


def _assert_exception_metadata(exc, *, category, blame=ErrorBlame.USER_ERROR):
    """Assert that an EvaluationException has the expected blame, category, and target populated."""
    assert exc.blame == blame
    assert exc.category == category
    assert exc.target == ErrorTarget.DOCUMENT_RETRIEVAL_EVALUATOR


def test_init_label_min_not_int_error_metadata():
    with pytest.raises(EvaluationException) as exc_info:
        DocumentRetrievalEvaluator(ground_truth_label_min=0.5, ground_truth_label_max=4)  # type: ignore

    _assert_exception_metadata(exc_info.value, category=ErrorCategory.INVALID_VALUE)


def test_init_label_max_not_int_error_metadata():
    with pytest.raises(EvaluationException) as exc_info:
        DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=4.5)  # type: ignore

    _assert_exception_metadata(exc_info.value, category=ErrorCategory.INVALID_VALUE)


def test_init_label_min_gte_max_error_metadata():
    with pytest.raises(EvaluationException) as exc_info:
        DocumentRetrievalEvaluator(ground_truth_label_min=2, ground_truth_label_max=1)

    _assert_exception_metadata(exc_info.value, category=ErrorCategory.INVALID_VALUE)


def test_empty_ground_truth_error_metadata():
    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=2)

    with pytest.raises(EvaluationException) as exc_info:
        evaluator(retrieval_ground_truth=[], retrieved_documents=[])

    _assert_exception_metadata(exc_info.value, category=ErrorCategory.MISSING_FIELD)


def test_missing_ground_truth_fields_error_metadata():
    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=2)

    with pytest.raises(EvaluationException) as exc_info:
        evaluator(
            retrieval_ground_truth=[{"document_id": "doc_0"}],
            retrieved_documents=[{"document_id": "doc_0", "relevance_score": 1.0}],
        )

    _assert_exception_metadata(exc_info.value, category=ErrorCategory.MISSING_FIELD)


def test_non_integer_query_relevance_label_error_metadata():
    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=2)

    with pytest.raises(EvaluationException) as exc_info:
        evaluator(
            retrieval_ground_truth=[{"document_id": "doc_0", "query_relevance_label": 1.5}],
            retrieved_documents=[{"document_id": "doc_0", "relevance_score": 1.0}],
        )

    _assert_exception_metadata(exc_info.value, category=ErrorCategory.INVALID_VALUE)


def test_query_relevance_label_below_min_error_metadata():
    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=1, ground_truth_label_max=4)

    with pytest.raises(EvaluationException) as exc_info:
        evaluator(
            retrieval_ground_truth=[{"document_id": "doc_0", "query_relevance_label": 0}],
            retrieved_documents=[{"document_id": "doc_0", "relevance_score": 1.0}],
        )

    _assert_exception_metadata(exc_info.value, category=ErrorCategory.INVALID_VALUE)


def test_query_relevance_label_above_max_error_metadata():
    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=2)

    with pytest.raises(EvaluationException) as exc_info:
        evaluator(
            retrieval_ground_truth=[{"document_id": "doc_0", "query_relevance_label": 5}],
            retrieved_documents=[{"document_id": "doc_0", "relevance_score": 1.0}],
        )

    _assert_exception_metadata(exc_info.value, category=ErrorCategory.INVALID_VALUE)


def test_missing_retrieved_document_fields_error_metadata():
    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=2)

    with pytest.raises(EvaluationException) as exc_info:
        evaluator(
            retrieval_ground_truth=[{"document_id": "doc_0", "query_relevance_label": 1}],
            retrieved_documents=[{"document_id": "doc_0"}],
        )

    _assert_exception_metadata(exc_info.value, category=ErrorCategory.MISSING_FIELD)


def test_non_numeric_relevance_score_error_metadata():
    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=2)

    with pytest.raises(EvaluationException) as exc_info:
        evaluator(
            retrieval_ground_truth=[{"document_id": "doc_0", "query_relevance_label": 1}],
            retrieved_documents=[{"document_id": "doc_0", "relevance_score": "not-a-number"}],
        )

    _assert_exception_metadata(exc_info.value, category=ErrorCategory.INVALID_VALUE)


def test_too_many_documents_error_metadata():
    groundtruth_docs = [
        RetrievalGroundTruthDocument(
            {"document_id": f"doc_{x}", "query_relevance_label": random.choice([0, 1, 2, 3, 4])}
        )
        for x in range(0, 10001)
    ]
    retrieved_docs = [
        RetrievedDocument({"document_id": f"doc_{x}", "relevance_score": random.uniform(-10, 10)})
        for x in range(0, 10001)
    ]

    evaluator = DocumentRetrievalEvaluator()

    with pytest.raises(EvaluationException) as exc_info:
        evaluator(retrieval_ground_truth=groundtruth_docs, retrieved_documents=retrieved_docs)

    _assert_exception_metadata(exc_info.value, category=ErrorCategory.INVALID_VALUE)


def test_missing_threshold_error_metadata():
    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=2)

    with pytest.raises(EvaluationException) as exc_info:
        evaluator._get_binary_result(unknown_metric=1.0)

    _assert_exception_metadata(exc_info.value, category=ErrorCategory.FAILED_EXECUTION, blame=ErrorBlame.SYSTEM_ERROR)


# On a scale of -1 to 2, -1 is the configured minimum ("irrelevant") and 0 is the lowest relevant label.
NEGATIVE_SCALE_GROUND_TRUTH = [
    {"document_id": "relevant_0", "query_relevance_label": 0},
    {"document_id": "irrelevant", "query_relevance_label": -1},
]


def _negative_scale_properties(retrieved_ids):
    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=-1, ground_truth_label_max=2)
    result = evaluator(
        retrieval_ground_truth=NEGATIVE_SCALE_GROUND_TRUTH,
        retrieved_documents=[
            {"document_id": doc_id, "relevance_score": float(len(retrieved_ids) - i)}
            for i, doc_id in enumerate(retrieved_ids)
        ],
    )
    return result["document_retrieval_properties"]


def test_fidelity_counts_label_zero_as_relevant_when_label_min_is_negative():
    # The only relevant document is retrieved, so fidelity is 1. It used to be 0, because a retrieved
    # document labeled 0 was treated like a document without a label.
    properties = _negative_scale_properties(["relevant_0"])
    assert properties["fidelity"] == pytest.approx(1.0)
    assert properties["top1_relevance"] == 0
    assert properties["top3_max_relevance"] == 0
    assert properties["holes"] == 0

    # Also retrieving the irrelevant document does not change fidelity.
    properties = _negative_scale_properties(["relevant_0", "irrelevant"])
    assert properties["fidelity"] == pytest.approx(1.0)


def test_holes_do_not_count_as_relevant_when_label_min_is_negative():
    # A retrieved document without a label used to get label 0, which is relevant on this scale,
    # so an irrelevant document plus a hole gave fidelity 1.
    properties = _negative_scale_properties(["irrelevant", "unlabeled"])
    assert properties["fidelity"] == 0
    assert properties["top1_relevance"] == -1
    assert properties["top3_max_relevance"] == -1
    assert properties["holes"] == 1

    properties = _negative_scale_properties(["unlabeled"])
    assert properties["fidelity"] == 0
    assert properties["top1_relevance"] == -1
    assert properties["holes"] == 1


@pytest.mark.parametrize(
    "label_min, label_max, ground_truth, retrieved_ids, expected",
    [
        # Default scale: a retrieved document labeled 0 (the minimum) still reports zeros.
        (
            0,
            4,
            [("a", 0), ("b", 3)],
            ["a"],
            {"ndcg@3": 0, "fidelity": 0, "top1_relevance": 0, "top3_max_relevance": 0, "holes": 0},
        ),
        # Default scale: only holes retrieved.
        (
            0,
            4,
            [("a", 2)],
            ["x", "y"],
            {"ndcg@3": 0, "fidelity": 0, "top1_relevance": 0, "top3_max_relevance": 0, "holes": 2},
        ),
        # Scale starting above 0: holes still get label 0, and a document at the minimum is scored as before.
        (
            1,
            4,
            [("a", 1), ("b", 3)],
            ["a", "x"],
            {"fidelity": 0, "top1_relevance": 1, "top3_max_relevance": 1, "holes": 1},
        ),
    ],
)
def test_label_scales_starting_at_or_above_zero_are_unchanged(
    label_min, label_max, ground_truth, retrieved_ids, expected
):
    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=label_min, ground_truth_label_max=label_max)
    result = evaluator(
        retrieval_ground_truth=[{"document_id": d, "query_relevance_label": label} for d, label in ground_truth],
        retrieved_documents=[
            {"document_id": doc_id, "relevance_score": float(len(retrieved_ids) - i)}
            for i, doc_id in enumerate(retrieved_ids)
        ],
    )
    properties = result["document_retrieval_properties"]
    for key, value in expected.items():
        assert properties[key] == pytest.approx(value), key
