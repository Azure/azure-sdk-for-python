---
name: cu-sdk-generate-analyzer
description: Create and test a custom Azure AI Content Understanding analyzer for a folder of documents of a single type. Walks layout extraction → schema authoring → validation → batch test → stdout summary using the typed ContentUnderstandingClient. Use when the user wants to author a custom analyzer for invoices, contracts, forms, or any other single-type document set.
---

# Generate a Custom Analyzer (single document type)

Author a custom Content Understanding analyzer for one document type
end-to-end: extract layout, draft a field schema, validate locally, create the
analyzer, batch-test it on sample files, and read a quality summary.

The workflow uses the typed `ContentUnderstandingClient` shipped in this
package — the same client `samples/sample_create_analyzer.py` and
`samples/sample_analyze_binary.py` use.

> **[COPILOT INTERACTION MODEL]:** This skill is designed to be interactive.
> At each step marked with **[ASK USER]**, pause execution and prompt the user
> for input or confirmation before proceeding. Do NOT silently skip these
> prompts. Use the `ask_questions` tool when available.

> **[USE INSTEAD]:** If the user's packet contains **multiple different
> document types** (for example, an invoice, a bank statement, and a loan
> application in one PDF), route them to the
> [`cu-sdk-generate-analyzer-classify-route`](../cu-sdk-generate-analyzer-classify-route/SKILL.md)
> skill instead. This skill assumes one document type per analyzer.

## Prerequisites

- Python >= 3.9 with the SDK installed (see [`cu-sdk-setup`](../cu-sdk-setup/SKILL.md)).
- Virtual environment active.
- `.env` configured with `CONTENTUNDERSTANDING_ENDPOINT` (and optionally `CONTENTUNDERSTANDING_KEY`).
- Model deployments set up via `samples/sample_update_defaults.py`.

> **[ASK USER] Prerequisites check:**
> 1. "Is your virtual environment active and the SDK installed?" — if no, route to `cu-sdk-setup`.
> 2. "Is `CONTENTUNDERSTANDING_ENDPOINT` set in `.env`?" — if no, route to `cu-sdk-setup` Step 4.
> 3. "Have you run `sample_update_defaults.py` for this resource?" — if no, ask them to run it first.
> 4. "How many representative documents do you have, and where are they?" — fewer than 3 is fine but more is better for testing coverage.

## Package directory

```
sdk/contentunderstanding/azure-ai-contentunderstanding
```

## Scripts and templates

```
.github/skills/cu-sdk-generate-analyzer/
├── scripts/
│   ├── extract_layout.py     # Stage 1
│   ├── extract_layout.sh
│   ├── create_and_test.py    # Stage 2
│   └── create_and_test.sh
└── templates/
    └── schema_template.json  # Starter schema for Step 2
```

See [`scripts/README.md`](scripts/README.md) for a one-page reference.

## Workflow

### Step 1 — Extract layout for representative documents

The model behind Content Understanding sees the **text and structure** the
service extracts from your file, not the original pixels. Reviewing the
layout output is the fastest way to know what labels and headings you can
anchor your field descriptions to.

> **[ASK USER]** "Point me at one of your sample documents (or a folder of
> them). I'll run layout extraction so we can see what the model will be
> looking at."

Run:

```bash
python .github/skills/cu-sdk-generate-analyzer/scripts/extract_layout.py \
    --input <path-to-folder-or-file> \
    --output .local_only/layout/
```

This produces one `<doc>.layout.md` and one `<doc>.layout.json` per input.
Open the `.layout.md` file in VS Code and look for the **text anchors** you
want to extract from — labels (`"Invoice #:"`), section headings
(`"Bill To"`), table headers, etc.

> **Reference**: this is the same call pattern as
> [`samples/sample_analyze_binary.py`](../../../samples/sample_analyze_binary.py)
> using `prebuilt-documentSearch`.

### Step 2 — Draft a JSON field schema

Start from the template instead of writing from scratch:

```bash
mkdir -p .local_only/schemas
cp .github/skills/cu-sdk-generate-analyzer/templates/schema_template.json \
   .local_only/schemas/<name>_v1.json
```

Then edit `.local_only/schemas/<name>_v1.json`: set `baseAnalyzerId`, replace every
`REPLACE:` placeholder, and add/remove fields. The schema is a JSON object
with two required top-level keys:

- `baseAnalyzerId` — which prebuilt analyzer your custom analyzer extends. Use the table below.
- `fieldSchema.fields` — the named fields you want to extract.

#### Choosing `baseAnalyzerId`

