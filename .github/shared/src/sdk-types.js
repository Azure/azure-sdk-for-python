import * as z from "zod";

/**
 * Represents supported SDK language identifiers.
 *
 * @readonly
 * @enum {"azure-sdk-for-go" | "azure-sdk-for-java" | "azure-sdk-for-js" | "azure-sdk-for-net" | "azure-sdk-for-python" | "azure-sdk-for-rust"}
 */
export const SdkName = Object.freeze({
  Go: "azure-sdk-for-go",
  Java: "azure-sdk-for-java",
  Js: "azure-sdk-for-js",
  Net: "azure-sdk-for-net",
  Python: "azure-sdk-for-python",
  Rust: "azure-sdk-for-rust",
});
/** @type {import("zod").ZodType<SdkName>} */
export const SdkNameSchema = z.enum(Object.values(SdkName));

/*
 * Data for the API view request.
 */
export const APIViewRequestDataSchema = z.object({ packageName: z.string(), filePath: z.string() });
/**
 * @typedef {import("zod").infer<typeof APIViewRequestDataSchema>} APIViewRequestData
 */

/**
 * Represents the result of the spec-gen-sdk generation process.
 */
export const SpecGenSdkArtifactInfoSchema = z.object({
  language: SdkNameSchema,
  result: z.string(),
  headSha: z.string(),
  prNumber: z.string().optional(),
  labelAction: z.boolean().optional(),
  isSpecGenSdkCheckRequired: z.boolean(),
  apiViewRequestData: z.array(APIViewRequestDataSchema),
});
/**
 * @typedef {import("zod").infer<typeof SpecGenSdkArtifactInfoSchema>} SpecGenSdkArtifactInfo
 */

/**
 * @typedef {{
 *   breakingChange: string | undefined,
 *   breakingChangeApproved: string | undefined,
 *   breakingChangeSuppression: string | undefined,
 *   breakingChangeSuppressionApproved: string | undefined
 * }} SdkLabelInfo
 */

/**
 * @typedef {Record<SdkName, SdkLabelInfo>} SdkLabels
 */

/**
 * SDK labels mapping for breaking change labels
 * @type {SdkLabels}
 * */
export const sdkLabels = {
  "azure-sdk-for-go": {
    breakingChange: "BreakingChange-Go-Sdk",
    breakingChangeApproved: "BreakingChange-Go-Sdk-Approved",
    breakingChangeSuppression: "BreakingChange-Go-Sdk-Suppression",
    breakingChangeSuppressionApproved: "BreakingChange-Go-Sdk-Suppression-Approved",
  },
  "azure-sdk-for-java": {
    breakingChange: undefined,
    breakingChangeApproved: undefined,
    breakingChangeSuppression: undefined,
    breakingChangeSuppressionApproved: undefined,
  },
  "azure-sdk-for-js": {
    breakingChange: "BreakingChange-JavaScript-Sdk",
    breakingChangeApproved: "BreakingChange-JavaScript-Sdk-Approved",
    breakingChangeSuppression: "BreakingChange-JavaScript-Sdk-Suppression",
    breakingChangeSuppressionApproved: "BreakingChange-JavaScript-Sdk-Suppression-Approved",
  },
  "azure-sdk-for-net": {
    breakingChange: undefined,
    breakingChangeApproved: undefined,
    breakingChangeSuppression: undefined,
    breakingChangeSuppressionApproved: undefined,
  },
  "azure-sdk-for-python": {
    breakingChange: "BreakingChange-Python-Sdk",
    breakingChangeApproved: "BreakingChange-Python-Sdk-Approved",
    breakingChangeSuppression: "BreakingChange-Python-Sdk-Suppression",
    breakingChangeSuppressionApproved: "BreakingChange-Python-Sdk-Suppression-Approved",
  },
  "azure-sdk-for-rust": {
    breakingChange: undefined,
    breakingChangeApproved: undefined,
    breakingChangeSuppression: undefined,
    breakingChangeSuppressionApproved: undefined,
  },
};
