import { describe, expect, it } from "vitest";
import { sleep } from "../src/sleep.js";

describe("sleep", () => {
  it.each([-1, 0, 1, 2])("sleep(%s)", async (ms) => {
    await expect(sleep(ms)).resolves.toBeUndefined();
  });
});
