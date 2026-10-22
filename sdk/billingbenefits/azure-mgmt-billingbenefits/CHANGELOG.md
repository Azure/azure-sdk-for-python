# Release History

## 1.0.0b2 (2026-03-31)

### Features Added

  - Enum `CommitmentGrain` added member `FULL_TERM`
  - Enum `CommitmentGrain` added member `UNKNOWN`
  - Model `Sku` added property `tier`
  - Model `Sku` added property `size`
  - Model `Sku` added property `family`
  - Model `Sku` added property `capacity`
  - Enum `Term` added member `P1M`
  - Added model `ApplicableMacc`
  - Added enum `ApplyDiscountOn`
  - Added model `AutomaticShortfallSuppressReason`
  - Added model `Award`
  - Added enum `BenefitType`
  - Added model `BenefitValidateModel`
  - Added model `BenefitValidateRequest`
  - Added model `BenefitValidateResponse`
  - Added model `BenefitValidateResponseProperty`
  - Added model `CatalogClaimsItem`
  - Added model `ChargeShortfallRequest`
  - Added model `ConditionalCredit`
  - Added model `ConditionalCreditContributor`
  - Added enum `ConditionalCreditEntityType`
  - Added model `ConditionalCreditMilestone`
  - Added model `ConditionalCreditMilestoneBase`
  - Added model `ConditionalCreditPatchRequest`
  - Added model `ConditionalCreditPatchRequestProperties`
  - Added model `ConditionalCreditProperties`
  - Added enum `ConditionalCreditStatus`
  - Added enum `ConditionalCreditsProvisioningState`
  - Added model `ConditionalCreditsValidateModel`
  - Added model `ConditionsItem`
  - Added model `Contributor`
  - Added model `ContributorConditionalCreditMilestone`
  - Added model `ContributorConditionalCreditProperties`
  - Added model `Credit`
  - Added model `CreditBreakdownItem`
  - Added model `CreditDimension`
  - Added enum `CreditExpirationPolicy`
  - Added model `CreditPatchProperties`
  - Added model `CreditPatchRequest`
  - Added model `CreditPolicies`
  - Added model `CreditProperties`
  - Added model `CreditReason`
  - Added enum `CreditRedemptionPolicy`
  - Added model `CreditSource`
  - Added model `CreditSourcePatchRequest`
  - Added model `CreditSourceProperties`
  - Added enum `CreditStatus`
  - Added model `CreditsValidateModel`
  - Added model `CustomPriceProperties`
  - Added model `Discount`
  - Added enum `DiscountAppliedScopeType`
  - Added enum `DiscountCombinationRule`
  - Added enum `DiscountEntityType`
  - Added model `DiscountPatchRequest`
  - Added model `DiscountPatchRequestProperties`
  - Added model `DiscountProperties`
  - Added enum `DiscountProvisioningState`
  - Added enum `DiscountRuleType`
  - Added enum `DiscountStatus`
  - Added enum `DiscountType`
  - Added model `DiscountTypeCustomPrice`
  - Added model `DiscountTypeCustomPriceMultiCurrency`
  - Added model `DiscountTypeProduct`
  - Added model `DiscountTypeProductFamily`
  - Added model `DiscountTypeProductSku`
  - Added model `DiscountTypeProperties`
  - Added enum `EnablementMode`
  - Added model `EntityTypeAffiliateDiscount`
  - Added model `EntityTypePrimaryDiscount`
  - Added model `FreeServices`
  - Added model `FreeServicesPatchRequest`
  - Added model `FreeServicesPatchRequestProperties`
  - Added model `FreeServicesProperties`
  - Added enum `FreeServicesStatus`
  - Added model `Macc`
  - Added enum `MaccEntityType`
  - Added model `MaccMilestone`
  - Added enum `MaccMilestoneStatus`
  - Added model `MaccModelProperties`
  - Added model `MaccPatchRequest`
  - Added model `MaccPatchRequestProperties`
  - Added enum `MaccStatus`
  - Added model `MaccValidateModel`
  - Added model `ManagedServiceIdentity`
  - Added enum `ManagedServiceIdentityType`
  - Added model `MarketSetPricesItems`
  - Added enum `MilestoneStatus`
  - Added model `Plan`
  - Added model `PriceGuaranteeProperties`
  - Added enum `PricingPolicy`
  - Added model `PrimaryConditionalCreditProperties`
  - Added model `ProxyResource`
  - Added model `ResourceSku`
  - Added model `SavingsPlanValidateModel`
  - Added model `SellerResourceListRequest`
  - Added model `SellerResourceListRequestProperties`
  - Added model `ServiceManagedIdentity`
  - Added enum `ServiceManagedIdentityType`
  - Added model `Shortfall`
  - Added enum `SkuTier`
  - Added model `TrackedResource`
  - Added model `UserAssignedIdentity`
  - Operation group `SavingsPlanOperations` added method `begin_update`
  - Added operation group `ApplicableMaccsOperations`
  - Added operation group `BenefitOperations`
  - Added operation group `ConditionalCreditContributorsOperations`
  - Added operation group `ConditionalCreditsOperations`
  - Added operation group `ContributorsOperations`
  - Added operation group `CreditsOperations`
  - Added operation group `DiscountOperations`
  - Added operation group `DiscountsOperations`
  - Added operation group `FreeServicesOperations`
  - Added operation group `MaccsOperations`
  - Added operation group `SellerResourceOperations`
  - Added operation group `SourcesOperations`

### Breaking Changes

  - This version introduces new hybrid models which have dual dictionary and model nature. Please follow https://aka.ms/azsdk/python/migrate/hybrid-models for migration.
  - For the method breakings, please refer to https://aka.ms/azsdk/python/migrate/operations for migration.
  - Renamed client `BillingBenefitsRP` to `BillingBenefitsMgmtClient`
  - Model `SavingsPlanOrderAliasModel` moved instance variable `display_name`, `savings_plan_order_id`, `provisioning_state`, `billing_scope_id`, `term`, `billing_plan`, `applied_scope_type`, `applied_scope_properties` and `commitment` under property `properties` whose type is `SavingsPlanOrderAliasProperties`
  - Deleted or renamed model `BillingInformation`
  - Deleted or renamed model `OperationResultError`
  - Deleted or renamed model `PricingCurrencyDuration`
  - Deleted or renamed model `PricingCurrencyTotal`
  - Deleted or renamed model `SavingsPlanPurchaseValidateRequest`
  - Method `SavingsPlanOperations.list_all` changed its parameter `orderby`/`refresh_summary`/`skiptoken`/`selected_state`/`take` from `positional_or_keyword` to `keyword_only`
  - Renamed method `SavingsPlanOperations.update` to `SavingsPlanOperations.begin_update`

### Other Changes

  - Deleted model `SavingsPlanModelList`/`SavingsPlanOrderModelList`/`BillingBenefitsRPOperationsMixin` which actually were not used by SDK users

## 1.0.0b1 (2022-12-14)

* Initial Release
