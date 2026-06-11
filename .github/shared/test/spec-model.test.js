import { randomUUID } from "crypto";
import { readdir } from "fs/promises";
import { dirname, isAbsolute, join, resolve } from "path";
import { describe, expect, it } from "vitest";
import { mapAsync } from "../src/array.js";
import { ConsoleLogger } from "../src/logger.js";
import { SpecModel } from "../src/spec-model.js";
import { Duration } from "../src/time.js";
import { repoRoot } from "./repo.js";

/**
 * @typedef {import('../src/readme.js').ReadmeJSON} ReadmeJSON
 * @typedef {import('../src/spec-model.js').SpecModelJSON} SpecModelJSON
 * @typedef {import('../src/swagger.js').SwaggerJSON} SwaggerJSON
 * @typedef {import('../src/tag.js').TagJSON} TagJSON
 */

const options = { logger: new ConsoleLogger(/*debug*/ true) };

describe("SpecModel", () => {
  it("can be created with mock folder", async () => {
    const specModel = new SpecModel("foo");
    expect(specModel.folder).toBe(resolve("foo"));

    await expect(specModel.getReadmes()).rejects.toThrowError(/no such file or directory/i);
  });

  it("returns cached spec model", () => {
    const path = randomUUID();

    const specModel1 = new SpecModel(path);
    const specModel2 = new SpecModel(path);

    expect(specModel1).toBe(specModel2);
  });

  it("returns spec model", async () => {
    const folder = resolve(
      __dirname,
      "fixtures/getSpecModel/specification/contosowidgetmanager/resource-manager",
    );

    const specModel = new SpecModel(folder, options);

    expect(specModel.toString()).toContain("SpecModel");
    expect(specModel.folder).toBe(folder);

    const readmes = [...(await specModel.getReadmes()).values()];
    expect(readmes.length).toBe(1);

    const readme = readmes[0];
    expect(readme.toString()).toContain("Readme");
    expect(readme.path).toBe(resolve(folder, "readme.md"));
    expect(readme.specModel).toBe(specModel);

    await expect(readme.getGlobalConfig()).resolves.toEqual({
      "openapi-type": "arm",
      "openapi-subtype": "rpaas",
      tag: "package-2021-11-01",
    });

    const tags = [...(await readme.getTags()).values()].sort((a, b) =>
      a.name.localeCompare(b.name),
    );
    expect(tags.length).toBe(2);

    expect(tags[0].toString()).toContain("Tag");
    expect(tags[0].name).toBe("package-2021-10-01-preview");
    expect(tags[0].readme).toBe(readme);

    const inputFiles0 = [...tags[0].inputFiles.values()];
    expect(inputFiles0.length).toBe(1);
    expect(inputFiles0[0].toString()).toContain("Swagger");
    expect(inputFiles0[0].path).toBe(
      resolve(folder, "Microsoft.Contoso/preview/2021-10-01-preview/contoso.json"),
    );
    expect(inputFiles0[0].tag).toBe(tags[0]);

    const refs0 = [...(await inputFiles0[0].getRefs()).values()].sort((a, b) =>
      a.path.localeCompare(b.path),
    );

    expect(refs0.length).toBe(1);

    expect(refs0[0].path).toBe(
      resolve(
        dirname(inputFiles0[0].path),
        "../../../../../common-types/resource-management/v5/types.json",
      ),
    );
    expect(refs0[0].tag).toBe(tags[0]);

    expect(tags[1].name).toBe("package-2021-11-01");
    const inputFiles1 = [...tags[1].inputFiles.values()];
    expect(inputFiles1.length).toBe(1);
    expect(inputFiles1[0].path).toBe(
      resolve(folder, "Microsoft.Contoso/stable/2021-11-01/contoso.json"),
    );
    expect(inputFiles1[0].tag).toBe(tags[1]);

    const jsonDefault = /** @type {SpecModelJSON} */ (await specModel.toJSONAsync());
    const readmeJSONDefault = /** @type {ReadmeJSON} */ (jsonDefault.readmes[0]);
    const readmePathDefault = readmeJSONDefault.path;
    expect(isAbsolute(readmePathDefault)).toBe(true);
    expect(
      /** @type {SwaggerJSON} */ (/** @type {TagJSON} */ (readmeJSONDefault.tags[0]).inputFiles[0])
        .refs,
    ).toBeUndefined();

    const jsonRefsRelative = /** @type {SpecModelJSON} */ (
      await specModel.toJSONAsync({
        includeOperations: true,
        includeRefs: true,
        relativePaths: true,
      })
    );
    const readmeJSONRelative = /** @type {ReadmeJSON} */ (jsonRefsRelative.readmes[0]);
    const readmePathRelative = readmeJSONRelative.path;
    expect(isAbsolute(readmePathRelative)).toBe(false);
    expect(
      /** @type {SwaggerJSON}*/ (/** @type {TagJSON} */ (readmeJSONRelative.tags[0]).inputFiles[0])
        .operations,
    ).toBeDefined();
    expect(
      /** @type {SwaggerJSON}*/ (/** @type {TagJSON} */ (readmeJSONRelative.tags[0]).inputFiles[0])
        .refs,
    ).toBeDefined();
  });

  it("sorts readmes in toJSONAsync", async () => {
    const folder = resolve(__dirname, "fixtures/getSpecModel/specification/multi-readme");

    const specModel = new SpecModel(folder, options);
    const json = /** @type {import('../src/spec-model.js').SpecModelJSON} */ (
      await specModel.toJSONAsync()
    );

    expect(json.readmes.length).toBe(2);
    const paths = json.readmes.map(
      (r) => /** @type {import('../src/readme.js').ReadmeJSON} */ (r).path,
    );
    expect(paths[0].localeCompare(paths[1])).toBeLessThan(0);
  });

  it("uses strings for tag names and doesn't parse Date object", async () => {
    const folder = resolve(__dirname, "fixtures/getSpecModel/specification/yaml-date-parsing");

    const specModel = new SpecModel(folder, options);

    const readme = [...(await specModel.getReadmes()).values()][0];

    const globalConfig = await readme.getGlobalConfig();

    const tag = /** @type {unknown} */ (globalConfig["tag"]);

    expect(tag).not.toBeTypeOf("object");

    expect(tag).toBeTypeOf("string");
    expect(tag).toBe("2022-12-01");
  });

  it("throws when a tag is defined more than once", async () => {
    // data-plane/readme.md defines the `package-2022-12-01` tag twice.
    const folder = resolve(
      __dirname,
      "fixtures/getSpecModel/specification/contosowidgetmanager/data-plane",
    );

    const specModel = new SpecModel(folder, options);

    const readmes = await specModel.getReadmes();

    await expect(
      mapAsync([...readmes.values()], async (r) => await r.getTags()),
    ).rejects.toThrowError(/multiple.*tag/i);

    await expect(specModel.toJSONAsync()).rejects.toThrowError(/multiple.*tag/i);

    await expect(specModel.toJSONAsync({ embedErrors: true })).resolves.toMatchObject({
      readmes: [
        {
          error: /** @type {unknown} */ (expect.stringMatching(/multiple.*tag/i)),
        },
      ],
    });
  });

  describe("getAffectedReadmeTags", () => {
    it("returns affected readme tags", async () => {
      const folder = resolve(
        __dirname,
        "fixtures/getAffectedReadmeTags/specification/contosowidgetmanager",
      );

      const specModel = new SpecModel(folder, options);

      const swaggerPath = resolve(
        folder,
        "resource-manager/Microsoft.Contoso/stable/2021-11-01/contoso.json",
      );

      const affectedReadmeTags = await specModel.getAffectedReadmeTags(swaggerPath);

      expect(affectedReadmeTags.size).toBe(1);

      const readmePath = [...affectedReadmeTags.keys()][0];
      expect(readmePath).toBe(resolve(folder, "resource-manager/readme.md"));

      const tagNames = [...[...affectedReadmeTags.values()][0].keys()];
      expect(tagNames.length).toBe(1);

      expect(tagNames[0]).toBe("package-2021-11-01");
    });

    it("returns affected readme tags for multiple tags", async () => {
      const folder = resolve(__dirname, "fixtures/getAffectedSwaggers/specification/1");

      const specModel = new SpecModel(folder, options);

      const swaggerPath = resolve(folder, "data-plane/shared/shared.json");

      const affectedReadmeTags = await specModel.getAffectedReadmeTags(swaggerPath);

      expect(affectedReadmeTags.size).toBe(1);

      const readmePath = [...affectedReadmeTags.keys()][0];
      expect(readmePath).toBe(resolve(folder, "data-plane/readme.md"));

      const tagNames = [...[...affectedReadmeTags.values()][0].keys()].sort();

      expect(tagNames.length).toBe(2);
      expect(tagNames[0]).toBe("tag-1");
      expect(tagNames[1]).toBe("tag-2");
    });

    it("throws when an input-file is not found", async () => {
      const folder = resolve(
        __dirname,
        "fixtures/getAffectedReadmeTags/specification/input-file-not-found",
      );
      const specModel = new SpecModel(folder, options);

      await expect(
        specModel.getAffectedReadmeTags(resolve(folder, "data-plane/a.json")),
      ).rejects.toThrowError(/Failed to read file for swagger/i);
    });

    it("throws when an input-file is invalid JSON", async () => {
      const folder = resolve(
        __dirname,
        "fixtures/getAffectedReadmeTags/specification/input-file-invalid-json",
      );
      const specModel = new SpecModel(folder, options);

      await expect(
        specModel.getAffectedReadmeTags(resolve(folder, "data-plane/a.json")),
      ).rejects.toThrowError(`SyntaxError: Unexpected token 'i', "invalid json" is not valid JSON`);

      await expect(specModel.toJSONAsync({ includeRefs: true })).rejects.toThrowError(
        `SyntaxError: Unexpected token 'i', "invalid json" is not valid JSON`,
      );

      await expect(
        specModel.toJSONAsync({ embedErrors: true, includeRefs: true }),
      ).resolves.toMatchObject({
        readmes: [
          {
            tags: [
              {
                inputFiles: [
                  {
                    error: /** @type {unknown} */ (
                      expect.stringContaining(
                        "Unexpected token 'i', \"invalid json\" is not valid JSON",
                      )
                    ),
                  },
                ],
                name: "package-2021-11-01",
              },
            ],
          },
        ],
      });
    });
  });

  describe("getAffectedSwaggers", () => {
    const folder = resolve(__dirname, "fixtures/getAffectedSwaggers/specification/1");

    const specModel = new SpecModel(folder, options);

    it("returns directly referenced swagger", async () => {
      const swaggerPath = resolve(folder, "data-plane/a.json");

      const actual = [...(await specModel.getAffectedSwaggers(swaggerPath)).keys()].sort();

      const expected = ["data-plane/a.json"].map((p) => resolve(folder, p)).sort();

      expect(actual).toEqual(expected);
    });

    it("throws when swagger file is not found", async () => {
      const swaggerPath = resolve(folder, "data-plane/not-found.json");

      await expect(specModel.getAffectedSwaggers(swaggerPath)).rejects.toThrowError(
        /not found in specModel/i,
      );
    });

    it("returns correct swaggers for one layer of dependencies", async () => {
      const swaggerPath = resolve(folder, "data-plane/nesting/b.json");

      const actual = [...(await specModel.getAffectedSwaggers(swaggerPath)).keys()].sort();

      const expected = ["data-plane/a.json", "data-plane/nesting/b.json"]
        .map((p) => resolve(folder, p))
        .sort();

      expect(actual).toEqual(expected);
    });

    it("returns correct swaggers for two layers of dependencies", async () => {
      const swaggerPath = resolve(folder, "data-plane/c.json");

      const actual = [...(await specModel.getAffectedSwaggers(swaggerPath)).keys()].sort();

      const expected = ["data-plane/a.json", "data-plane/nesting/b.json", "data-plane/c.json"]
        .map((p) => resolve(folder, p))
        .sort();

      expect(actual).toEqual(expected);
    });

    it("returns correct swaggers for three layers of dependencies", async () => {
      const swaggerPath = resolve(folder, "data-plane/d.json");

      const actual = [...(await specModel.getAffectedSwaggers(swaggerPath)).keys()].sort();

      const expected = [
        "data-plane/a.json",
        "data-plane/nesting/b.json",
        "data-plane/c.json",
        "data-plane/d.json",
      ]
        .map((p) => resolve(folder, p))
        .sort();

      expect(actual).toEqual(expected);
    });

    it("returns correctly for multiple shared dependencies", async () => {
      const swaggerPath = resolve(folder, "data-plane/shared/shared.json");

      const actual = [...(await specModel.getAffectedSwaggers(swaggerPath)).keys()].sort();

      const expected = [
        "data-plane/a.json",
        "data-plane/nesting/b.json",
        "data-plane/c.json",
        "data-plane/d.json",
        "data-plane/shared/shared.json",
        "data-plane/e.json",
      ]
        .map((p) => resolve(folder, p))
        .sort();

      expect(actual).toEqual(expected);
    });
  });
});

