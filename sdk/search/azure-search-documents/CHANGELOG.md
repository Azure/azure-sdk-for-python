# Release History

## 1.0.0b4 (Unreleased)

**Breaking Changes**

- Reorganized `SearchServiceClient` into `SearchIndexClient` & `SearchIndexerClient`    #11507
- Split searchindex.json and searchservice.json models and operations into separate namespaces #11508
- Renamed `edm` to `SearchFieldDataType`    #11511
- Now Search Synonym Map creation/update returns a model    #11514
- Renaming  #11565

  SearchIndexerDataSource -> SearchIndexerDataSourceConnection
  SearchField.SynonymMaps -> SearchField.SynonymMapNames
  SearchField.Analyzer -> SearchField.AnalyzerName
  SearchField.IndexAnalyzer -> SearchField.IndexAnalyzerName
  SearchField.SearchAnalyzer -> SearchField.SearchAnalyzerName
  SearchableField.SynonymMaps -> SearchableField.SynonymMapNames
  SearchableField.Analyzer -> SearchableField.AnalyzerName
  SearchableField.IndexAnalyzer -> SearchableField.IndexAnalyzerName
  SearchableField.SearchAnalyzer -> SearchableField.SearchAnalyzerName
  Similarity -> SimilarityAlgorithm
  Suggester -> SearchSuggester
  PathHierarchyTokenizerV2 -> PathHierarchyTokenizer
- Renamed DataSource methods to DataSourceConnection    #11693
  

## 1.0.0b3 (2020-05-04)

**Features**

- Add support for synonym maps operations #10830
- Add support for skillset operations #10832
- Add support of indexers operation #10836
- Add helpers for defining searchindex fields #10833

**Breaking Changes**

- `SearchIndexClient` renamed to `SearchClient`

## 1.0.0b2 (2020-04-07)

**Features**

- Added index service client    #10324
- Accepted an array of RegexFlags for PatternAnalyzer and PatternTokenizer  #10409

**Breaking Changes**

- Removed `SearchApiKeyCredential` and now using `AzureKeyCredential` from azure.core.credentials as key credential

## 1.0.0b1 (2020-03-10)

First release of Azure Search SDK for Python
