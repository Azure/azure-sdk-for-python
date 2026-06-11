import { describe, expect, it } from "vitest";

import { add, Duration, formatDuration, getDuration, subtract } from "../src/time.js";

describe("time", () => {
  // Cover Duration, formatDuration, getDuration, add, and subtract in a single test
  it.each([
    [Duration.Millisecond, "00:00:00"],
    [Duration.Second, "00:00:01"],
    [Duration.Minute, "00:01:00"],
    [Duration.Hour, "01:00:00"],
    [Duration.Day, "24:00:00"],
    [Duration.Week, "168:00:00"],
  ])("formatDuration(%i)=%s", (duration, expected) => {
    const now = new Date();
    expect(formatDuration(getDuration(now, add(now, duration)))).toEqual(expected);
    expect(formatDuration(getDuration(now, subtract(now, duration)))).toEqual(expected);
  });
});
