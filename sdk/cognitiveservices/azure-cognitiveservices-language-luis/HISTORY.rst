.. :changelog:

Release History
===============

0.5.0 (2019-11-08)
++++++++++++++++++

*Authoring*

**Features**

- Model HierarchicalChildEntity has a new parameter children
- Model HierarchicalChildEntity has a new parameter instance_of
- Model PatternFeatureInfo has a new parameter enabled_for_all_models
- Model PhraseListFeatureInfo has a new parameter enabled_for_all_models
- Model PhraselistCreateObject has a new parameter enabled_for_all_models
- Model PhraselistUpdateObject has a new parameter enabled_for_all_models
- Model JSONModelFeature has a new parameter enabled_for_all_models
- Model ChildEntity has a new parameter children
- Model ChildEntity has a new parameter instance_of
- Model ChildEntity has a new parameter type_id
- Model ChildEntity has a new parameter readable_type
- Model FeatureInfoObject has a new parameter enabled_for_all_models
- Model LuisApp has a new parameter phraselists
- Model LuisApp has a new parameter hierarchicals
- Model HierarchicalModel has a new parameter features
- Added operation ModelOperations.get_intent_features
- Added operation ModelOperations.replace_intent_features
- Added operation ModelOperations.update_entity_child
- Added operation ModelOperations.add_entity_child
- Added operation ModelOperations.delete_entity_feature
- Added operation ModelOperations.delete_intent_feature
- Added operation ModelOperations.replace_entity_features
- Added operation ModelOperations.get_entity_features
- Added operation FeaturesOperations.add_intent_feature
- Added operation FeaturesOperations.add_entity_feature

**Breaking changes**

- Operation ModelOperations.update_hierarchical_entity has a new signature
- Operation ModelOperations.add_entity has a new signature
- Model LuisApp no longer has parameter model_features
- Removed operation ModelOperations.add_hierarchical_entity
- Removed operation ModelOperations.add_composite_entity
- Removed operation ModelOperations.add_hierarchical_entity_child
- Removed operation ModelOperations.update_entity
- Removed operation FeaturesOperations.list_application_version_pattern_features

0.4.0 (2019-10-25)
++++++++++++++++++

**Features**

- Added operation PredictionOperations.get_slot_prediction
- Added operation PredictionOperations.get_version_prediction

**Breaking changes**
- Parameter score of model Sentiment is now required
- Model EntityLabel no longer has parameter role
- Model EntityLabel no longer has parameter role_id
- Model JSONEntity no longer has parameter role
- Model EntityLabelObject no longer has parameter role
- Model CompositeEntityModel has a new signature
- Removed operation PredictionOperations.resolve
  
0.3.1 (2019-09-11)
++++++++++++++++++

*Authoring*

**Bugfixes**

- Removed duplicate enum

0.3.0 (2019-08-27)
++++++++++++++++++

*Authoring*

**Features**

- Model EntityLabelObject has a new parameter role
- Model JSONEntity has a new parameter role
- Model EntityLabel has a new parameter role
- Model EntityLabel has a new parameter role_id

0.2.0 (2019-04-26)
++++++++++++++++++

*Authoring*

**Features**

- Model ProductionOrStagingEndpointInfo has a new parameter failed_regions
- Model EndpointInfo has a new parameter failed_regions
- Added operation PatternOperations.list_patterns
- Added operation PatternOperations.list_intent_patterns
- Added operation ModelOperations.list_pattern_any_entity_roles
- Added operation ModelOperations.list_regex_entity_infos
- Added operation ModelOperations.list_pattern_any_entity_infos
- Added operation ModelOperations.list_composite_entity_roles
- Added operation ModelOperations.list_entity_suggestions
- Added operation ModelOperations.list_hierarchical_entity_roles
- Added operation ModelOperations.list_prebuilt_entity_roles
- Added operation ModelOperations.list_entity_roles
- Added operation ModelOperations.list_regex_entity_roles
- Added operation ModelOperations.list_intent_suggestions
- Added operation ModelOperations.list_custom_prebuilt_entity_roles
- Added operation ModelOperations.list_closed_list_entity_roles
- Added operation FeaturesOperations.list_application_version_pattern_features
- Added operation AppsOperations.package_published_application_as_gzip
- Added operation AppsOperations.package_trained_application_as_gzip
- Added operation group SettingsOperations
- Added operation group AzureAccountsOperations

**Breaking changes**

- Operation AppsOperations.update_settings has a new signature
- Operation AppsOperations.delete has a new signature
- Operation AppsOperations.publish has a new signature
- Model ApplicationPublishObject no longer has parameter region
- Removed operation PatternOperations.get_intent_patterns
- Removed operation PatternOperations.get_patterns
- Removed operation ModelOperations.get_regex_entity_roles
- Removed operation ModelOperations.get_custom_prebuilt_entity_roles
- Removed operation ModelOperations.get_pattern_any_entity_infos
- Removed operation ModelOperations.get_prebuilt_entity_roles
- Removed operation ModelOperations.get_composite_entity_roles
- Removed operation ModelOperations.get_pattern_any_entity_roles
- Removed operation ModelOperations.get_entity_roles
- Removed operation ModelOperations.get_regex_entity_infos
- Removed operation ModelOperations.get_entity_suggestions
- Removed operation ModelOperations.get_closed_list_entity_roles
- Removed operation ModelOperations.get_intent_suggestions
- Removed operation ModelOperations.get_hierarchical_entity_roles
- Model ApplicationSettingUpdateObject has a new signature

*Runtime*

**Features**

- Model LuisResult has a new parameter connected_service_result

0.1.0 (2018-08-15)
++++++++++++++++++

* Initial Release
