# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import pytest
import os
import json
import pathlib
import random
from azure.ai.evaluation import evaluate
from azure.ai.evaluation._exceptions import EvaluationException
from azure.ai.evaluation._evaluators._document_retrieval import (
    DocumentRetrievalEvaluator,
    RetrievalGroundTruthDocument,
    RetrievedDocument
)

def _get_file(name):
    """Get the file from the unittest data folder."""
    data_path = os.path.join(pathlib.Path(__file__).parent.resolve(), "data")
    return os.path.join(data_path, name)

@pytest.fixture()
def doc_retrieval_eval_data():
    filename = _get_file("beir_document_retrieval_evaluation.jsonl")
    records = []
    with open(filename) as f:
        records.extend(
            [json.loads(x) for x in f.readlines()]
        )

    return filename, records

@pytest.fixture()
def bad_doc_retrieval_eval_data():
    filename = _get_file("bad_input_document_retrieval_evaluation.jsonl")

    records = []
    with open(filename) as f:
        records.extend(
            [json.loads(x) for x in f.readlines()]
        )

    return filename, records

def test_success(doc_retrieval_eval_data):
    _, records = doc_retrieval_eval_data
    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=3)
    
    for record in records:
        result = evaluator(**record)

        assert isinstance(result, dict)
        assert "ndcg@3" in result

def test_groundtruth_min_gte_max():
    expected_exception_msg = "The ground truth label maximum must be strictly greater than the ground truth label minimum."
    with pytest.raises(EvaluationException) as exc_info:
        DocumentRetrievalEvaluator(ground_truth_label_min=2, ground_truth_label_max=1)

    assert expected_exception_msg in str(
        exc_info._excinfo[1]
    )

    with pytest.raises(EvaluationException) as exc_info:
        DocumentRetrievalEvaluator(ground_truth_label_max=0, ground_truth_label_min=0)

    assert expected_exception_msg in str(
        exc_info._excinfo[1]
    )

def test_incorrect_groundtruth_min():
    expected_exception_msg = ("A query relevance label less than the configured minimum value was detected in the evaluation input data. "
                        "Check the range of ground truth label values in the input data and set the value of ground_truth_label_min to "
                        "the appropriate value for your data.")
    data_groundtruth_min = 0
    configured_groundtruth_min = 1

    groundtruth_docs = [
        RetrievalGroundTruthDocument({"document_id": f"doc_{x}", "query_relevance_label": x}) for x in range(data_groundtruth_min, 5)
    ]

    retrieved_docs = [
        RetrievedDocument({"document_id": f"doc_{x}", "relevance_score": random.uniform(-10, 10)}) for x in range(data_groundtruth_min, 5)
    ]

    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=configured_groundtruth_min, ground_truth_label_max=4)

    with pytest.raises(EvaluationException) as exc_info:
        evaluator(retrieval_ground_truth=groundtruth_docs, retrieved_documents=retrieved_docs)

    assert expected_exception_msg in str(
        exc_info._excinfo[1]
    )

def test_incorrect_groundtruth_max():
    expected_exception_msg = ("A query relevance label greater than the configured maximum value was detected in the evaluation input data. "
                        "Check the range of ground truth label values in the input data and set the value of ground_truth_label_max to "
                        "the appropriate value for your data.")
    data_groundtruth_max = 5
    configured_groundtruth_max = 4

    groundtruth_docs = [
        RetrievalGroundTruthDocument({"document_id": f"doc_{x}", "query_relevance_label": x}) for x in range(0, data_groundtruth_max + 1)
    ]

    retrieved_docs = [
        RetrievedDocument({"document_id": f"doc_{x}", "relevance_score": random.uniform(-10, 10)}) for x in range(0, data_groundtruth_max + 1)
    ]

    evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=configured_groundtruth_max)

    with pytest.raises(EvaluationException) as exc_info:
        evaluator(retrieval_ground_truth=groundtruth_docs, retrieved_documents=retrieved_docs)

    assert expected_exception_msg in str(
        exc_info._excinfo[1]
    )

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
        "total_ground_truth_documents_threshold": 10
    }

    for threshold in [custom_threshold_subset, custom_threshold_superset]:
        evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=2, **threshold)
        results = evaluator(**record)

        expected_keys = [
            "ndcg@3", "ndcg@3_result", "ndcg@3_threshold", "ndcg@3_higher_is_better",
            "xdcg@3", "xdcg@3_result", "xdcg@3_threshold", "xdcg@3_higher_is_better",
            "fidelity", "fidelity_result", "fidelity_threshold", "fidelity_higher_is_better",
            "top1_relevance", "top1_relevance_result", "top1_relevance_threshold", "top1_relevance_higher_is_better",
            "top3_max_relevance", "top3_max_relevance_result", "top3_max_relevance_threshold", "top3_max_relevance_higher_is_better",
            "total_retrieved_documents", "total_retrieved_documents_result", "total_retrieved_documents_threshold", "total_retrieved_documents_higher_is_better",
            "total_ground_truth_documents", "total_ground_truth_documents_result", "total_ground_truth_documents_threshold", "total_ground_truth_documents_higher_is_better",
            "holes", "holes_result", "holes_threshold", "holes_higher_is_better",
            "holes_ratio", "holes_ratio_result", "holes_ratio_threshold", "holes_ratio_higher_is_better"
        ]

        assert set(expected_keys) == set(results.keys())

