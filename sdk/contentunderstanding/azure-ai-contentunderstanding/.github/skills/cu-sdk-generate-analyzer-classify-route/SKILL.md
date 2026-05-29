---
name: cu-sdk-generate-analyzer-classify-route
description: Create and test a classify-and-route Azure AI Content Understanding pipeline for packets that contain multiple document types (e.g. invoice + bank statement + loan application in one PDF). Walks per-type schema authoring → outer classifier wiring → batch test → category-aware stdout summary using the typed ContentUnderstandingClient. Use when the user has mixed-document packets.
---

# Generate a Classify-and-Route Analyzer (mixed document packets)

Build a classify-and-route pipeline: one **outer classifier analyzer** that
segments and labels a multi-document packet, plus one **inner extractor
analyzer per document type**. The packet flows through the outer analyzer
once; each segment is automatically routed to the matching inner analyzer
for field extraction.

> **[USE INSTEAD]:** If every page in the user's documents is the **same
> type** (only invoices, only contracts, etc.), use
> [`cu-sdk-generate-analyzer`](../cu-sdk-generate-analyzer/SKILL.md) instead.
> Classify-and-route is for **mixed** packets.

> **[COPILOT INTERACTION MODEL]:** At each step marked with **[ASK USER]**,
> pause execution and prompt the user before proceeding.

## Prerequisites

Required: venv active, SDK installed, `.env` with `CONTENTUNDERSTANDING_ENDPOINT`
(plus `CONTENTUNDERSTANDING_KEY` or `az login`), and `samples/sample_update_defaults.py`
run once for this resource. Full setup lives in [`cu-sdk-setup`](../cu-sdk-setup/SKILL.md).

> **[COPILOT] Probe first, then route on failure — do not duplicate setup logic here.**
>
> ```bash
> python -c "import sys; print('venv:', 'ok' if sys.prefix != sys.base_prefix else 'INACTIVE')"
> ( [ -f .env ] && grep -E '^CONTENTUNDERSTANDING_ENDPOINT=https?://' .env >/dev/null && echo 'endpoint: ok' ) || echo 'endpoint: MISSING'
> ( [ -f .env ] && grep -E '^CONTENTUNDERSTANDING_KEY=.+' .env >/dev/null && echo 'key: set' ) || echo 'key: empty'
> az account show >/dev/null 2>&1 && echo 'az: ok' || echo 'az: not logged in'
> ```
>
> | Failure | Route to |
> |---|---|
> | venv `INACTIVE` or `azure.ai.contentunderstanding` import fails | [`cu-sdk-setup`](../cu-sdk-setup/SKILL.md) Steps 2–3, then resume |
> | endpoint `MISSING` | [`cu-sdk-setup`](../cu-sdk-setup/SKILL.md) Step 4 (env vars), then resume |
> | endpoint `ok`, key `empty`, `az: not logged in` | [`cu-sdk-setup`](../cu-sdk-setup/SKILL.md) Step 4 auth section (run `az login` **or** add `CONTENTUNDERSTANDING_KEY` to `.env`), then resume |
> | All env checks pass but service calls fail with model errors | [`cu-sdk-setup`](../cu-sdk-setup/SKILL.md) Step 6 (`sample_update_defaults.py`), then resume |
> | All ok | ✅ Proceed to the Packet check below. |
>
> Never ask the user to paste an endpoint or API key into chat — they edit `.env` directly or run `az login`.

> **[ASK USER] Packet check:**
> 1. "Does each document in your packet contain more than one type of form (e.g. an invoice page followed by a bank statement page)?" — if no, route to `cu-sdk-generate-analyzer`.
> 2. "What types of documents appear in your packets?" — capture as the list of inner analyzers.

> **[ASK USER] Packet check:**
> 1. "Does each document in your packet contain more than one type of form (e.g. an invoice page followed by a bank statement page)?" — if no, route to `cu-sdk-generate-analyzer`.
> 2. "What types of documents appear in your packets?" — capture as the list of inner analyzers.

## Architecture

```
                       ┌──────────────────────────────┐
   mixed packet  ───►  │  outer (classifier) analyzer │
                       │  baseAnalyzerId: prebuilt-…  │
                       │  config.enableSegment: true  │
                       │  config.contentCategories:   │
                       │    invoice          ────────►│──┐
                       │    bank_statement   ────────►│──┼──► per-segment fields
                       │    loan_application ────────►│──┘
                       └──────────────────────────────┘
                                                       │
                       inner analyzers (1 per type)    │
                       ───────────────────────────     ▼
                       invoice extractor   ◄──── routes here for invoice pages
                       bank statement ext. ◄──── routes here for bank pages
                       loan app extractor  ◄──── routes here for loan pages
```

