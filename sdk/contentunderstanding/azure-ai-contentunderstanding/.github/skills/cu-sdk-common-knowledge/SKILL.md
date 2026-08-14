---
name: cu-sdk-common-knowledge
description: Domain knowledge for Azure AI Content Understanding. Use this skill to answer questions about Content Understanding concepts, analyzers, field schemas, API operations, and SDK usage. Always consult official documentation before answering.
---

# Azure AI Content Understanding Domain Knowledge

This skill provides domain knowledge for Azure AI Content Understanding, a multimodal AI service that extracts semantic content from documents, video, audio, and image files.

> **[COPILOT GUIDANCE]:** Always consult the official documentation first before answering user questions. Use `fetch_webpage` to read the relevant doc page when the reference material below is insufficient or may be outdated.
>
> When a user's question is broad or ambiguous, ask them to clarify:
> - "Which modality are you working with — documents, images, audio, or video?"
> - "Are you using a prebuilt analyzer, or building a custom one?"
> - "Are you asking about the Python SDK specifically, or the service in general?"

## Official Documentation

The authoritative source for Content Understanding is: **https://learn.microsoft.com/azure/ai-services/content-understanding/**

Always read the relevant page (via `fetch_webpage`) before answering if the reference material below does not cover the topic.

### Key Documentation Pages

| Topic | URL |
|-------|-----|
| **Overview** | https://learn.microsoft.com/azure/ai-services/content-understanding/overview |
| **What's new** | https://learn.microsoft.com/azure/ai-services/content-understanding/whats-new |
| **Content Understanding Studio** | https://learn.microsoft.com/azure/ai-services/content-understanding/quickstart/content-understanding-studio?tabs=portal%2Ccu-studio |
| **Service limits** | https://learn.microsoft.com/azure/ai-services/content-understanding/service-limits |
| **Region & language support** | https://learn.microsoft.com/azure/ai-services/content-understanding/language-region-support |
| **Prebuilt analyzers** | https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/prebuilt-analyzers |
| **Create custom analyzer** | https://learn.microsoft.com/azure/ai-services/content-understanding/tutorial/create-custom-analyzer?tabs=portal%2Cdocument&pivots=programming-language-python |
| **Document markdown** | https://learn.microsoft.com/azure/ai-services/content-understanding/document/markdown |
| **Document elements** | https://learn.microsoft.com/azure/ai-services/content-understanding/document/elements |
| **Video overview** | https://learn.microsoft.com/azure/ai-services/content-understanding/video/overview |
| **Video elements** | https://learn.microsoft.com/azure/ai-services/content-understanding/video/elements |
| **Audio overview** | https://learn.microsoft.com/azure/ai-services/content-understanding/audio/overview |
| **Image overview** | https://learn.microsoft.com/azure/ai-services/content-understanding/image/overview |
| **REST API reference** | https://learn.microsoft.com/rest/api/contentunderstanding/operation-groups |

> **Search tip:** If the above pages don't cover the user's question, search the doc tree at `https://learn.microsoft.com/azure/ai-services/content-understanding/`.

### Python SDK Resources

| Resource | Link |
|----------|------|
| **Python package on PyPI** | https://pypi.org/project/azure-ai-contentunderstanding/ |
| **Python SDK README** | https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/README.md |
| **Python SDK Samples** | https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/contentunderstanding/azure-ai-contentunderstanding/samples |

## Field-description rule: the two-stage pipeline

Custom analyzer extraction is a **two-stage pipeline**:

1. **Stage 1 — content extraction (OCR + layout).** The service reads the
   file and produces structured text plus layout metadata (sections, tables,
   headings). The original pixels are *not* what the LLM in stage 2 sees.
2. **Stage 2 — field extraction (LLM).** The LLM reads the stage-1 markdown
   and uses your field descriptions to identify values.

Implications for `fieldSchema.fields[*].description`:

✅ Reference **text content and structure**: labels (`"Invoice #"`),
section headings (`"Bill To"`), adjacent labels, alternative phrasings,
format examples.

❌ Do **not** reference visual appearance: colour, font, font size, bold or
italic, or "the box at the top-right" without text anchors.

Good description:

> "Invoice issue date, found near the 'Invoice #' label at the top right.
> May also be labelled 'Invoice Date', 'Date', or 'Issued'. Format is
> usually MM/DD/YYYY. Examples: '01/15/2024', 'January 15, 2024'."

Used by [`cu-sdk-author-analyzer`](../cu-sdk-author-analyzer/SKILL.md)
and [`cu-sdk-author-analyzer-classify-route`](../cu-sdk-author-analyzer-classify-route/SKILL.md).

## Choosing `baseAnalyzerId`

Every custom analyzer extends a built-in prebuilt analyzer via
`baseAnalyzerId`. Pick the row that matches the **modality** of the content
you're analyzing (documents, audio, video, image). Typos here are a common
first-time error; the local schema validator (in
[`_shared/schema_validator.py`](../_shared/)) rejects any value not in this
table.

| Content type | `baseAnalyzerId` |
|---|---|
| Documents (PDF, image of a page) | `prebuilt-document` |
| Audio (mp3, wav, m4a) | `prebuilt-audio` |
| Video (mp4, mov) | `prebuilt-video` |
| Image-only analyzer | `prebuilt-image` |

> ⚠️ **Only modality-level prebuilts are valid as `baseAnalyzerId` for
> custom analyzers.** `*Search` variants (`prebuilt-documentSearch`,
> `prebuilt-audioSearch`, `prebuilt-videoSearch`), task-specific prebuilts
> (`prebuilt-invoice`, `prebuilt-receipt`, `prebuilt-idDocument`), and
> `prebuilt-layout` are **not** accepted here — the service returns
> `InvalidBaseAnalyzerId`. Those prebuilts can still be called directly as
> standalone analyzers via
> `client.begin_analyze(analyzer_id="prebuilt-invoice", ...)`. See the
> [analyzer-reference docs](https://learn.microsoft.com/azure/ai-services/content-understanding/concepts/analyzer-reference#baseanalyzerid).

Used by [`cu-sdk-author-analyzer`](../cu-sdk-author-analyzer/SKILL.md)
(custom analyzer) and
[`cu-sdk-author-analyzer-classify-route`](../cu-sdk-author-analyzer-classify-route/SKILL.md)
(both inner extractors and the outer classifier).

## Classify-and-route rule

When using `config.contentCategories` to classify and route mixed-document
packets:

1. **Category descriptions follow the same text-anchored rule** as field
   descriptions. Describe each category by the text that appears on its
   pages (headings, labels), not by visual style.
2. **`config.enableSegment` must be `true`** so the classifier carves the
   packet into segments before routing each one.
3. **Inner analyzers must already exist** before the outer classifier is
   created.
4. **Category fill rate is per-category**, not packet-wide. A field that
   only appears in invoice segments should be evaluated against the number
   of invoice segments, not the total number of segments.
5. **No top-level `fieldSchema`** on the outer classifier. The outer
   analyzer's job is classification + routing only; field extraction
   belongs in the inner analyzers.

Used by [`cu-sdk-author-analyzer-classify-route`](../cu-sdk-author-analyzer-classify-route/SKILL.md).

## Related Skills

- `cu-sdk-setup` — Set up Python environment and run samples
- `cu-sdk-sample-run` — Run specific samples interactively
- `cu-sdk-author-analyzer` — Author + test a custom analyzer for one document type
- `cu-sdk-author-analyzer-classify-route` — Author + test a classify-and-route pipeline for mixed-document packets
