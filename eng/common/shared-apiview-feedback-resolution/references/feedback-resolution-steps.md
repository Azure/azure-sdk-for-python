# APIView Feedback Resolution Details

## Feedback Categories

- **Critical**: Breaking changes, security issues - must resolve
- **Suggestions**: Naming improvements, documentation - should resolve
- **Informational**: Style notes - optional

## Resolution Approaches

**If TypeSpec change needed:**

1. Run `azsdk_typespec_delegate_apiview_feedback` to apply AI-suggested fixes
2. Review the proposed TypeSpec changes
3. Apply changes to `client.tsp` (for SDK customizations) or `main.tsp` (for API changes)
4. Use TypeSpec customization for complex customizations

**If code-only fix needed:**

1. Apply the fix directly in the SDK repository
2. Regenerate SDK if needed

## Post-Resolution Steps

1. Run `azsdk_run_typespec_validation` to verify TypeSpec changes
2. Run `azsdk_package_generate_code` to regenerate SDK
3. Build and test the updated SDK
4. Update the SDK PR with changes
5. Re-check APIView for any new comments
6. Inform user to request re-review if needed