Key rules (also captured in
[`cu-sdk-common-knowledge`](../cu-sdk-common-knowledge/SKILL.md) §
"classify-and-route"):

1. **Category descriptions reference text anchors**, not visual cues
   (matches the two-stage pipeline rule for fields).
2. **`config.enableSegment` must be `true`** so the classifier can carve up
   the packet before routing.
3. **Inner analyzers must exist before** the outer classifier is created.
   The provided script handles ordering automatically.
4. **Category fill rate is per-category**, not packet-wide. The script's
   stdout summary uses the right denominator.

## Package directory

```
sdk/contentunderstanding/azure-ai-contentunderstanding
```

## Scripts and templates

```
.github/skills/cu-sdk-generate-analyzer-classify-route/
├── scripts/
│   ├── create_and_test_router.py
│   └── create_and_test_router.sh
└── templates/
    └── classifier_template.json   # Starter outer-classifier schema for Step 3
```

## Workflow

### Step 1 — Identify the document types

Run layout extraction (same as the single-type skill) on a representative
packet to see the section headings:

```bash
python .github/skills/cu-sdk-generate-analyzer/scripts/extract_layout.py \
    --input <packet.pdf> \
    --output .local_only/layout/
```

> **[ASK USER]** "Looking at `.local_only/layout/<packet>.layout.md`, what discrete
> document types do you see? List them in plain English (e.g. invoice, bank
> statement, loan application)."

### Step 2 — Draft one inner schema per type

