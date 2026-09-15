# Release History

## 1.0.0b2 (2026-08-13)

### Features Added

  - Client `RelationshipsMgmtClient` added operation group `contains_relationships`
  - Added model `ContainsRelationship`
  - Added model `ContainsRelationshipProperties`
  - Added model `ServiceGroupMemberRelationshipPropertiesV2`
  - Model `DependencyOfRelationshipsOperations` added method `list_by_parent`
  - Model `ServiceGroupMemberRelationshipsOperations` added method `list_by_parent`
  - Added operation group `ContainsRelationshipsOperations`

### Breaking Changes

  - Method `RelationshipsMgmtClient.__init__` inserted a `positional_or_keyword` parameter `subscription_id`
  - Deleted or renamed model `ServiceGroupMemberRelationshipProperties`

## 1.0.0b1 (2026-04-02)

### Other Changes

  - Initial version