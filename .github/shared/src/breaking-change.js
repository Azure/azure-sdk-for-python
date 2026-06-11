/* v8 ignore start */

/**
 * Breaking change configuration and constants for Azure REST API specs
 * This file contains the single source of truth for all breaking change and versioning approval labels.
 *
 * Used across multiple tools in the Azure/azure-rest-api-specs repository.
 */

// All versioning approval labels in one place
export const VERSIONING_APPROVALS = {
  BENIGN: "Versioning-Approved-Benign",
  BUG_FIX: "Versioning-Approved-BugFix",
  PRIVATE_PREVIEW: "Versioning-Approved-PrivatePreview",
  BRANCH_POLICY_EXCEPTION: "Versioning-Approved-BranchPolicyException",
  PREVIOUSLY: "Versioning-Approved-Previously",
  RETIRED: "Versioning-Approved-Retired",
};

// All breaking change approval labels in one place
export const BREAKING_CHANGE_APPROVALS = {
  BENIGN: "BreakingChange-Approved-Benign",
  BUG_FIX: "BreakingChange-Approved-BugFix",
  USER_IMPACT: "BreakingChange-Approved-UserImpact",
  BRANCH_POLICY_EXCEPTION: "BreakingChange-Approved-BranchPolicyException",
  PREVIOUSLY: "BreakingChange-Approved-Previously",
  SECURITY: "BreakingChange-Approved-Security",
};

// Review required labels
export const REVIEW_REQUIRED_LABELS = {
  BREAKING_CHANGE: "BreakingChangeReviewRequired",
  VERSIONING: "VersioningReviewRequired",
};

// Extract values as arrays for validation and configuration
export const versioningApprovalValues = Object.values(VERSIONING_APPROVALS);
export const breakingChangeApprovalValues = Object.values(BREAKING_CHANGE_APPROVALS);
export const reviewRequiredLabelValues = Object.values(REVIEW_REQUIRED_LABELS);

// Type guard functions for runtime validation
/**
 * @param {string} value
 */
export function isValidVersioningApproval(value) {
  return versioningApprovalValues.includes(value);
}

/**
 * @param {string} value
 */
export function isValidBreakingChangeApproval(value) {
  return breakingChangeApprovalValues.includes(value);
}

/**
 * @param {string} value
 */
export function isReviewRequiredLabel(value) {
  return reviewRequiredLabelValues.includes(value);
}

// Configuration for different check types
export const breakingChangesCheckType = {
  SameVersion: {
    reviewRequiredLabel: REVIEW_REQUIRED_LABELS.VERSIONING,
    approvalPrefixLabel: "Versioning-Approved-*",
    approvalLabels: versioningApprovalValues,
  },
  CrossVersion: {
    reviewRequiredLabel: REVIEW_REQUIRED_LABELS.BREAKING_CHANGE,
    approvalPrefixLabel: "BreakingChange-Approved-*",
    approvalLabels: breakingChangeApprovalValues,
  },
};

// Check types
export const BREAKING_CHANGES_CHECK_TYPES = {
  SAME_VERSION: "SameVersion",
  CROSS_VERSION: "CrossVersion",
};