Treat each type as a single-doc-type analyzer (pick `baseAnalyzerId` from
the table in
[`cu-sdk-common-knowledge` § Choosing `baseAnalyzerId`](../cu-sdk-common-knowledge/SKILL.md#choosing-baseanalyzerid),
then add `fieldSchema.fields`). Field descriptions follow the
[two-stage pipeline rule](../cu-sdk-common-knowledge/SKILL.md#field-description-rule-the-two-stage-pipeline)
— reference text and structure, never visual appearance. See
[`cu-sdk-generate-analyzer`](../cu-sdk-generate-analyzer/SKILL.md) Step 2 for
the full field-schema walkthrough.

> **Reference**:
> [`samples/sample_create_classifier.py`](../../../samples/sample_create_classifier.py)
> ships a complete worked example using `samples/sample_files/mixed_financial_docs.pdf`
> with three categories — Invoice, Bank_Statement, Loan_Application.

### Step 3 — Draft the outer classifier schema

The outer schema has **no** `fieldSchema`. Its job is classification + routing.
Start from the template:

```bash
mkdir -p .local_only/schemas
cp .github/skills/cu-sdk-generate-analyzer-classify-route/templates/classifier_template.json \
   .local_only/schemas/<name>_classifier_v1.json
```

Example after editing:
```json
{
  "baseAnalyzerId": "prebuilt-document",
  "description": "Classify mixed financial packets and route to per-type extractors.",
  "config": {
    "enableSegment": true,
    "omitContent": true,
    "contentCategories": {
      "invoice": {
        "description": "Pages whose top heading is 'Invoice'; contain an Invoice # label and a line-item table.",
        "analyzerId": "invoice"
      },
      "bank_statement": {
        "description": "Pages whose top heading is 'Bank Statement' or 'Account Statement'; contain Account Number and Statement Period labels.",
        "analyzerId": "bank_statement"
      },
      "loan_application": {
        "description": "Pages whose top heading is 'Loan Application'; contain Applicant Name and Loan Amount labels.",
        "analyzerId": "loan_application"
      }
    }
  },
  "models": {
    "completion": "gpt-4.1",
    "embedding": "text-embedding-3-large"
  }
}
```

The `analyzerId` value in each category is **an alias** that the script
resolves at runtime, matching the `--inner-schema alias=path` flags you
pass. Two exceptions skip alias resolution:

* Values starting with `prebuilt-` (e.g. `prebuilt-invoice`) are used as-is
  — no inner schema needed. Useful for routing a category at a service
  prebuilt extractor.
* Categories without an `analyzerId` at all are classification-only — the
  segment is labelled but no fields are extracted.

> **Why `omitContent: true`?** When omitted, the service also returns the
> raw, un-segmented document content as an extra entry in `contents`. That
> entry has no category, no fields, and shows up in the summary as a
> confusing `(uncategorized)` row. Setting `omitContent: true` removes it.

> **Category description rule:** describe each category in terms of text
> anchors (headings, labels) — never visual cues. Same reason as the
> field-description rule.

### Step 4 — Validate, create, and batch-test

```bash
python .github/skills/cu-sdk-generate-analyzer-classify-route/scripts/create_and_test_router.py \
    --outer-schema .local_only/schemas/classifier.json \
    --inner-schema invoice=.local_only/schemas/invoice.json \
    --inner-schema bank_statement=.local_only/schemas/bank_statement.json \
    --inner-schema loan_application=.local_only/schemas/loan_application.json \
    --input samples/sample_files/mixed_financial_docs.pdf \
    --output .local_only/test_results/v1
```

> **Shortcut — `--schema-dir`:** if your inner schema filenames match the
> outer-schema category aliases (e.g. `.local_only/schemas/invoice_v1.json` for category
> `invoice`), replace every `--inner-schema alias=path` with a single
> `--schema-dir .local_only/schemas/`. The script picks the newest matching file per
> alias (alphabetical sort, so `invoice_v2.json` wins over `invoice_v1.json`).

> **Iteration helper — `--reuse`:** add `--reuse` to name analyzers by a
> sha1 of their schema (`<stem>_<hash[:8]>`) and skip creation when an
> analyzer with that ID already exists. Re-running with the same schemas
> is a no-op on the create side, so you don't pile up stale analyzers while
> iterating. Edit a schema → hash changes → new analyzer is created.

The script:

1. Validates every schema (exits with code **2** if any fails — no service
   call made).
2. Errors out if the outer schema references an alias that has no matching
   `--inner-schema`, or if you supply an `--inner-schema` that no category
   uses.
3. Creates inner analyzers first, then patches and creates the outer
   classifier.
4. Analyzes every input file, writing one JSON per file under `--output`.
5. Prints a **category-aware** stdout summary (per-category fill rate
   uses each category's segment count, not the packet-wide total).

### Step 5 — Read the category-aware summary

Example output:

```
========================================================================
[SUMMARY] (category-aware)

category: bank_statement  (1 segments)
--------------------------------------
  field                          fill rate   avg conf
  AccountNumber                  100.0%      0.918
  StatementPeriod                100.0%      0.882

category: invoice  (1 segments)
-------------------------------
  field                          fill rate   avg conf
  InvoiceNumber                  100.0%      0.962
  TotalAmount                    100.0%      0.531

category: loan_application  (1 segments)
----------------------------------------
  field                          fill rate   avg conf
  ApplicantName                  100.0%      0.875
  LoanAmount                     100.0%      0.799

lowest-confidence fields across all categories:
  0.531  [invoice] TotalAmount  (mixed_financial_docs)
  0.799  [loan_application] LoanAmount  (mixed_financial_docs)
  0.875  [loan_application] ApplicantName  (mixed_financial_docs)
========================================================================
```

For each input document the script writes two files into `--output`:

- `<doc>.json` — full `AnalysisResult` with all per-segment fields and grounding.
- `<doc>.llm.md` — the same result rendered via the SDK's
  [`to_llm_input`](../../../samples/sample_create_classifier.py) helper.
  For classify-and-route, the helper expands each classified segment into
  its own block with the **category in the YAML front matter**, separated by
  `*****` dividers — drop it into an LLM prompt or skim it in VS Code.

> **Template comment keys**: any key whose name starts with `_`
> (e.g. `_comment`, `_optional_returnDetails`) is stripped from both the
> outer and inner schemas before the request body is sent. Use them freely
> as inline documentation.

> **`models.completion` for inner schemas**: each inner schema (which has a
> `fieldSchema`) needs `models.completion` set unless the resource has
> defaults configured via
> [`samples/sample_update_defaults.py`](../../../samples/sample_update_defaults.py).
> `create_and_test_router.py` prints a `[WARN]` per inner schema that is
> missing it, before any service call.

### Step 6 — Clean up (optional)

By default the script leaves both the outer classifier **and** all inner
analyzers in your resource so you can re-use them. Pass `--ephemeral` to
delete all of them at the end of the run.

## Exit codes

| Code | Meaning |
|---|---|
| `0` | Every document analyzed successfully. |
| `1` | At least one service-side failure. |
| `2` | Local user error — schema validation, missing inner alias, bad path. No service call made. |

## Related skills

- [`cu-sdk-generate-analyzer`](../cu-sdk-generate-analyzer/SKILL.md) — single doc type.
- [`cu-sdk-common-knowledge`](../cu-sdk-common-knowledge/SKILL.md) — service concepts, two-stage pipeline, `baseAnalyzerId` table, classify-and-route rules.
- [`cu-sdk-sample-run`](../cu-sdk-sample-run/SKILL.md) — run individual SDK samples (e.g. `sample_create_classifier.py`) for deeper reference.
- [`cu-sdk-setup`](../cu-sdk-setup/SKILL.md) — install the SDK, configure env.
