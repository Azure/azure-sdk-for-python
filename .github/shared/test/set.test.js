import { describe, expect, it } from "vitest";
import { equals, intersect } from "../src/set.js";

describe("set", () => {
  it.each([
    // not instanceof Set: null, undefined
    [null, null, false],
    [undefined, undefined, false],
    [null, undefined, false],
    [null, [], false],
    [undefined, [], false],
    // not instanceof Set: number, string, object, array
    [1, 1, false],
    ["a", "a", false],
    [{}, {}, false],
    [[], [], false],
    // different lengths
    [new Set(), new Set([1]), false],
    [new Set([1]), new Set([1, 2]), false],
    [new Set([1, 2]), new Set([1, 2, 3]), false],
    // different elements
    [new Set([1]), new Set([2]), false],
    [new Set([1, 2]), new Set([1, 3]), false],
    [new Set([1, 2]), new Set([2, 3]), false],
    [new Set([1, 2, 3]), new Set([2, 3, 4]), false],
    // sets with same elements, size >= 0
    [new Set(), new Set(), true],
    [new Set([1]), new Set([1]), true],
    [new Set([1, 2]), new Set([1, 2]), true],
    [new Set([1, 2, 3]), new Set([1, 2, 3]), true],
  ])("equals(%o, %o) = %o", (set1, set2, expected) => {
    // @ts-expect-error testing runtime behavior of invalid types
    expect(equals(set1, set2)).toBe(expected);
    // @ts-expect-error testing runtime behavior of invalid types
    expect(equals(set2, set1)).toBe(expected);
  });

  it.each([
    [[], [], []],
    [[1, 2, 3], [], []],
    [
      [1, 2, 3],
      [2, 3, 4],
      [2, 3],
    ],
    [[1, 2, 3], [4, 5, 6], []],
    [
      [1, 2, 3],
      [1, 2, 3],
      [1, 2, 3],
    ],
    [
      ["a", "b", "c"],
      ["b", "c", "d"],
      ["b", "c"],
    ],
  ])(
    "intersect(%o, %o) = %o",
    (
      /** @type {(string|number)[]} */ a,
      /** @type {(string|number)[]} */ b,
      /** @type {(string|number)[]} */ result,
    ) => {
      const setA = new Set(a);
      const setB = new Set(b);
      const setResult = new Set(result);

      // Check both orders, result should be same
      expect(intersect(setA, setB)).toEqual(setResult);
      expect(intersect(setB, setA)).toEqual(setResult);
    },
  );
});
