import { describe, expect, it } from "vitest";
import { filterAsync, flatMapAsync, includesEvery, includesNone, mapAsync } from "../src/array.js";
import { sleep } from "../src/sleep.js";

describe("array", () => {
  it("filterAsync", async () => {
    const input = [1, 2, 3];

    const result = await filterAsync(input, async (item, index) => {
      await sleep(index);
      return item === 1 || index === 1;
    });

    expect(result).toEqual([1, 2]);
  });

  it("flatMapAsync", async () => {
    const input = [1, 2, 3];

    const result = await flatMapAsync(input, async (item, index) => {
      await sleep(index);
      return [index, item * index];
    });

    expect(result).toEqual([0, 0, 1, 2, 2, 6]);
  });

  it("mapAsync", async () => {
    const input = [1, 2, 3];

    const result = await mapAsync(input, async (item, index) => {
      await sleep(index);
      return item * index;
    });

    expect(result).toEqual([0, 2, 6]);
  });

  it("includesEvery", () => {
    const input = [1, 2, 3];
    const values = [1, 2];

    expect(includesEvery(input, values)).toBe(true);
    expect(includesEvery(input, [4])).toBe(false);
    expect(includesEvery(input, [])).toBe(true);
  });

  it("includesNone", () => {
    const input = [1, 2, 3];
    const values = [4, 5];

    expect(includesNone(input, values)).toBe(true);
    expect(includesNone(input, [2])).toBe(false);
    expect(includesNone(input, [])).toBe(true);
  });
});
