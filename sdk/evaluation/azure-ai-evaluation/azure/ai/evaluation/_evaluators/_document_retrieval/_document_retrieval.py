# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

import json
import math
import operator
from itertools import starmap
from azure.ai.evaluation._exceptions import EvaluationException
from typing import Dict, List, TypedDict, Optional


RetrievalGroundTruthDocument = TypedDict(
    'RetrievalGroundTruthDocument',
    {
        "document_id": str,
        "query_relevance_label": int
    }
)

RetrievedDocument = TypedDict(
    'RetrievedDocument',
    {
        "document_id": str,
        "relevance_score": float
    }
)


DocumentRetrievalMetrics = TypedDict(
    'DocumentRetrievalMetrics',
    {
        "ndcg@3": float,
        "ndcg@3_result": bool,
        "xdcg@3": float,
        "xdcg@3_result": bool,
        "fidelity": float,
        "fidelity_result": bool,
        "top1_relevance": float,
        "top1_relevance_result": bool,
        "top3_max_relevance": float,
        "top3_max_relevance_result": bool,
        "holes": int,
        "holes_result": bool,
        "holes_ratio": float,
        "holes_ratio_result": bool,
        "total_retrieved_documents": int,
        "total_groundtruth_documents": int
    }
)


class DocumentRetrievalEvaluator:
    """
    Calculate document retrieval metrics, such as NDCG, XDCG, Fidelity and Top K Relevance.
    """
    def __init__(self, *, groundtruth_label_min: int = 0, groundtruth_label_max: int = 4, threshold: Optional[dict] = None):
        super().__init__()
        self.k = 3
        self.xdcg_discount_factor = 0.6
        self.groundtruth_label_min = groundtruth_label_min
        self.groundtruth_label_max = groundtruth_label_max
        
        # The default threshold for metrics where higher numbers are better.
        self._threshold = {
            "ndcg@3": 0.5,
            "xdcg@3": 0.5,
            "fidelity": 0.5,
            "top1_relevance": 50,
            "top3_max_relevance": 50,
            "total_retrieved_documents": 50,
            "total_groundtruth_documents": 50
        }

        # Ideally, the number of holes should be zero.
        self._threshold_holes = {
            "holes": 0,
            "holes_ratio": 0
        }

        if threshold and not isinstance(threshold, dict):
            raise EvaluationException(
                f"Threshold must be a dictionary, got {type(threshold)}"
            )

        self._threshold.update(threshold)

    def _compute_holes(
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
    
    def _compute_ndcg(
        self,
        result_docs_groundtruth_labels: List[int],
        ideal_docs_groundtruth_labels: List[int],
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
    
    def _compute_xdcg(
        self,
        result_docs_groundtruth_labels: List[int]
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
    
    def _compute_fidelity(
        self,
        result_docs_groundtruth_labels: List[int],
        ideal_docs_groundtruth_labels: List[int],
    ) -> float:
        """
        Fidelity calculated over all documents retrieved from a search query.
        Fidelity measures how objectively good are all of the documents retrieved compared with all known good documents in the underlying data store.
        """
        def calculate_weighted_sum_by_rating(labels: List[int]) -> float:
            s = self.groundtruth_label_min + 1

            # get a count of each label
            label_counts = {str(i): 0 for i in range(s, self.groundtruth_label_max + 1)}

            for label in labels:
                if label >= s:
                    label_counts[str(label)] += 1

            sorted_label_counts = [x[1] for x in sorted(label_counts.items(), key=lambda x: x[0])]

            # calculate weights
            weights = [(math.pow(2, i+1) - 1) for i in range(s, self.groundtruth_label_max + 1)]

            # return weighted sum
            return sum(starmap(operator.mul, zip(sorted_label_counts, weights)))
        
        weighted_sum_by_rating_results = calculate_weighted_sum_by_rating(result_docs_groundtruth_labels)
        weighted_sum_by_rating_index = calculate_weighted_sum_by_rating(ideal_docs_groundtruth_labels)

        if weighted_sum_by_rating_index == 0:
            return math.nan

        return weighted_sum_by_rating_results / float(weighted_sum_by_rating_index)
    
    def _get_binary_result(self, **metrics) -> Dict[str, float]:
        result = {}

        for metric_name, metric_value in metrics.items():
            if metric_name in self._threshold.keys():
                result[f"{metric_name}_result"] = (metric_value >= self._threshold[metric_name])
                result[f"{metric_name}_threshold"] = self._threshold[metric_name]
                result[f"{metric_name}_lower_is_better"] = False

            elif metric_name in self._threshold_holes.keys():
                result[f"{metric_name}_result"] = (metric_value <= self._threshold_holes[metric_name])
                result[f"{metric_name}_threshold"] = self._threshold_holes[metric_name]
                result[f"{metric_name}_lower_is_better"] = True

            else:
                raise ValueError(f"No threshold set for metric '{metric_name}'")
            
        return result

    def __call__(self, *, retrieval_ground_truth: str, retrieved_documents: str) -> DocumentRetrievalMetrics:
        """
        Compute document retrieval metrics for documents retrieved from a search algorithm against a known set of ground truth documents.

        Input `retrieval_ground_truth` is a JSON-formatted string representation of `List[azure.ai.evaluation.RetrievalGroundTruthDocument]`, where each item of the list represents a ground-truth judgement for a particular document relative to a query.
        Input `retrieved_documents` is a JSON-formatted string representation of `List[azure.ai.evaluation.RetrievedDocument]`, where each item of the list represents a document scored by a search algorithm for the same query.

        Evaluation metrics calculated include NDCG@3, XDCG@3, Fidelity, Top K Relevance and Holes.
        """
        # input validation
        qrels = [RetrievalGroundTruthDocument(x) for x in json.loads(retrieval_ground_truth)]
        results = [RetrievedDocument(x) for x in json.loads(retrieved_documents)]

        if len(qrels) > 10000 or len(results) > 10000:
            raise ValueError("The results and ground-truth sets should contain no more than 10000 items.")

        # if the qrels are empty, no meaningful evaluation is possible
        if len(qrels) == 0:
            raise ValueError("No groundtruth labels were provided.")

        # if the results set is empty, results are all zero
        if len(results) == 0:
            metrics = {
                f"ndcg@{self.k}": 0.0,
                f"xdcg@{self.k}": 0.0,
                "fidelity": 0.0,
                "top1_relevance": 0.0,
                "top3_max_relevance": 0.0,
                "holes": 0,
                "holes_ratio": 0,
                "total_retrieved_documents": len(results),
                "total_groundtruth_documents": len(qrels)
            }
            binary_result = self._get_binary_result(**metrics)
            for k, v in binary_result.items():
                metrics[k] = v

            return DocumentRetrievalMetrics(**metrics)

        # flatten qrels and results to normal dictionaries
        qrels_lookup = {x["document_id"]: x["query_relevance_label"] for x in qrels}
        results_lookup = {x["document_id"]: x["relevance_score"] for x in results}

        # sort each input set by label to get the ranking
        qrels_sorted_by_rank = sorted(qrels_lookup.items(), key=lambda x: x[1], reverse=True)
        results_sorted_by_rank = sorted(results_lookup.items(), key=lambda x: x[1], reverse=True)

        # find ground truth labels for the results set and ideal set
        result_docs_groundtruth_labels = [qrels_lookup[doc_id] if doc_id in qrels_lookup else 0 for (doc_id, _) in results_sorted_by_rank]
        ideal_docs_groundtruth_labels = [label for (_, label) in qrels_sorted_by_rank]

        # calculate the proportion of result docs with no ground truth label (holes)
        holes = self._compute_holes(
            [x[0] for x in results_sorted_by_rank],
            [x[0] for x in qrels_sorted_by_rank]
        )
        holes_ratio = holes / float(len(results))

        # if none of the retrieved docs are labeled, report holes only
        if not any(result_docs_groundtruth_labels):
            metrics = {
                f"ndcg@{self.k}": 0,
                f"xdcg@{self.k}": 0,
                "fidelity": 0,
                "top1_relevance": 0,
                "top3_max_relevance": 0,
                "holes": holes,
                "holes_ratio": holes_ratio,
                "total_retrieved_documents": len(results),
                "total_groundtruth_documents": len(qrels)
            }
            binary_result = self._get_binary_result(**metrics)
            for k, v in binary_result.items():
                metrics[k] = v

            return DocumentRetrievalMetrics(**metrics)

        metrics = {
            f"ndcg@{self.k}": self._compute_ndcg(result_docs_groundtruth_labels[:self.k], ideal_docs_groundtruth_labels[:self.k]),
            f"xdcg@{self.k}": self._compute_xdcg(result_docs_groundtruth_labels[:self.k]),
            "fidelity": self._compute_fidelity(result_docs_groundtruth_labels, ideal_docs_groundtruth_labels),
            "top1_relevance": result_docs_groundtruth_labels[0],
            "top3_max_relevance": max(result_docs_groundtruth_labels[:self.k]),
            "holes": holes,
            "holes_ratio": holes_ratio,
            "total_retrieved_documents": len(results),
            "total_groundtruth_documents": len(qrels)
        }

        binary_result = self._get_binary_result(**metrics)
        for k, v in binary_result.items():
            metrics[k] = v
        
        return DocumentRetrievalMetrics(**metrics)