| Content type | `baseAnalyzerId` |
|---|---|
| Documents (PDF, image of a page) | `prebuilt-document` |
| Documents needing rich semantic search content | `prebuilt-documentSearch` |
| Audio (mp3, wav, m4a) | `prebuilt-audio` |
| Audio needing semantic search | `prebuilt-audioSearch` |
| Video (mp4, mov) | `prebuilt-video` |
| Video needing semantic search | `prebuilt-videoSearch` |
| Image-only analyzer | `prebuilt-imageAnalyzer` |
| Invoices (built-in fields) | `prebuilt-invoice` |
| Receipts (built-in fields) | `prebuilt-receipt` |

> Typos here are a common first-time error. The local validator (Step 3) rejects any value not in this table.

#### Example single-type schema

```json
{
  "baseAnalyzerId": "prebuilt-document",
  "description": "Extract invoice header and totals.",
  "config": {
    "estimateFieldSourceAndConfidence": true,
    "returnDetails": true
  },
  "models": {
    "completion": "gpt-4.1",
    "embedding": "text-embedding-3-large"
  },
  "fieldSchema": {
    "name": "invoice_v1",
    "description": "Invoice header fields.",
    "fields": {
      "invoiceNumber": {
        "type": "string",
        "method": "extract",
        "description": "Invoice number printed near the 'Invoice #' label at the top of the page.",
        "estimateSourceAndConfidence": true
      },
      "totalAmount": {
        "type": "number",
        "method": "extract",
        "description": "Grand total at the bottom of the document; typically labelled 'Total' or 'Amount Due'. Excludes any 'Subtotal' value.",
        "estimateSourceAndConfidence": true
      }
    }
  }
}
```

> **Reference**: see
> [`samples/sample_create_analyzer.py`](../../../samples/sample_create_analyzer.py)
> for the typed-model equivalent. The script accepts a JSON dict directly
> (the SDK's `begin_create_analyzer` is overloaded for both).

> **Field-description rule (two-stage pipeline):** descriptions must reference
> **text content and structure** (labels, headings, neighbouring fields), not
> visual appearance (colour, font, size). See
> [`cu-sdk-common-knowledge`](../cu-sdk-common-knowledge/SKILL.md) §
> "two-stage pipeline".

### Step 3 — Validate the schema locally

```bash
python .github/skills/cu-sdk-generate-analyzer/scripts/create_and_test.py \
    --schema .local_only/schemas/invoice_v1.json \
    --input samples/sample_files/sample_invoice.pdf \
    --output .local_only/test_results/v1
```

The script runs the local validator first. If anything is wrong (unknown
`baseAnalyzerId`, missing `fieldSchema`, malformed entries) it exits with
code **2** *before* any service call.

### Step 4 — Read the stdout summary

After the script finishes you get something like:

```
========================================================================
[SUMMARY]

category: (single)  (3 document segments)
------------------------------------------
  field                          fill rate   avg conf
  invoiceNumber                  100.0%      0.962
  totalAmount                     66.7%      0.481

lowest-confidence fields:
  0.461  totalAmount  (mixed_financial_docs)
  0.732  invoiceNumber  (mixed_financial_docs)
========================================================================
```

### Step 5 — Clean up (optional)

By default the analyzer is kept in your resource so you can re-use it. Pass
`--ephemeral` to delete it at the end of a run:

```bash
python .github/skills/cu-sdk-generate-analyzer/scripts/create_and_test.py \
    --schema .local_only/schemas/invoice_v1.json \
    --input samples/sample_files/sample_invoice.pdf \
    --output .local_only/test_results/v1 \
    --ephemeral
```

> **Iteration helper — `--reuse`:** add `--reuse` to name the analyzer by a
> sha1 of its schema (`<schema-stem>_<hash[:8]>`) and skip creation when an
> analyzer with that ID already exists. Re-running with the same schema is
> a no-op on the create side, so you don't pile up stale analyzers while
> iterating. Edit the schema → hash changes → new analyzer is created.

For explicit lifecycle management see
[`samples/sample_get_analyzer.py`](../../../samples/sample_get_analyzer.py),
[`samples/sample_list_analyzers.py`](../../../samples/sample_list_analyzers.py),
[`samples/sample_update_analyzer.py`](../../../samples/sample_update_analyzer.py),
and
[`samples/sample_delete_analyzer.py`](../../../samples/sample_delete_analyzer.py).

## Exit codes

| Code | Meaning |
|---|---|
| `0` | All documents analyzed successfully. |
| `1` | At least one service-side failure (network, throttling, invalid response). |
| `2` | Local user error — schema validator failure, missing flag, bad input path. No service call was made. |

## Related skills

- [`cu-sdk-setup`](../cu-sdk-setup/SKILL.md) — install the SDK, configure env.
- [`cu-sdk-sample-run`](../cu-sdk-sample-run/SKILL.md) — run one reference sample.
- [`cu-sdk-common-knowledge`](../cu-sdk-common-knowledge/SKILL.md) — service concepts and field-description rules.
- [`cu-sdk-generate-analyzer-classify-route`](../cu-sdk-generate-analyzer-classify-route/SKILL.md) — multi-doc-type packets.
