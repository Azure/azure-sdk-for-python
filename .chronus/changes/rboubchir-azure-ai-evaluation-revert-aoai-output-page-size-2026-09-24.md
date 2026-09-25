---
changeKind: breaking
packages:
  - azure-ai-evaluation
---

Removed the `aoai_output_items_page_size` option from `evaluate` and its input validation.
Callers using this option must remove it; it no longer configures native Azure OpenAI grader output retrieval.
Output-item requests again use a fixed page size of 100 and the existing OpenAI client's configured retry
policy, without adaptive page-size reduction or a separate SDK-level retry budget. All cursor pages are
still retrieved, and result ordering and missing-row alignment are unchanged.
