import { dirname, join, resolve } from "path";
import { describe, expect, it } from "vitest";
import { API_VERSION_LIFECYCLE_STAGES, Swagger } from "../src/swagger.js";

import { fileURLToPath } from "url";
import { ConsoleLogger } from "../src/logger.js";
import { Readme } from "../src/readme.js";
import { SpecModel } from "../src/spec-model.js";
import { Tag } from "../src/tag.js";
import { swaggerTypeSpecGenerated } from "./examples.js";

const __dirname = dirname(fileURLToPath(import.meta.url));

describe("Swagger", () => {
  it("can be created with mock path", async () => {
    const swagger = new Swagger("bar");
    expect(swagger.path).toBe(resolve("bar"));
    expect(swagger.tag).toBeUndefined();

    await expect(swagger.getRefs()).rejects.toThrowError(/Failed to read file for swagger/i);
  });

  it("resolves path against Tag.readme", () => {
    const readme = new Readme("/specs/foo/readme.md");
    const tag = new Tag("2025-01-01", [], { readme });
    const swagger = new Swagger("test.json", { tag });

    expect(swagger.path).toBe(resolve("/specs/foo/test.json"));
  });

  it("can be created with empty string content", async () => {
    const folder = "/fake";
    const swagger = new Swagger(resolve(folder, "empty.json"), {
      content: "{}",
    });

    const operations = await swagger.getOperations();
    expect(new Set(operations.keys())).toEqual(new Set());

    const examples = await swagger.getExamples();
    expect(new Set(examples.keys())).toEqual(new Set());

    const refs = await swagger.getRefs();
    expect(new Set(refs.keys())).toEqual(new Set());

    expect(await swagger.getTypeSpecGenerated()).toEqual(false);
  });

  it("can be created with typespec-generated string content", async () => {
    const folder = "/fake";
    const swagger = new Swagger(resolve(folder, "empty.json"), {
      content: swaggerTypeSpecGenerated,
    });

    const operations = await swagger.getOperations();
    expect(new Set(operations.keys())).toEqual(new Set());

    const examples = await swagger.getExamples();
    expect(new Set(examples.keys())).toEqual(new Set());

    const refs = await swagger.getRefs();
    expect(new Set(refs.keys())).toEqual(new Set());

    expect(await swagger.getTypeSpecGenerated()).toEqual(true);
  });

  it("can be created with sample string content", async () => {
    const content = `
    {
      "paths": {
        "/foo": {
          "parameters": ["unknown", 0],
          "get": {
            "operationId": "Foo_Get"
          },
          "put": {
            "operationId": "Foo_CreateOrUpdate"
          }
        },
        "/bar": {
          "get": {
            "operationId": "Bar_Get"
          }
        }
      },
      "x-ms-paths": {
        "/baz": {
          "get": {
            "operationId": "Baz_Get"
          }
        }
      }
    }
    `;

    const folder = "/fake";
    const swagger = new Swagger(resolve(folder, "empty.json"), {
      content,
    });

    const operations = await swagger.getOperations();
    expect(new Set(operations.keys())).toEqual(
      new Set(["Foo_Get", "Foo_CreateOrUpdate", "Bar_Get", "Baz_Get"]),
    );

    const examples = await swagger.getExamples();
    expect(new Set(examples.keys())).toEqual(new Set());

    const refs = await swagger.getRefs();
    expect(new Set(refs.keys())).toEqual(new Set());
  });

  it("throws when created with invalid JSON content", async () => {
    const folder = "/fake";
    const swagger = new Swagger(resolve(folder, "invalid.json"), {
      content: `not json`,
      tag: new Tag("test-tag", [], { readme: new Readme("/fake/readme.md") }),
    });

    await expect(swagger.getRefs()).rejects.toThrowErrorMatchingInlineSnapshot(`
      [SpecModelError: Failed to parse JSON for swagger: ${resolve("/fake/invalid.json")}
        Problem File: ${resolve("/fake/invalid.json")}
        Readme: ${resolve("/fake/readme.md")}
        Tag: test-tag
        Cause: SyntaxError: Unexpected token 'o', "not json" is not valid JSON]
    `);
  });

  it("throws when created with invalid schema content", async () => {
    const folder = "/fake";
    const swagger = new Swagger(resolve(folder, "invalid.json"), {
      content: `{"paths": "invalid"}`,
      tag: new Tag("test-tag", [], { readme: new Readme("/fake/readme.md") }),
    });

    // getRefs() shouldn't throw, since it doesn't care about the zod schema
    // ensures we are evaluating each data method lazily
    await expect(swagger.getRefs().then((m) => new Set(m.keys()))).resolves.toEqual(new Set());

    // getOperations() should throw, since the input wasn't valid per the zod schema
    await expect(swagger.getOperations()).rejects.toThrowErrorMatchingInlineSnapshot(`
      [SpecModelError: Failed to parse schema for swagger: ${resolve("/fake/invalid.json")}
        Problem File: ${resolve("/fake/invalid.json")}
        Readme: ${resolve("/fake/readme.md")}
        Tag: test-tag
        Cause: [
        {
          "expected": "record",
          "code": "invalid_type",
          "path": [
            "paths"
          ],
          "message": "Invalid input: expected record, received string"
        }
      ]]
    `);
  });

  it("throws when created with invalid ref content", async () => {
    const invalidRefContent = `
      {
        "paths": {
          "/foo": {
            "get": {
              "operationId": "Foo_Get",
              "$ref": "/does/not/exist.json"
            }
          }
        }
      }
    `;

    const folder = "/fake";
    const swagger = new Swagger(resolve(folder, "invalid.json"), {
      content: invalidRefContent,
      tag: new Tag("test-tag", [], { readme: new Readme("/fake/readme.md") }),
    });

    await expect(swagger.getRefs()).rejects.toThrowErrorMatchingInlineSnapshot(
      `
      [SpecModelError: Failed to resolve file for swagger: ${resolve("/fake/invalid.json")}
        Problem File: ${resolve("/fake/invalid.json")}
        Readme: ${resolve("/fake/readme.md")}
        Tag: test-tag
        Cause: ResolverError: Error reading file "${resolve("/does/not/exist.json").replace(/\\/g, "/").toLowerCase()}"]
    `,
    );
  });

  it("sorts refs in toJSONAsync", async () => {
    // a.json has 2+ refs (nesting/b.json, c.json, etc.) so the sort comparator gets invoked
    const swagger = new Swagger(
      resolve(__dirname, "fixtures/getAffectedSwaggers/specification/1/data-plane/a.json"),
    );
    const json = /** @type {import('../src/swagger.js').SwaggerJSON} */ (
      await swagger.toJSONAsync({ includeRefs: true })
    );
    const refs = /** @type {import('../src/swagger.js').SwaggerJSON[]} */ (json.refs);
    expect(refs.length).toBe(4);
    // ensure at least first two elements are sorted correctly
    expect(refs[0].path.localeCompare(refs[1].path)).toBeLessThan(0);
  });

  // TODO: Test that path is resolved against backpointer

  it("excludes example files", async () => {
    const swagger = new Swagger(resolve(__dirname, "fixtures/swagger/ignoreExamples/swagger.json"));
    const refs = await swagger.getRefs();

    const expectedIncludedPath = resolve(
      __dirname,
      "fixtures/swagger/ignoreExamples/included.json",
    );
    expect(refs).toMatchObject(
      new Map([
        [
          expectedIncludedPath,
          expect.objectContaining({
            path: /** @type {unknown} */ (expect.stringContaining(expectedIncludedPath)),
          }),
        ],
      ]),
    );
  });

  it("returns examples", async () => {
    const swagger = new Swagger(resolve(__dirname, "fixtures/swagger/ignoreExamples/swagger.json"));
    const examples = await swagger.getExamples();

    const expectedExamplePath = resolve(
      __dirname,
      "fixtures/swagger/ignoreExamples/examples/example.json",
    );
    expect(examples).toMatchObject(
      new Map([
        [
          expectedExamplePath,
          expect.objectContaining({
            path: /** @type {unknown} */ (expect.stringContaining(expectedExamplePath)),
          }),
        ],
      ]),
    );
  });

  it("returns cached examples on second call", async () => {
    const swagger = new Swagger(resolve(__dirname, "fixtures/swagger/ignoreExamples/swagger.json"));
    const examples1 = await swagger.getExamples();
    const examples2 = await swagger.getExamples();

    // Both calls should return the same (cached) Map instance
    expect(examples2).toBe(examples1);
  });

  it("computes versionKind from path", () => {
    let swagger = new Swagger(resolve("foo/preview/2025-01-01-preview/foo.json"));
    expect(swagger.versionKind).toEqual(API_VERSION_LIFECYCLE_STAGES.PREVIEW);

    swagger = new Swagger(resolve("foo/stable/2025-01-01/foo.json"));
    expect(swagger.versionKind).toEqual(API_VERSION_LIFECYCLE_STAGES.STABLE);
  });

  describe("getOperations", () => {
    it("should return normal operations", async () => {
      const testFixturePath = join(__dirname, "fixtures", "swagger", "specification");
      const targetPath = join(
        testFixturePath,
        "servicelinker/resource-manager/Microsoft.ServiceLinker/stable/2024-04-01/test.json",
      );
      const specModel = new SpecModel(testFixturePath, {
        logger: new ConsoleLogger(/*debug*/ true),
      });
      const result = await specModel.getSwaggers();
      const swagger = result.find((s) => s.path === targetPath);

      if (!swagger) throw new Error("Swagger not found for the given path");
      const operationsMap = await swagger.getOperations();
      expect(operationsMap.size).toBe(3);

      let expectedApiPath =
        "/subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}/providers/Microsoft.ServiceLinker/locations/{location}/dryruns/{dryrunName}";

      // Test specific operations by ID
      const createDryrun = operationsMap.get("Connector_CreateDryrun");
      const getDryrun = operationsMap.get("Connector_GetDryrun");
      const listDryruns = operationsMap.get("Connector_ListDryrun");

      expect(createDryrun).toBeDefined();
      if (createDryrun) {
        expect(createDryrun.id).toBe("Connector_CreateDryrun");
        expect(createDryrun.httpMethod).toBe("PUT");
        expect(createDryrun.path).toBe(expectedApiPath);
      }

      expect(getDryrun).toBeDefined();
      if (getDryrun) {
        expect(getDryrun.id).toBe("Connector_GetDryrun");
        expect(getDryrun.httpMethod).toBe("GET");
        expect(getDryrun.path).toBe(expectedApiPath);
      }

      expectedApiPath =
        "/subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}/providers/Microsoft.ServiceLinker/locations/{location}/dryruns";
      expect(listDryruns).toBeDefined();
      if (listDryruns) {
        expect(listDryruns.id).toBe("Connector_ListDryrun");
        expect(listDryruns.httpMethod).toBe("GET");
        expect(listDryruns.path).toBe(expectedApiPath);
      }
    });
  });
});
