# `cu-sdk-author-analyzer/scripts/` — quick reference

Two scripts that implement the create-an-analyzer loop using the typed
``ContentUnderstandingClient``. See [`../SKILL.md`](../SKILL.md) for the
full guided workflow.

| Script | What it does |
|---|---|
| [`extract_layout.py`](extract_layout.py) | Stage 1 — run ``prebuilt-documentSearch`` on each input and dump ``<doc>.layout.{json,md}``. |
| [`create_and_test.py`](create_and_test.py) | Stage 2 — validate schema → create analyzer → batch-test → stdout summary. |

### Stage 1: extract layout

```bash
python extract_layout.py \
    --input samples/sample_files/mixed_financial_docs.pdf \
    --output .local_only/layout/
```

Outputs:

```
.local_only/layout/
├── mixed_financial_docs.layout.json   # raw AnalysisResult dump
└── mixed_financial_docs.layout.md     # markdown rendering for VS Code
```

Open the ``.layout.md`` files in VS Code to see what text anchors the model
will use. Draft your ``fieldSchema`` against those anchors (the SKILL.md
walks you through this).

### Stage 2: create + test

```bash
python create_and_test.py \
    --schema .local_only/schemas/invoice_v1.json \
    --input samples/sample_files/mixed_financial_docs.pdf \
    --output .local_only/test_results/v1
```

Outputs:

```
.local_only/test_results/v1/
├── mixed_financial_docs.json
└── ... one JSON per input document
```

Plus a stdout summary listing per-field fill rate and the three
lowest-confidence ``(field, document)`` pairs.

By default the analyzer is **kept** in the resource. Pass ``--ephemeral`` to
``delete_analyzer`` at the end of the run.

### Exit codes

* ``0`` — every document analyzed successfully.
* ``1`` — at least one service-side failure.
* ``2`` — user error (schema validator failure, missing flags, bad input
  paths). The script exits before any service call in this case.

### Authentication

Same precedence as the SDK samples:

1. ``CONTENTUNDERSTANDING_KEY`` → ``AzureKeyCredential``.
2. Otherwise ``DefaultAzureCredential`` (typically ``az login``).
