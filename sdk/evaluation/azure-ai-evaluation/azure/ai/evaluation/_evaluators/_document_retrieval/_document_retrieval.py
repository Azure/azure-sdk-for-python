# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
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


DocumentRetrievalMetrics = TypedDict(
    'DocumentRetrievalMetrics',
    {
        "ndcg@{self.k}": float,
        "xdcg@{self.k}": float,
        "fidelity": float,
        "top1_relevance": float,
        "topk_max_relevance@{self.k}": float,
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
    def __init__(self):
        super().__init__()
        self.k = 3
        self.xdcg_discount_factor = 0.6 

    def __compute_holes(
        self,
        actual_docs: list,
        labeled_docs: list
    ) -> int:
        """
        The number of documents retrieved from a search query which have no provided ground-truth label.
        This metric is helpful for determining the accuracy of other metrics that are highly sensitive to missing ground-truth knowledge,
        such as NDCG, XDCG, and Fidelity.
        """
        return len(set(actual_docs).difference(set(labeled_docs)))
    
    def __compute_ndcg(
        self,
        result_docs_groundtruth_labels: List[float],
        ideal_docs_groundtruth_labels: List[float],
    ) -> float:
        """
        NDCG (Normalized Discounted Cumulative Gain) calculated for the top 3 documents retrieved from a search query.
        NDCG measures how well a document ranking compares to an ideal document ranking given a list of ground-truth documents.
        """
        # Set the scoring function
        def calculate_dcg(relevance: float, rank: int):
            return ((math.pow(2, relevance) - 1) / (math.log2(rank + 1)))

        ranks = list(range(1, self.k + 1))
        dcg = sum(starmap(calculate_dcg, zip(result_docs_groundtruth_labels, ranks)))
        idcg = sum(starmap(calculate_dcg, zip(ideal_docs_groundtruth_labels, ranks)))
        ndcg = dcg / float(idcg)

        return ndcg
    
    def __compute_xdcg(
        self,
        result_docs_groundtruth_labels: List[float]
    ) -> float:
        """
        XDCG calculated for the top 3 documents retrieved from a search query.
        XDCG measures how objectively good are the top 3 documents, discounted by their position in the list.
        """
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
        """
        Fidelity calculated over all documents retrieved from a search query.
        Fidelity measures how objectively good are all of the documents retrieved compared with all known good documents in the underlying data store.
        """
        def get_rating(label: float) -> str:
            if label >= 3:
                return "perfect"
            
            elif label >= 2.5:
                return "excellent"
            
            elif label >= 2:
                return "good"
            
            elif label >= 1.5:
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

        if weighted_sum_by_rating_index == 0:
            return math.nan

        return weighted_sum_by_rating_results / float(weighted_sum_by_rating_index)
    
    def __call__(self, *, groundtruth_documents_labels: str, retrieved_documents_labels: str) -> DocumentRetrievalMetrics:
        # input validation
        qrels = [DocumentLabel(x) for x in json.loads(groundtruth_documents_labels)]
        results = [DocumentLabel(x) for x in json.loads(retrieved_documents_labels)]

        if len(qrels) > 1000 or len(results) > 1000:
            raise ValueError("The results and ground-truth sets should contain no more than 1000 items.")

        # if the qrels are empty, no meaningful evaluation is possible
        if len(qrels) == 0:
            raise ValueError("No groundtruth labels were provided.")

        # if the results set is empty, results are all zero
        if len(results) == 0:
            return DocumentRetrievalMetrics(**{
                f"ndcg@{self.k}": 0,
                f"xdcg@{self.k}": 0,
                "fidelity": 0,
                "top1_relevance": 0,
                f"topk_max_relevance@{self.k}": 0,
                "holes": 0,
                "ratioholes": 0,
                "total_document_results": len(results),
                "total_groundtruth_documents": len(qrels)
            })

        # flatten qrels and results to normal dictionaries
        qrels_lookup = {x["document_id"]: x["label"] for x in qrels}
        results_lookup = {x["document_id"]: x["label"] for x in results}

        # sort each input set by label to get the ranking
        qrels_sorted_by_rank = sorted(qrels_lookup.items(), key=lambda x: x[1], reverse=True)
        results_sorted_by_rank = sorted(results_lookup.items(), key=lambda x: x[1], reverse=True)

        # find ground truth labels for the results set and ideal set
        result_docs_groundtruth_labels = [qrels_lookup[doc_id] if doc_id in qrels_lookup else 0 for (doc_id, _) in results_sorted_by_rank]
        ideal_docs_groundtruth_labels = [label for (_, label) in qrels_sorted_by_rank]

        # calculate the proportion of result docs with no ground truth label (holes)
        holes = self.__compute_holes(
            [x[0] for x in results_sorted_by_rank],
            [x[0] for x in qrels_sorted_by_rank]
        )
        ratioholes = holes / float(len(results))

        # if none of the retrieved docs are labeled, report holes only
        if not any(result_docs_groundtruth_labels):
            return DocumentRetrievalMetrics(**{
                f"ndcg@{self.k}": 0,
                f"xdcg@{self.k}": 0,
                "fidelity": 0,
                "top1_relevance": 0,
                f"topk_max_relevance@{self.k}": 0,
                "holes": holes,
                "ratioholes": ratioholes,
                "total_document_results": len(results),
                "total_groundtruth_documents": len(qrels)
            })

        return DocumentRetrievalMetrics(**{
            f"ndcg@{self.k}": self.__compute_ndcg(result_docs_groundtruth_labels[:self.k], ideal_docs_groundtruth_labels[:self.k]),
            f"xdcg@{self.k}": self.__compute_xdcg(result_docs_groundtruth_labels[:self.k]),
            "fidelity": self.__compute_fidelity(result_docs_groundtruth_labels, ideal_docs_groundtruth_labels),
            "top1_relevance": result_docs_groundtruth_labels[0],
            f"topk_max_relevance@{self.k}": max(result_docs_groundtruth_labels[:self.k]),
            "holes": holes,
            "ratioholes": ratioholes,
            "total_document_results": len(results),
            "total_groundtruth_documents": len(qrels)
        })
