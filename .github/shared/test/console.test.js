import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { log } from "../src/console.js";

describe("console", () => {
  describe("log", () => {
    /** @type {import("vitest").MockInstance<typeof process.stdout.write>} */
    let writeSpy;

    beforeEach(() => {
      writeSpy = vi.spyOn(process.stdout, "write").mockReturnValue(true);
    });

    afterEach(() => {
      writeSpy.mockRestore();
    });

    it("writes a formatted line to stdout", async () => {
      await log("hello %s", "world");
      expect(writeSpy).toBeCalledWith("hello world\n");
    });

    it("formats multiple arguments like console.log", async () => {
      await log("a", "b", "c");
      expect(writeSpy).toBeCalledWith("a b c\n");
    });

    it("works with no arguments", async () => {
      await log();
      expect(writeSpy).toBeCalledWith("\n");
    });

    it("awaits drain when stdout has backpressure", async () => {
      writeSpy.mockReturnValueOnce(false);

      let resolved = false;
      const promise = log("backpressure test").then(() => {
        resolved = true;
      });

      // Should still be pending before drain
      expect(resolved).toBe(false);
      expect(writeSpy).toBeCalledWith("backpressure test\n");

      // Unblock backpressure
      process.stdout.emit("drain");
      await promise;

      expect(resolved).toBe(true);
    });
  });
});
