import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ConsoleLogger, debugLogger, defaultLogger } from "../src/logger.js";

describe("logger", () => {
  /** @type {import("vitest").MockInstance} */ let debugSpy;
  /** @type {import("vitest").MockInstance} */ let errorSpy;
  /** @type {import("vitest").MockInstance} */ let logSpy;
  /** @type {import("vitest").MockInstance} */ let warnSpy;

  beforeEach(() => {
    debugSpy = vi.spyOn(console, "debug");
    errorSpy = vi.spyOn(console, "error");
    logSpy = vi.spyOn(console, "log");
    warnSpy = vi.spyOn(console, "warn");
  });

  afterEach(() => {
    debugSpy.mockRestore();
    errorSpy.mockRestore();
    logSpy.mockRestore();
    warnSpy.mockRestore();
  });

  it.each([
    ["defaultLogger", defaultLogger, false],
    ["debugLogger", debugLogger, true],
    ["new ConsoleLogger(isDebug: false)", new ConsoleLogger(false), false],
    ["new ConsoleLogger(isDebug: true)", new ConsoleLogger(true), true],
  ])("%s", (_name, logger, isDebug) => {
    expect(logger.isDebug()).toBe(isDebug);

    logger.info("test info");
    expect(logSpy).toBeCalledWith("test info");

    logger.warning("test warning");
    expect(warnSpy).toBeCalledWith("test warning");

    logger.error("test error");
    expect(errorSpy).toBeCalledWith("test error");

    logger.debug("test debug");
    if (isDebug) {
      expect(debugSpy).toBeCalledWith("test debug");
    } else {
      expect(debugSpy).toBeCalledTimes(0);
    }
  });
});