def test_invalid_input(bad_doc_retrieval_eval_data):
    filename, records = bad_doc_retrieval_eval_data
    for record in records:
        expected_exception_msg = record.pop("expected_exception")
        with pytest.raises(EvaluationException) as exc_info:
            evaluator = DocumentRetrievalEvaluator(ground_truth_label_min=0, ground_truth_label_max=2)
            evaluator(**record)

        assert expected_exception_msg in str(
            exc_info._excinfo[1]
        )


def test_qrels_results_limit():
    groundtruth_docs = [
        RetrievalGroundTruthDocument({"document_id": f"doc_{x}", "query_relevance_label": random.choice([0, 1, 2, 3, 4])}) for x in range(0, 10000)
    ]

    retrieved_docs = [
        RetrievedDocument({"document_id": f"doc_{x}", "relevance_score": random.uniform(-10, 10)}) for x in range(0, 10000)
    ]

    evaluator = DocumentRetrievalEvaluator()
    evaluator(retrieval_ground_truth=groundtruth_docs, retrieved_documents=retrieved_docs)

def test_qrels_results_exceeds_max_allowed():
    expected_exception_msg = "'retrieval_ground_truth' and 'retrieved_documents' inputs should contain no more than 10000 items."

    groundtruth_docs = [
        RetrievalGroundTruthDocument({"document_id": f"doc_{x}", "query_relevance_label": random.choice([0, 1, 2, 3, 4])}) for x in range(0, 10001)
    ]

    retrieved_docs = [
        RetrievedDocument({"document_id": f"doc_{x}", "relevance_score": random.uniform(-10, 10)}) for x in range(0, 10001)
    ]

    evaluator = DocumentRetrievalEvaluator()

    with pytest.raises(EvaluationException) as exc_info:
        evaluator(retrieval_ground_truth=groundtruth_docs, retrieved_documents=retrieved_docs)

    assert expected_exception_msg in str(
        exc_info._excinfo[1]
    )

def test_no_retrieved_documents():
    groundtruth_docs = [
        RetrievalGroundTruthDocument({"document_id": f"doc_{x}", "query_relevance_label": random.choice([0, 1, 2, 3, 4])}) for x in range(0, 9)
    ]

    retrieved_docs = []

    evaluator = DocumentRetrievalEvaluator()
    result = evaluator(retrieval_ground_truth=groundtruth_docs, retrieved_documents=retrieved_docs)

    assert result["ndcg@3"] == 0
    assert result["holes"] == 0

def test_no_labeled_retrieved_documents():
    groundtruth_docs = [
        RetrievalGroundTruthDocument({"document_id": f"doc_{x}", "query_relevance_label": random.choice([0, 1, 2, 3, 4])}) for x in range(0, 9)
    ]

    retrieved_docs = [
        RetrievedDocument({"document_id": f"doc_{x}_nolabel", "relevance_score": random.uniform(-10, 10)}) for x in range(0, 9)
    ]

    evaluator = DocumentRetrievalEvaluator()
    result = evaluator(retrieval_ground_truth=groundtruth_docs, retrieved_documents=retrieved_docs)

    assert result["ndcg@3"] == 0
    assert result["holes"] == len(retrieved_docs)    

