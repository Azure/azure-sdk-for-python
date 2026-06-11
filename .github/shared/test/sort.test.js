import { describe, expect, it } from "vitest";
import { byDate, invert } from "../src/sort.js";

describe("byDate", () => {
  const input = [{ foo: "2025-01-01" }, { foo: "2023-01-01" }, { foo: "2024-01-01" }];

  it("ascending by default", () => {
    input.sort(byDate((s) => s.foo));

    // Value `undefined` always sorts to the end
    expect(input).toEqual([{ foo: "2023-01-01" }, { foo: "2024-01-01" }, { foo: "2025-01-01" }]);
  });

  it("descending with invert()", () => {
    input.sort(invert(byDate((s) => s.foo)));

    // Value `undefined` always sorts to the end
    expect(input).toEqual([{ foo: "2025-01-01" }, { foo: "2024-01-01" }, { foo: "2023-01-01" }]);
  });

  it.each([null, undefined, "invalid"])("invalid input: %s", (i) => {
    const input = [{ foo: "2025-01-01" }, { foo: "2024-01-01" }];
    const comparator = byDate((/** @type {{foo: string}} */ i) => i.foo);

    // Ensure base case doesn't throw
    input.sort(comparator);
    expect(input).toEqual([{ foo: "2024-01-01" }, { foo: "2025-01-01" }]);

    input[0].foo = /** @type {string} */ (i);
    expect(() => input.sort(comparator)).toThrowError(`Unable to parse '${i}' to a valid date`);
  });
});
