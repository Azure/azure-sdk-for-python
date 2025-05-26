# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import math
import operator
from itertools import starmap
from typing import Any, Dict, List, TypedDict, Tuple, Optional, Union
from azure.ai.evaluation._evaluators._common import EvaluatorBase
from azure.ai.evaluation._exceptions import EvaluationException
from typing_extensions import override, overload


RetrievalGroundTruthDocument = TypedDict(
    "RetrievalGroundTruthDocument", {"document_id": str, "query_relevance_label": int}
)

RetrievedDocument = TypedDict(
    "RetrievedDocument", {"document_id": str, "relevance_score": float}
)


class DocumentRetrievalEvaluator(EvaluatorBase):
    """
    Calculate document retrieval metrics, such as NDCG, XDCG, Fidelity, Top K Relevance and Holes.

    .. admonition:: Example:

        .. literalinclude:: ../samples/evaluation_samples_evaluate.py
            :start-after: [START document_retrieval_evaluator]
            :end-before: [END document_retrieval_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call a DocumentRetrievalEvaluator

    .. admonition:: Example using Azure AI Project URL:
                
        .. literalinclude:: ../samples/evaluation_samples_evaluate_fdp.py
            :start-after: [START document_retrieval_evaluator]
            :end-before: [END document_retrieval_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize and call DocumentRetrievalEvaluator using Azure AI Project URL in following format 
                https://{resource_name}.services.ai.azure.com/api/projects/{project_name}
    
    .. admonition:: Example with Threshold:
        .. literalinclude:: ../samples/evaluation_samples_threshold.py
            :start-after: [START threshold_document_retrieval_evaluator]
            :end-before: [END threshold_document_retrieval_evaluator]
            :language: python
            :dedent: 8
            :caption: Initialize with threshold and call a DocumentRetrievalEvaluator.
    """

    def __init__(
        self,
        *,
        ground_truth_label_min: int = 0,
        ground_truth_label_max: int = 4,
        ndcg_threshold: Optional[float] = 0.5,
        xdcg_threshold: Optional[float] = 50.0,
        fidelity_threshold: Optional[float] = 0.5,
        top1_relevance_threshold: Optional[float] = 50.0,
        top3_max_relevance_threshold: Optional[float] = 50.0,
        total_retrieved_documents_threshold: Optional[int] = 50,
        total_ground_truth_documents_threshold: Optional[int] = 50
    ):
        super().__init__()
        self.k = 3
        self.xdcg_discount_factor = 0.6

        if ground_truth_label_min >= ground_truth_label_max:
            raise EvaluationException(
                "The ground truth label maximum must be strictly greater than the ground truth label minimum."
            )

        if not isinstance(ground_truth_label_min, int):
            raise EvaluationException(
                "The ground truth label minimum must be an integer value."
            )

        if not isinstance(ground_truth_label_max, int):
            raise EvaluationException(
                "The ground truth label maximum must be an integer value."
            )

        self.ground_truth_label_min = ground_truth_label_min
        self.ground_truth_label_max = ground_truth_label_max

        # The default threshold for metrics where higher numbers are better.
        self._threshold_metrics: Dict[str, Any] = {
            "ndcg@3": ndcg_threshold,
            "xdcg@3": xdcg_threshold,
            "fidelity": fidelity_threshold,
            "top1_relevance": top1_relevance_threshold,
            "top3_max_relevance": top3_max_relevance_threshold,
            "total_retrieved_documents": total_retrieved_documents_threshold,
            "total_ground_truth_documents": total_ground_truth_documents_threshold,
        }

        # Ideally, the number of holes should be zero.
        self._threshold_holes = {"holes": 0, "holes_ratio": 0}

    def _compute_holes(self, actual_docs: List[str], labeled_docs: List[str]) -> int:
        """
        The number of documents retrieved from a search query which have no provided ground-truth label.
        This metric is helpful for determining the accuracy of other metrics that are highly sensitive to missing ground-truth knowledge,
        such as NDCG, XDCG, and Fidelity.

        :param actual_docs: A list of retrieved documents' IDs.
        :type actual_docs: List[str]
        :param labeled_docs: A list of ideal documents' IDs.
        :type labeled: List[str]
        :return: The holes calculation result.
        :rtype: int
        """
        return len(set(actual_docs).difference(set(labeled_docs)))

    def _compute_ndcg(
        self,
        result_docs_groundtruth_labels: List[int],
        ideal_docs_groundtruth_labels: List[int],
    ) -> float:
        """NDCG (Normalized Discounted Cumulative Gain) calculated for the top K documents retrieved from a search query.
        NDCG measures how well a document ranking compares to an ideal document ranking given a list of ground-truth documents.
        
        :param result_docs_groundtruth_labels: A list of retrieved documents' ground truth labels.
        :type result_docs_groundtruth_labels: List[int]
        :param ideal_docs_groundtruth_labels: A list of ideal documents' ground truth labels.
        :type ideal_docs_groundtruth_labels: List[int]
        :return: The NDCG@K calculation result.
        :rtype: float
        """

        # Set the scoring function
        def calculate_dcg(relevance: float, rank: int):
            return (math.pow(2, relevance) - 1) / (math.log2(rank + 1))

        ranks = list(range(1, self.k + 1))
        dcg = sum(starmap(calculate_dcg, zip(result_docs_groundtruth_labels, ranks)))
        idcg = sum(starmap(calculate_dcg, zip(ideal_docs_groundtruth_labels, ranks)))
        ndcg = dcg / float(idcg)

        return ndcg

    def _compute_xdcg(self, result_docs_groundtruth_labels: List[int]) -> float:
        """XDCG calculated for the top K documents retrieved from a search query.
        XDCG measures how objectively good are the top K documents, discounted by their position in the list.
        
        :param result_docs_groundtruth_labels: A list of retrieved documents' ground truth labels.
        :type result_docs_groundtruth_labels: List[int]
        :return: The XDCG@K calculation result.
        :rtype: float
        """

        def calculate_xdcg_numerator(relevance, rank):
            return 25 * relevance * math.pow(self.xdcg_discount_factor, rank - 1)

        def calculate_xdcg_denominator(rank):
            return math.pow(self.xdcg_discount_factor, rank - 1)

        ranks = list(range(1, self.k + 1))
        xdcg_n = sum(
            starmap(
                calculate_xdcg_numerator, zip(result_docs_groundtruth_labels, ranks)
            )
        )
        xdcg_d = sum(map(calculate_xdcg_denominator, ranks))

        return xdcg_n / float(xdcg_d)

    def _compute_fidelity(
        self,
        result_docs_groundtruth_labels: List[int],
        ideal_docs_groundtruth_labels: List[int],
    ) -> float:
        """Fidelity calculated over all documents retrieved from a search query.
        Fidelity measures how objectively good are all of the documents retrieved compared with all known good documents in the underlying data store.
        
        :param result_docs_groundtruth_labels: A list of retrieved documents' ground truth labels.
        :type result_docs_groundtruth_labels: List[int]
        :param ideal_docs_groundtruth_labels: A list of ideal documents' ground truth labels.
        :type ideal_docs_groundtruth_labels: List[int]
        :return: The fidelity calculation result.
        :rtype: float
        """

        def calculate_weighted_sum_by_rating(labels: List[int]) -> float:
            # here we assume that the configured groundtruth label minimum translates to "irrelevant",
            # so we exclude documents with that label from the calculation.
            s = self.ground_truth_label_min + 1

            # get a count of each label
            label_counts = {str(i): 0 for i in range(s, self.ground_truth_label_max + 1)}

            for label in labels:
                if label >= s:
                    label_counts[str(label)] += 1

            sorted_label_counts = [
                x[1] for x in sorted(label_counts.items(), key=lambda x: x[0])
            ]

            # calculate weights
            weights = [
                (math.pow(2, i + 1) - 1)
                for i in range(s, self.ground_truth_label_max + 1)
            ]

            # return weighted sum
            return sum(starmap(operator.mul, zip(sorted_label_counts, weights)))

        weighted_sum_by_rating_results = calculate_weighted_sum_by_rating(
            result_docs_groundtruth_labels
        )
        weighted_sum_by_rating_index = calculate_weighted_sum_by_rating(
            ideal_docs_groundtruth_labels
        )

        if weighted_sum_by_rating_index == 0:
            return math.nan

        return weighted_sum_by_rating_results / float(weighted_sum_by_rating_index)

    def _get_binary_result(self, **metrics) -> Dict[str, float]:
        result: Dict[str, Any] = {}

        for metric_name, metric_value in metrics.items():
            if metric_name in self._threshold_metrics.keys():
                result[f"{metric_name}_result"] = "pass" if metric_value >= self._threshold_metrics[metric_name] else "fail"
                result[f"{metric_name}_threshold"] = self._threshold_metrics[metric_name]
                result[f"{metric_name}_higher_is_better"] = True

            elif metric_name in self._threshold_holes.keys():
                result[f"{metric_name}_result"] = "pass" if metric_value <= self._threshold_holes[metric_name] else "fail"
                result[f"{metric_name}_threshold"] = self._threshold_holes[metric_name]
                result[f"{metric_name}_higher_is_better"] = False

            else:
                raise ValueError(f"No threshold set for metric '{metric_name}'")

        return result

    def _validate_eval_input(
        self, eval_input: Dict
    ) -> Tuple[List[RetrievalGroundTruthDocument], List[RetrievedDocument]]:
        """Validate document retrieval evaluator inputs.

        :param eval_input: The input to the evaluation function.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Tuple[List[azure.ai.evaluation.RetrievalGroundTruthDocument], List[azure.ai.evaluation.RetrievedDocument]]
        """
        retrieval_ground_truth = eval_input.get("retrieval_ground_truth")
        retrieved_documents = eval_input.get("retrieved_documents")

        # if the qrels are empty, no meaningful evaluation is possible
        if not retrieval_ground_truth:
            raise EvaluationException(
                ("'retrieval_ground_truth' parameter must contain at least one item. "
                 "Check your data input to be sure that each input record has ground truth defined.")
            )

        qrels = []

        # validate the qrels to be sure they are the correct type and are bounded by the given configuration
        for qrel in retrieval_ground_truth:
            document_id = qrel.get("document_id")
            query_relevance_label = qrel.get("query_relevance_label")

            if document_id is None or query_relevance_label is None:
                raise EvaluationException(
                    (
                        "Invalid input data was found in the retrieval ground truth. "
                        "Ensure that all items in the 'retrieval_ground_truth' array contain "
                        "'document_id' and 'query_relevance_label' properties."
                    )
                )

            if not isinstance(query_relevance_label, int):
                raise EvaluationException(
                    "Query relevance labels must be integer values."
                )

            if query_relevance_label < self.ground_truth_label_min:
                raise EvaluationException(
                    (
                        "A query relevance label less than the configured minimum value was detected in the evaluation input data. "
                        "Check the range of ground truth label values in the input data and set the value of ground_truth_label_min to "
                        "the appropriate value for your data."
                    )
                )

            if query_relevance_label > self.ground_truth_label_max:
                raise EvaluationException(
                    (
                        "A query relevance label greater than the configured maximum value was detected in the evaluation input data. "
                        "Check the range of ground truth label values in the input data and set the value of ground_truth_label_max to "
                        "the appropriate value for your data."
                    )
                )

            qrels.append(qrel)

        # validate retrieved documents to be sure they are the correct type
        results = []

        if isinstance(retrieved_documents, list):
            for result in retrieved_documents:
                document_id = result.get("document_id")
                relevance_score = result.get("relevance_score")

                if document_id is None or relevance_score is None:
                    raise EvaluationException(
                        (
                            "Invalid input data was found in the retrieved documents. "
                            "Ensure that all items in the 'retrieved_documents' array contain "
                            "'document_id' and 'relevance_score' properties."
                        )
                    )

                if not isinstance(relevance_score, float) and not isinstance(
                    relevance_score, int
                ):
                    raise EvaluationException(
                        "Retrieved document relevance score must be a numerical value."
                    )

                results.append(result)

        if len(qrels) > 10000 or len(results) > 10000:
            raise EvaluationException(
                "'retrieval_ground_truth' and 'retrieved_documents' inputs should contain no more than 10000 items."
            )

        return qrels, results

    async def _do_eval(self, eval_input: Dict) -> Dict[str, float]:
        """Produce a document retrieval evaluation result.

        :param eval_input: The input to the evaluation function.
        :type eval_input: Dict
        :return: The evaluation result.
        :rtype: Dict[str, float]
        """
        qrels, results = self._validate_eval_input(eval_input)

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
                "total_ground_truth_documents": len(qrels),
            }
            binary_result = self._get_binary_result(**metrics)
            for k, v in binary_result.items():
                metrics[k] = v

            return metrics

        # flatten qrels and results to normal dictionaries
        qrels_lookup = {x["document_id"]: x["query_relevance_label"] for x in qrels}
        results_lookup = {x["document_id"]: x["relevance_score"] for x in results}

        # sort each input set by label to get the ranking
        qrels_sorted_by_rank = sorted(
            qrels_lookup.items(), key=lambda x: x[1], reverse=True
        )
        results_sorted_by_rank = sorted(
            results_lookup.items(), key=lambda x: x[1], reverse=True
        )

        # find ground truth labels for the results set and ideal set
        result_docs_groundtruth_labels = [
            qrels_lookup[doc_id] if doc_id in qrels_lookup else 0
            for (doc_id, _) in results_sorted_by_rank
        ]
        ideal_docs_groundtruth_labels = [label for (_, label) in qrels_sorted_by_rank]

        # calculate the proportion of result docs with no ground truth label (holes)
        holes = self._compute_holes(
            [x[0] for x in results_sorted_by_rank], [x[0] for x in qrels_sorted_by_rank]
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
                "total_ground_truth_documents": len(qrels),
            }
            binary_result = self._get_binary_result(**metrics)
            for k, v in binary_result.items():
                metrics[k] = v

            return metrics

        metrics = {
            f"ndcg@{self.k}": self._compute_ndcg(
                result_docs_groundtruth_labels[: self.k],
                ideal_docs_groundtruth_labels[: self.k],
            ),
            f"xdcg@{self.k}": self._compute_xdcg(
                result_docs_groundtruth_labels[: self.k]
            ),
            "fidelity": self._compute_fidelity(
                result_docs_groundtruth_labels, ideal_docs_groundtruth_labels
            ),
            "top1_relevance": result_docs_groundtruth_labels[0],
            "top3_max_relevance": max(result_docs_groundtruth_labels[: self.k]),
            "holes": holes,
            "holes_ratio": holes_ratio,
            "total_retrieved_documents": len(results),
            "total_ground_truth_documents": len(qrels),
        }

        binary_result = self._get_binary_result(**metrics)
        for k, v in binary_result.items():
            metrics[k] = v

        return metrics

    @overload
    def __call__(  # type: ignore
        self,
        *,
        retrieval_ground_truth: List[RetrievalGroundTruthDocument],
        retrieved_documents: List[RetrievedDocument],
    ) -> Dict[str, float]:
        """
        Compute document retrieval metrics for documents retrieved from a search algorithm against a known set of ground truth documents.

        Evaluation metrics calculated include NDCG@3, XDCG@3, Fidelity, Top K Relevance and Holes.

        :keyword retrieval_ground_truth: a list of ground-truth document judgements for a query, where each item in the list contains a unique document identifier and a query relevance label.
        :paramtype retrieval_ground_truth: List[azure.ai.evaluation.RetrievalGroundTruthDocument]
        :keyword retrieved_documents: a list of documents scored by a search algorithm for a query, where each item in the list contains a unique document identifier and a relevance score.
        :paramtype retrieved_documents: List[azure.ai.evaluation.RetrievedDocument]
        :return: The document retrieval metrics.
        :rtype: Dict[str, float]
        """

    @override
    def __call__(self, *args, **kwargs):
        """
        Compute document retrieval metrics for documents retrieved from a search algorithm against a known set of ground truth documents.

        Evaluation metrics calculated include NDCG@3, XDCG@3, Fidelity, Top K Relevance and Holes.

        :keyword retrieval_ground_truth: a list of ground-truth document judgements for a query, where each item in the list contains a unique document identifier and a query relevance label.
        :paramtype retrieval_ground_truth: List[azure.ai.evaluation.RetrievalGroundTruthDocument]
        :keyword retrieved_documents: a list of documents scored by a search algorithm for a query, where each item in the list contains a unique document identifier and a relevance score.
        :paramtype retrieved_documents: List[azure.ai.evaluation.RetrievedDocument]
        :return: The document retrieval metrics.
        :rtype: Dict[str, float]
        """
        return super().__call__(*args, **kwargs)