// TODO: Update tests for new object-oriented API

// Stress test the parser against all specs in the specification/ folder. This
// is a long-running test and should be run manually. To run this test, remove
// the '.skip' from the describe block. Put '.skip' back in when done or this
// test may fail unexpectedly in the future.
describe.skip("Parse readmes", () => {
  it("Does not produce exceptions", { timeout: 30 * Duration.Minute }, async ({ expect }) => {
    const excludeFolders = [
      "authorization", // specification/authorization/resource-manager/readme.md defines has duplicate tags including 'package-2020-10-01'
      "azureactivedirectory", // specification/azureactivedirectory/resource-manager/readme.md has duplicate tags including 'package-preview-2020-07'
      "cost-management", // specification/cost-management/resource-manager/readme.md has duplicate tags including 'package-2019-01'
      "migrate", // specification/migrate/resource-manager/readme.md has duplicate tags including 'package-migrate-2023-04'
      "quota", // specification/quota/resource-manager/readme.md has duplicate tags including 'package-2023-02-01'
      "redisenterprise", // specification/redisenterprise/resource-manager/readme.md has duplicate tags including 'package-2024-02'
      "security", // specification/security/resource-manager/readme.md has duplicate tags including 'package-2021-07-preview-only'
      "confidentialledger", // data-plane/readme.md tag 'package-2022-04-20-preview-ledger' points to a swagger file that doesn't exist
      "network", // network takes a long time to evaluate
      "servicenetworking", // servicenetworking includes a swagger file which references a file that doesn't exist
    ];

    // List all folders under specification/
    const folders = await readdir(join(repoRoot, "specification"), {
      withFileTypes: true,
    });
    const services = folders
      .filter((f) => f.isDirectory() && !excludeFolders.includes(f.name))
      .map((f) => f.name);
    for (const folder of services) {
      // Folders are listed in alphabetical order, when running this function
      // iteratively over all service folders, a value can be placed in in this
      // condition to skip folders that appear before a given folder. This means
      // you won't have to wait for tests to run over all folders that have
      // previously passed.
      if (folder < "000") {
        console.log(`Skipping service: ${folder}`);
        continue;
      }

      console.log(`Testing service: ${folder}`);
      const specModel = new SpecModel(`specification/${folder}`, options);

      expect(specModel).toBeDefined();
    }
  });

  it("runs properly against specific services", { timeout: 30 * Duration.Minute }, ({ expect }) => {
    /** @type {string[]} */
    const folders = [
      // Fill in services to test here
    ];
    for (const folder of folders) {
      console.log(`Testing service: ${folder}`);
      const specModel = new SpecModel(`specification/${folder}`, options);

      expect(specModel).toBeDefined();
    }
  });
});

