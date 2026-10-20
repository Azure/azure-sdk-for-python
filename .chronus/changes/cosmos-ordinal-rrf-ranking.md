---
changeKind: fix
packages:
  - sdk/cosmos/azure-cosmos
---

Fixed hybrid-search reciprocal rank fusion (RRF) to use ordinal component ranks by default, so equal component scores receive distinct ranks. Component-score ties use the numeric document portion of `_rid` in the component query's sort direction, and final fused-score ties use numeric document `_rid` descending. Set `AZURE_COSMOS_HYBRID_SEARCH_USE_COMPETITION_RANKING=true` to opt into competition ranking (for example, `1, 2, 2, 2, 5` rather than ordinal `1, 2, 3, 4, 5`).
