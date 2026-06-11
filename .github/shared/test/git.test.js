import { describe, expect, it } from "vitest";
import { isFullGitSha } from "../src/git.js";
import { fullGitSha } from "./examples.js";

describe("git", () => {
  it.each([
    [undefined, false],
    [null, false],
    ["", false],
    // Short SHAs of 7 chars are not valid
    ["abc1234", false],
    // Invalid hex chars
    ["aBcDeG0189".repeat(4), false],
    ["aBcDe 0189".repeat(4), false],
    ["aBcDe_0189".repeat(4), false],
    // Valid
    ["aBcDeF0189".repeat(4), true],
    [fullGitSha, true],
  ])("isFullGitSha(%o) => %o", (string, result) => {
    // @ts-expect-error Testing invalid input types
    expect(isFullGitSha(string)).toBe(result);
  });
});
