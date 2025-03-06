# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import math
from itertools import starmap
from azure.ai.evaluation._evaluators._common import EvaluatorBase
from typing import List, TypedDict


DocumentLabel = TypedDict(
    'DocumentLabel',
    {
        "document_id": str,
        "label": float
    }
)


DocumentRetrievalEvaluationData = TypedDict(
    'DocumentRetrievalEvaluationData',
    {
        "retrieved_documents_labels": List[DocumentLabel],
        "groundtruth_documents_labels": List[DocumentLabel]
    }
)


DocumentRetrievalMetrics = TypedDict(
    'DocumentRetrievalMetrics',
    {
        "ndcg@3": float,
        "xdcg@3": float,
        "fidelity": float,
        "top1_relevance": float,
        "topk_max_relevance@3": float,
        "holes": int,
        "holes_ratio": float,
        "total_document_results": int,
        "total_groundtruth_documents": int
    }
)

class DocumentRetrievalEvaluator:
    """
    Calculate document retrieval metrics, such as NDCG, XDCG, Fidelity and Top K Relevance.
    """
    def __init__(
        self,
        ndcg_score_linear: bool = True,
        xdcg_discount_factor: float = 0.6
    ):
        super().__init__()

        self.ndcg_score_linear = ndcg_score_linear  # TODO: pick an NDCG implementation to avoid setting this value
        self.xdcg_discount_factor = xdcg_discount_factor  # TODO: should we expose this, or just pick a recommended value?

    def __compute_holes(
        self,
        actual_docs: list,
        labeled_docs: list
    ) -> int:
        return len(set(actual_docs).difference(set(labeled_docs)))
    

    def __compute_ndcg(
        self,
        result_docs_groundtruth_labels: List[float],
        ideal_docs_groundtruth_labels: List[float],
    ) -> float:
        # Set the scoring function
        def calculate_dcg(relevance: float, rank: int):
            return ((math.pow(2, relevance) - 1) / (math.log2(rank + 1)))
        
        def calculate_dcg_linear(relevance: float, rank: int):
            return (relevance / (math.log2(rank + 1)))
        
        score_fn = calculate_dcg_linear if self.ndcg_score_linear else calculate_dcg

        ranks = list(range(1, self.k + 1))
        dcg = sum(starmap(score_fn, zip(result_docs_groundtruth_labels, ranks)))
        idcg = sum(starmap(score_fn, zip(ideal_docs_groundtruth_labels, ranks)))
        ndcg = dcg / float(idcg)

        return ndcg
    
    def __compute_xdcg(
        self,
        result_docs_groundtruth_labels: List[float]
    ) -> float:
        def calculate_xdcg_numerator(relevance, rank):
            return (25 * relevance * math.pow(self.xdcg_discount_factor, rank - 1))
        
        def calculate_xdcg_denominator(rank):
            return math.pow(self.xdcg_discount_factor, rank - 1)

        ranks = list(range(1, self.k + 1))
        xdcg_n = sum(starmap(calculate_xdcg_numerator, zip(result_docs_groundtruth_labels, ranks)))
        xdcg_d = sum(map(calculate_xdcg_denominator, ranks))

        return xdcg_n / float(xdcg_d)
    
    def __compute_fidelity(
        self,
        result_docs_groundtruth_labels: List[float],
        ideal_docs_groundtruth_labels: List[float],
    ) -> float:
        def get_rating(label: float) -> str:
            if label >= 4:
                return "perfect"
            
            elif label >= 3:
                return "excellent"
            
            elif label >= 2:
                return "good"
            
            elif label >= 1:
                return "fair"
            
            else:
                return "poor"

        def calculate_weighted_sum_by_rating(labels: List[float]) -> float:
            rating_counts = {
                "perfect": 0,
                "excellent": 0,
                "good": 0,
                "fair": 0, 
                "poor": 0
            }

            for label in labels:
                rating_counts[get_rating(label)] += 1 
            
            return (31 * rating_counts["perfect"]) + (15 * rating_counts["excellent"]) + (7 * rating_counts["good"]) + (3 * rating_counts["fair"]) 
        
        weighted_sum_by_rating_results = calculate_weighted_sum_by_rating(result_docs_groundtruth_labels)
        weighted_sum_by_rating_index = calculate_weighted_sum_by_rating(ideal_docs_groundtruth_labels)

        return weighted_sum_by_rating_results / float(weighted_sum_by_rating_index)
    
    def __call__(self, *, evaluation_data: DocumentRetrievalEvaluationData) -> DocumentRetrievalMetrics:
        qrels = evaluation_data["groundtruth_documents_labels"]
        results = evaluation_data["retrieved_documents_labels"]

        # if the qrels are empty, no meaningful evaluation is possible
        if len(qrels) == 0:
            raise ValueError("No groundtruth labels were provided.")

        # if the results set is empty, results are all zero
        if len(results) == 0:
            return DocumentRetrievalMetrics(**{
                "ndcg@3": 0,
                "xdcg@3": 0,
                "fidelity": 0,
                "top1_relevance": 0,
                "topk_max_relevance@3": 0,
                "holes": 0,
                "ratioholes": 0,
                "total_document_results": len(results),
                "total_groundtruth_documents": len(qrels)
            })

        # flatten qrels and results to normal dictionaries
        qrels_lookup = {x["document_id"]: x["label"] for x in qrels}
        results_lookup = {x["document_id"]: x["label"] for x in results}

        # calculate the proportion of result docs with no ground truth label (holes)
        holes = self.__compute_holes(list(results_lookup.keys()), list(qrels_lookup.keys()))
        ratioholes = holes / len(results)

        # sort each input set by label to get the ranking
        qrels_sorted_by_rank = sorted(qrels_lookup.items(), key=lambda x: x[1], reverse=True)
        results_sorted_by_rank = sorted(results_lookup.items(), key=lambda x: x[1], reverse=True)

        # find ground truth labels for the results set and ideal set
        result_docs_groundtruth_labels = [qrels_lookup[doc_id] if doc_id in qrels_lookup else 0 for (doc_id, _) in results_sorted_by_rank]
        ideal_docs_groundtruth_labels = [label for (_, label) in qrels_sorted_by_rank]

        # if none of the retrieved docs are labeled, report holes only
        if not any(result_docs_groundtruth_labels):
            return DocumentRetrievalMetrics(**{
                "ndcg@3": 0,
                "xdcg@3": 0,
                "fidelity": 0,
                "top1_relevance": 0,
                "topk_max_relevance@3": 0,
                "holes": holes,
                "ratioholes": ratioholes,
                "total_document_results": len(results),
                "total_groundtruth_documents": len(qrels)
            })

        return DocumentRetrievalMetrics(**{
            "ndcg@3": self.__compute_ndcg(result_docs_groundtruth_labels[:3], ideal_docs_groundtruth_labels[:3]),
            "xdcg@3": self.__compute_xdcg(result_docs_groundtruth_labels[:3]),
            "fidelity": self.__compute_fidelity(result_docs_groundtruth_labels, ideal_docs_groundtruth_labels),
            "top1_relevance": result_docs_groundtruth_labels[0],
            "topk_max_relevance@3": max(result_docs_groundtruth_labels[:3]),
            "holes": holes,
            "ratioholes": ratioholes,
            "total_document_results": len(results),
            "total_groundtruth_documents": len(qrels)
        })
