import { describe, expect, it } from "vitest";

import { resolve } from "path";
import { Tag } from "../src/tag.js";

describe("Tag", () => {
  it("can be created with mock swaggers", async () => {
    const tag = new Tag("tag", ["swagger"]);

    expect(tag.name).toBe("tag");
    expect(tag.readme).toBeUndefined();

    expect(tag.inputFiles.size).toBe(1);
    const swagger = [...tag.inputFiles.values()][0];
    expect(swagger.path).toBe(resolve("swagger"));

    await expect(swagger.getRefs()).rejects.toThrowError(/Failed to read file for swagger/i);
  });

  it("sorts input files in toJSONAsync", async () => {
    const tag = new Tag("test-tag", ["b.json", "a.json"]);
    const json = /** @type {import('../src/tag.js').TagJSON} */ (await tag.toJSONAsync());
    const files = json.inputFiles.map(
      (f) => /** @type {import('../src/swagger.js').SwaggerJSON} */ (f).path,
    );
    expect(files.length).toBe(2);
    expect(files[0].localeCompare(files[1])).toBeLessThan(0);
  });
});
