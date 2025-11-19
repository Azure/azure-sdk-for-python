### Settings
``` yaml
input-file: C:\repos\azure-rest-api-specs\specification\search\data-plane\Azure.Search\preview\2025-11-01-preview\searchservice.json
output-folder: C:\repos\generated\searchservice
namespace: azure.search.documents.indexes
python: true
version-tolerant: false
```
```yaml
directive:
    - rename-model:
          from: ExhaustiveKnnVectorSearchAlgorithmConfiguration
          to: ExhaustiveKnnAlgorithmConfiguration
    - rename-model:
          from: HnswVectorSearchAlgorithmConfiguration
          to: HnswAlgorithmConfiguration
    - rename-model:
          from: PrioritizedFields
          to: SemanticPrioritizedFields
    - rename-model:
          from: SemanticSettings
          to: SemanticSearch
    - rename-model:
          from: ServiceStatistics
          to: SearchServiceStatistics
    - rename-model:
          from: ServiceCounters
          to: SearchServiceCounters
    - rename-model:
          from: ServiceLimits
          to: SearchServiceLimits
    - rename-model:
          from: Suggester
          to: SearchSuggester
    - rename-model:
          from: Similarity
          to: SimilarityAlgorithm
    - rename-model:
          from: ClassicSimilarity
          to: ClassicSimilarityAlgorithm
    - rename-model:
          from: BM25Similarity
          to: BM25SimilarityAlgorithm
    - rename-model:
          from: AMLParameters
          to: AzureMachineLearningParameters
    - rename-model:
          from: AMLVectorizer
          to: AzureMachineLearningVectorizer
    - where-model: PIIDetectionSkill
      rename-property:
        from: maskingCharacter
        to: mask
```