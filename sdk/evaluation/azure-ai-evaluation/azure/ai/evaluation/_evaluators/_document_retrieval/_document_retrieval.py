# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import math
from itertools import starmap
from azure.ai.evaluation._evaluators._common import EvaluatorBase


class DocumentRetrievalEvaluator(EvaluatorBase):
    """
    Calculate document retrieval metrics, such as NDCG, XDCG, Fidelity and Top K Relevance.
    """
    def __init__(self, k: int = 3, ndcg_score_linear: bool = True, xdcg_discount_factor: float = 0.6):
        super().__init__()

        self.k = 3
        self.ndcg_score_linear = ndcg_score_linear  # TODO: pick an NDCG implementation to avoid setting this value
        self.xdcg_discount_factor = xdcg_discount_factor  # TODO: should we expose this, or just pick a recommended value?

    def __compute_holes(
        self,
        actual_docs,
        labeled_docs
    ):
        return len(set(actual_docs).difference(set(labeled_docs)))
    

    def __compute_ndcg(
        self,
        result_docs_groundtruth_labels: list,
        ideal_docs_groundtruth_labels: list,
    ):
        # Set the scoring function
        def calculate_dcg(relevance, rank):
            return ((math.pow(2, relevance) - 1) / (math.log2(rank + 1)))
        
        def calculate_dcg_linear(relevance, rank):
            return (relevance / (math.log2(rank + 1)))
        
        score_fn = calculate_dcg_linear if self.ndcg_score_linear else calculate_dcg

        ranks = list(range(1, self.k + 1))
        dcg = sum(starmap(score_fn, zip(result_docs_groundtruth_labels, ranks)))
        idcg = sum(starmap(score_fn, zip(ideal_docs_groundtruth_labels, ranks)))
        ndcg = dcg / float(idcg)

        return ndcg
    
    def __compute_xdcg(
        self,
        result_docs_groundtruth_labels: list
    ):
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
        result_docs_groundtruth_labels: list,
        ideal_docs_groundtruth_labels: list,
    ):
        def get_rating(score):
            if score >= 4:
                return "perfect"
            
            elif score >= 3:
                return "excellent"
            
            elif score >= 2:
                return "good"
            
            elif score >= 1:
                return "fair"
            
            else:
                return "poor"

        def calculate_weighted_sum_by_rating(relevance):
            rating_counts = {
                "perfect": 0,
                "excellent": 0,
                "good": 0,
                "fair": 0, 
                "poor": 0
            }

            for rel in relevance:
                rating_counts[get_rating(rel)] += 1 
            
            return (31 * rating_counts["perfect"]) + (15 * rating_counts["excellent"]) + (7 * rating_counts["good"]) + (3 * rating_counts["fair"]) 
        
        weighted_sum_by_rating_results = calculate_weighted_sum_by_rating(result_docs_groundtruth_labels)
        weighted_sum_by_rating_index = calculate_weighted_sum_by_rating(ideal_docs_groundtruth_labels)

        return weighted_sum_by_rating_results / float(weighted_sum_by_rating_index)
    
    def __call__(self, *, qrels: dict, results: dict):
        # if the results set or the groundtruth set is empty, no meaningful evaluation is possible.
        if len(results) == 0:
            return {
                f"ndcg@{self.k}": 0,
                f"xdcg@{self.k}": 0,
                f"fidelity": 0,
                f"top1_relevance": 0,
                f"topk_max_relevance@{self.k}": 0,
                f"holes": 0,
                f"ratioholes": 0,
                f"total_document_results": len(results),
                f"total_groundtruth_documents": len(qrels)
            }
        
        if len(qrels) == 0:
            return {
                f"ndcg@{self.k}": 0,
                f"xdcg@{self.k}": 0,
                f"fidelity": 0,
                f"top1_relevance": 0,
                f"topk_max_relevance@{self.k}": 0,
                f"holes": len(results),
                f"ratioholes": 1.0,
                f"total_document_results": len(results),
                f"total_groundtruth_documents": len(qrels)
            }

        # calculate the proportion of result docs with no ground truth label (holes)
        holes = self.__compute_holes(results.keys(), qrels.keys())
        ratioholes = holes / len(qrels)

        # sort each input set by label to get the ranking
        qrels_sorted_by_rank = sorted(qrels.items(), key=lambda x: x[1], reverse=True)
        results_sorted_by_rank = sorted(results.items(), key=lambda x: x[1], reverse=True)

        # find ground truth labels for the results set and ideal set
        result_docs_groundtruth_labels = [qrels[doc_id] if doc_id in qrels else 0 for (doc_id, _) in results_sorted_by_rank]
        ideal_docs_groundtruth_labels = [label for (_, label) in qrels_sorted_by_rank]

        # if none of the retrieved docs are labeled, report holes only
        if not any(result_docs_groundtruth_labels):
            return {
                f"ndcg@{self.k}": 0,
                f"xdcg@{self.k}": 0,
                f"fidelity": 0,
                f"top1_relevance": 0,
                f"topk_max_relevance@{self.k}": 0,
                f"holes": holes,
                f"ratioholes": ratioholes,
                f"total_document_results": len(results),
                f"total_groundtruth_documents": len(qrels)
            }

        return {
            f"ndcg@{self.k}": self.__compute_ndcg(result_docs_groundtruth_labels[:self.k], ideal_docs_groundtruth_labels[:self.k]),
            f"xdcg@{self.k}": self.__compute_xdcg(result_docs_groundtruth_labels[:self.k]),
            f"fidelity": self.__compute_fidelity(result_docs_groundtruth_labels, ideal_docs_groundtruth_labels),
            f"top1_relevance": result_docs_groundtruth_labels[0],
            f"topk_max_relevance@{self.k}": max(result_docs_groundtruth_labels[:self.k]),
            f"holes": holes,
            f"ratioholes": ratioholes,
            f"total_document_results": len(results),
            f"total_groundtruth_documents": len(qrels)
        }
