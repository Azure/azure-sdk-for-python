# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.
"""Parse ``resilience-contract.md`` § The matrix into typed records.

Used by ``test_contract_completeness.py`` to enforce that every
documented (row × applicable termination path) pair has a paired test
module under this directory.

The contract document is the source of truth — this parser reads the
matrix table from it (not a re-statement here). If the contract doc adds
a row, the parser sees it, the completeness test fails CI, and a new
test module must be added.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Disposition = Literal["re-invoke", "mark-failed", "no-recovery"]
TerminationPath = Literal["a", "b", "c"]


@dataclass(frozen=True)
class ContractRow:
    """One row of ``resilience-contract.md`` § The matrix.

    The matrix cell text is preserved verbatim so the completeness test
    can report it in failure messages.
    """

    row_number: int
    store: str  # "true" | "false"
    background: str  # "true" | "false" | "any"
    resilient_background: str  # "True" | "False" | "any"
    path_a_text: str
    path_b_text: str
    path_c_text: str

    @property
    def applicable_paths(self) -> tuple[TerminationPath, ...]:
        """Paths the matrix declares applicable for this row.

        All four rows have Path A and Path B contracts; only rows 1-3
        have Path C (row 4 says explicitly "no recovery applies", which
        IS a contract — the recovery code must NOT do anything for
        row 4 — and we test it).
        """
        return ("a", "b", "c")


def _contract_path() -> Path:
    """Locate ``resilience-contract.md`` relative to this test file.

    Layout::

        sdk/agentserver/azure-ai-agentserver-responses/
        ├── docs/
        │   └── resilience-contract.md           ← target (committed)
        └── tests/e2e/resilience_contract/        ← here
            └── _contract_parser.py

    From ``_contract_parser.py``:
      parents[0] = resilience_contract/
      parents[1] = e2e/
      parents[2] = tests/
      parents[3] = azure-ai-agentserver-responses/
    """
    here = Path(__file__).resolve()
    return here.parents[3] / "docs" / "resilience-contract.md"


def _extract_matrix_section(text: str) -> str:
    """Extract the markdown table under § The matrix."""
    # Match from the section header to the next ## heading.
    match = re.search(
        r"^## The matrix\s*\n(.*?)(?=^## )",
        text,
        flags=re.MULTILINE | re.DOTALL,
    )
    if match is None:
        raise ValueError(
            "Could not find '## The matrix' section in resilience-contract.md. "
            "The conformance suite cannot parse the contract."
        )
    return match.group(1)


def _parse_matrix_table(section: str) -> list[ContractRow]:
    """Parse the markdown table inside § The matrix.

    Expected column layout (per contract doc):

        | Row | store | background | resilient_background | Path A | Path B | Path C |
    """
    rows: list[ContractRow] = []
    in_table = False
    seen_header = False
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line.startswith("|"):
            # End of table once we leave the pipe-delimited block.
            if in_table:
                break
            continue
        in_table = True
        cells = [c.strip() for c in line.strip("|").split("|")]
        # Skip header + divider rows.
        if not seen_header:
            if cells[0].lower() in ("row", ""):
                seen_header = True
                continue
            # Divider like '|---|---|...'
            if all(set(c) <= set(":-") for c in cells):
                continue
        else:
            if all(set(c) <= set(":-") for c in cells):
                continue

        if len(cells) < 7:
            continue
        # The row-number cell uses bold or plain digits; strip backticks.
        row_text = cells[0].strip("` *")
        try:
            row_num = int(row_text)
        except ValueError:
            continue
        rows.append(
            ContractRow(
                row_number=row_num,
                store=cells[1].strip("` "),
                background=cells[2].strip("` "),
                resilient_background=cells[3].strip("` "),
                path_a_text=cells[4],
                path_b_text=cells[5],
                path_c_text=cells[6],
            )
        )
    if not rows:
        raise ValueError("Failed to parse any rows from § The matrix in resilience-contract.md.")
    return rows


def load_contract_rows() -> list[ContractRow]:
    """Read and parse ``resilience-contract.md`` § The matrix.

    The contract spec is maintained out-of-tree (it is not checked into
    ``sdk/agentserver/specs/``). Callers should treat
    :class:`FileNotFoundError` as a signal to skip the meta-test
    (e.g. ``pytest.skip(...)``) rather than fail; the per-cell tests in
    this package are the actual contract enforcers.
    """
    contract = _contract_path()
    if not contract.exists():
        raise FileNotFoundError(
            f"resilience-contract.md not found at expected path: {contract}. "
            "The contract spec is maintained out-of-tree — meta-completeness "
            "tests skip when it is unavailable. Per-cell tests in this "
            "package are unaffected."
        )
    text = contract.read_text(encoding="utf-8")
    return _parse_matrix_table(_extract_matrix_section(text))
