---
changeKind: feature
packages:
  - azure-ai-evaluation
---

Added the `aoai_output_items_page_size` option to `evaluate` for configuring the number of native Azure OpenAI
grader output items requested per HTTP response page. The default remains 100, all result pages are fetched, and
timed-out output-item requests retry the same page with progressively smaller page sizes.
