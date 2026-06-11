import { mkdtemp, rm } from "fs/promises";
import os from "os";
import path from "path";
import { describe, expect, it } from "vitest";
import { getRootFolder } from "../src/simple-git.js";

describe("getRootFolder", () => {
  it("resolves to repo root from a nested folder", async () => {
    const testDir = __dirname;
    const calculatedRoot = await getRootFolder(testDir);
    const expectedRoot = path.resolve(path.join(__dirname, "..", "..", ".."));
    expect(calculatedRoot).toBe(expectedRoot);
  });

  it("throws when directory is not a git repository", async () => {
    const tempDir = await mkdtemp(path.join(os.tmpdir(), "non-git-"));
    await expect(getRootFolder(tempDir)).rejects.toThrow();
    await rm(tempDir, { recursive: true, force: true });
  });
});
