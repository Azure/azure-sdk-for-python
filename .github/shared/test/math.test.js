import { describe, expect, it } from "vitest";
import { toPercent } from "../src/math.js";

describe("math", () => {
  it.each([
    [0, "0%"],
    [0, "0.0%", 1],
    [0, "0.00%", 2],
    [0.0001, "0%"],
    [0.0001, "0.0%", 1],
    [0.0001, "0.01%", 2],
    [0.001, "0%"],
    [0.001, "0.1%", 1],
    [0.01, "1%"],
    [0.25, "25%"],
    [1.0 / 3, "33%"],
    [1.0 / 3, "33.3%", 1],
    [1.0 / 3, "33.33%", 2],
    [1.0 / 3, "33.333%", 3],
    [0.5, "50%"],
    [0.99, "99%"],
    [0.999, "100%"],
    [1, "100%"],
  ])("toPercent(%f)=%s", (value, expected, decimals = 0) => {
    expect(toPercent(value, decimals)).toEqual(expected);
  });
});