describe("getSwaggers", () => {
  it("should return all swagger files from tags", async () => {
    const folder = resolve(
      __dirname,
      "fixtures/getSpecModel/specification/contosowidgetmanager/resource-manager",
    );

    const specModel = new SpecModel(folder, options);
    const swaggers = await specModel.getSwaggers();

    expect(swaggers.length).toBeGreaterThan(0);

    // Verify that all returned items are Swagger instances
    expect(swaggers.every((s) => s.constructor.name === "Swagger")).toBe(true);

    // Verify that swagger files have the expected properties
    const swagger = swaggers[0];
    expect(swagger.path).toBeDefined();
    expect(swagger.versionKind).toBeDefined();
  });

  it("should return swaggers from multiple readmes and tags", async () => {
    // Using a fixture that has multiple readme files
    const folder = resolve(
      __dirname,
      "fixtures/getSpecModel/specification/contosowidgetmanager/resource-manager",
    );
    const specModel = new SpecModel(folder, options);

    const swaggers = await specModel.getSwaggers();

    // Should find swaggers from all readmes
    expect(swaggers.length).toBeGreaterThan(0);

    // Each swagger should have a valid path
    swaggers.forEach((swagger) => {
      expect(swagger.path).toBeDefined();
      expect(typeof swagger.path).toBe("string");
      expect(swagger.path.length).toBeGreaterThan(0);
    });
  });

  it("should handle empty directories gracefully", async () => {
    // Test with a minimal or empty spec model
    const tempFolder = resolve(
      __dirname,
      "fixtures/getSpecModel/specification/contosowidgetmanager/resource-manager",
    );
    const specModel = new SpecModel(tempFolder, options);

    const swaggers = await specModel.getSwaggers();

    // Should return an array even if empty
    expect(Array.isArray(swaggers)).toBe(true);
  });

  it("should preserve tag relationships", async () => {
    const folder = resolve(
      __dirname,
      "fixtures/getSpecModel/specification/contosowidgetmanager/resource-manager",
    );

    const specModel = new SpecModel(folder, options);
    const swaggers = await specModel.getSwaggers();

    // Each swagger should have a tag reference
    swaggers.forEach((swagger) => {
      expect(swagger.tag).toBeDefined();
      if (swagger.tag) {
        expect(swagger.tag.name).toBeDefined();
        expect(typeof swagger.tag.name).toBe("string");
      }
    });
  });

  it("should work with swagger fixtures", async () => {
    const folder = resolve(__dirname, "fixtures/swagger");

    const specModel = new SpecModel(folder, options);
    const swaggers = await specModel.getSwaggers();

    // Expected paths as complete normalized paths
    const expectedSwaggerPaths = [
      "specification/common-types/resource-management/v2/types.json",
      "specification/common-types/resource-management/v3/types.json",
      "specification/common-types/resource-management/v3/types.json",
      "specification/common-types/resource-management/v3/types.json",
      "specification/servicelinker/resource-manager/Microsoft.ServiceLinker/preview/2023-04-01-preview/servicelinker.json",
      "specification/servicelinker/resource-manager/Microsoft.ServiceLinker/preview/2024-07-01-preview/servicelinker.json",
      "specification/servicelinker/resource-manager/Microsoft.ServiceLinker/stable/2022-05-01/servicelinker.json",
      "specification/servicelinker/resource-manager/Microsoft.ServiceLinker/stable/2024-04-01/servicelinker.json",
      "specification/servicelinker/resource-manager/Microsoft.ServiceLinker/stable/2024-04-01/test.json",
    ];

    // Sort swaggers by path to ensure consistent order
    expect(swaggers.sort((a, b) => a.path.localeCompare(b.path)).map((s) => s.path)).toEqual(
      expectedSwaggerPaths.map((p) => resolve(folder, p)),
    );
  });
});
