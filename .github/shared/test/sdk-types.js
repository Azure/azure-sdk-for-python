import { SdkName } from "../src/sdk-types.js";

/**
 * @typedef {import("../src/sdk-types.js").SpecGenSdkArtifactInfo} SpecGenSdkArtifactInfo
 */

/**
 * Create a mock SpecGenSdkArtifactInfo, filling unspecified properties with defaults.
 *
 * @param {Partial<import("../src/sdk-types.js").SpecGenSdkArtifactInfo>} [overrides]
 * @returns {SpecGenSdkArtifactInfo}
 */
export function createMockSpecGenSdkArtifactInfo(overrides = {}) {
  /** @type {SpecGenSdkArtifactInfo} */
  const defaults = {
    apiViewRequestData: [],
    headSha: "abc123",
    isSpecGenSdkCheckRequired: true,
    language: SdkName.Go,
    result: "test result",
  };

  return { ...defaults, ...overrides };
}
