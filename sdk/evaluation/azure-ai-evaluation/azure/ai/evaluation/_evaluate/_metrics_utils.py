# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------

from __future__ import annotations

from typing import Dict, Iterable, Tuple

import pandas as pd

from .._constants import BINARY_AGGREGATE_SUFFIX, EVALUATION_PASS_FAIL_MAPPING

_PASS_VALUE = EVALUATION_PASS_FAIL_MAPPING[True].lower()
_FAIL_VALUE = EVALUATION_PASS_FAIL_MAPPING[False].lower()


def _normalize_binary_value(value: object) -> object:
    """Normalize pass/fail values for comparision."""

    if value is None:
        return None
    if isinstance(value, bool):
        return EVALUATION_PASS_FAIL_MAPPING[value].lower()
    if isinstance(value, str):
        return value.strip().lower()
    return value


def compute_pass_fail_statistics(
    df: pd.DataFrame, evaluator_names: Iterable[str]
) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, int]]:
    """Compute binary aggregates, pass rates, and dataset-level result counts.

    :param df: DataFrame containing only evaluator output columns (prefixed with ``outputs.``).
    :param evaluator_names: Evaluator names as provided by the caller (case preserved).
    :return: Tuple of (pass_rates, binary_metrics, result_counts).
    """

    total_rows = len(df.index)
    row_status = ["pass"] * total_rows

    pass_rates: Dict[str, float] = {}
    binary_metrics: Dict[str, float] = {}

    evaluator_name_list = list(evaluator_names)

    for evaluator_name in evaluator_name_list:
        prefix = f"outputs.{evaluator_name}."
        evaluator_columns = [col for col in df.columns if col.startswith(prefix)]

        if not evaluator_columns:
            alt_prefix = f"{evaluator_name}."
            evaluator_columns = [col for col in df.columns if col.startswith(alt_prefix)]
            if evaluator_columns:
                prefix = alt_prefix

        if not evaluator_columns:
            rate = 0.0
            pass_rates[f"{evaluator_name}.pass_rate"] = rate
            binary_metrics[f"{evaluator_name}.{BINARY_AGGREGATE_SUFFIX}"] = round(rate, 2)
            for idx in range(total_rows):
                row_status[idx] = "errored"
            continue

        row_missing_column = f"{prefix}row_missing"
        row_missing_series = (
            df[row_missing_column].fillna(False).astype(bool) if row_missing_column in df.columns else None
        )

        metric_columns = [col for col in evaluator_columns if col != row_missing_column]
        result_columns = [col for col in metric_columns if col.endswith("_result")]

        evaluator_metric_df = df[metric_columns] if metric_columns else pd.DataFrame(index=df.index)

        if result_columns:
            result_df = df[result_columns].applymap(_normalize_binary_value)

            valid_mask = ~result_df.isna()
            invalid_mask = valid_mask & ~result_df.isin({_PASS_VALUE, _FAIL_VALUE})
            error_mask = (~valid_mask.any(axis=1)) | invalid_mask.any(axis=1)
            fail_mask = (~error_mask) & result_df.eq(_FAIL_VALUE).any(axis=1)
            pass_mask = (~error_mask) & (~fail_mask)
        else:
            # No explicit pass/fail outputs. Treat rows with any non-null metric as pass
            if evaluator_metric_df.empty:
                row_has_values = pd.Series(False, index=df.index)
            else:
                row_has_values = evaluator_metric_df.notna().any(axis=1)
            error_mask = ~row_has_values
            fail_mask = pd.Series(False, index=df.index)
            pass_mask = row_has_values & ~error_mask

        if row_missing_series is not None:
            error_mask = error_mask | row_missing_series

        pass_count = int(pass_mask.sum())
        rate = pass_count / total_rows if total_rows else 0.0
        pass_rates[f"{evaluator_name}.pass_rate"] = rate
        binary_metrics[f"{evaluator_name}.{BINARY_AGGREGATE_SUFFIX}"] = round(rate, 2)

        if total_rows:
            error_array = error_mask.to_numpy(dtype=bool)
            fail_array = fail_mask.to_numpy(dtype=bool)

            for idx, is_error in enumerate(error_array):
                if is_error:
                    row_status[idx] = "errored"

            for idx, is_fail in enumerate(fail_array):
                if is_fail and row_status[idx] != "errored":
                    row_status[idx] = "failed"

    if total_rows:
        passed_rows = sum(status == "pass" for status in row_status)
        failed_rows = sum(status == "failed" for status in row_status)
        errored_rows = sum(status == "errored" for status in row_status)
    else:
        passed_rows = failed_rows = errored_rows = 0

    result_counts = {
        "result_counts.total": total_rows,
        "result_counts.passed": passed_rows,
        "result_counts.failed": failed_rows,
        "result_counts.errored": errored_rows,
    }

    return pass_rates, binary_metrics, result_counts
