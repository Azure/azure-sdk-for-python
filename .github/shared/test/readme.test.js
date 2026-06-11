import { resolve } from "path";
import { describe, expect, it } from "vitest";
import { ConsoleLogger } from "../src/logger.js";
import { Readme, TagMatchRegex } from "../src/readme.js";
import { SpecModel } from "../src/spec-model.js";
import { contosoReadme } from "./examples.js";

const options = { logger: new ConsoleLogger(/*debug*/ true) };

describe("readme", () => {
  it("can be created with mock path", async () => {
    const readme = new Readme("bar");
    expect(readme.path).toBe(resolve("bar"));

    await expect(readme.getTags()).rejects.toThrowError(/no such file or directory/i);

    expect(readme.specModel).toBeUndefined();
  });

  it("resolves path against SpecModel", () => {
    const readme = new Readme("readme.md", {
      specModel: new SpecModel("/specs/foo"),
    });
    expect(readme.path).toBe(resolve("/specs/foo/readme.md"));
  });

  it("can be created with string content", async () => {
    const folder = "/fake";
    const readme = new Readme(resolve(folder, "readme.md"), {
      ...options,
      content: contosoReadme,
    });

    const tags = await readme.getTags();
    const tagNames = [...tags.keys()];
    const expectedTagNames = ["package-2021-11-01", "package-2021-10-01-preview"];

    expect(tagNames.sort()).toEqual(expectedTagNames.sort());

    const swaggerPaths = [...tags.values()].flatMap((t) => [...t.inputFiles.keys()]);

    const expectedPaths = [
      resolve(folder, "Microsoft.Contoso/stable/2021-11-01/contoso.json"),
      resolve(folder, "Microsoft.Contoso/preview/2021-10-01-preview/contoso.json"),
    ];

    expect(swaggerPaths.sort()).toEqual(expectedPaths.sort());
  });

  // If tag names are duplicated (with no disambiguating conditionals), it's almost certainly a bug
  // in the readme that should be fixed.
  it("throws if duplicate tags", async () => {
    let content = `
\`\`\`yaml $(tag) == 'package-2025-01-01'
input-file:
  - foo.json
\`\`\`
\`\`\`yaml $(tag) == 'package-2025-01-01'
input-file:
  - bar.json
\`\`\`
`;

    let readme = new Readme("foo", { ...options, content });

    await expect(readme.getTags()).rejects.toThrowError(
      "Multiple input-file definitions for tag package-2025-01-01",
    );
  });

  // A few existing specs use duplicate tags, but with conditionals to disambiguate at runtime.
  //
  // While this may work for generating the SDK itself (where you can specify the additional values),
  // it doesn't work for static analysis tools like LintDiff, since LintDiff wouldn't know what
  // additional values to pass to autorest.
  //
  // It may be possible to support this in spec-model, by allowing duplicate tags with different conditionals.
  // However, downstream users of the tags for static analysis would still need to throw.  Also, we only
  // found two specs using this pattern (and only in the private repo).  So I think it's better to continue
  // disallowing this, and instead rename the conflicting tags in the readme.  Rather than adding
  // complexity to spec-model for an edge case (with workarounds).
  //
  // More details: https://github.com/Azure/azure-rest-api-specs/issues/37003
  it("throws if duplicate tags with different conditionals", async () => {
    let content = `
\`\`\`yaml $(tag) == 'package-2025-01-01'
input-file:
  - foo.json
\`\`\`
\`\`\`yaml $(tag) == 'package-2025-01-01' && $(test-condition)
input-file:
  - bar.json
\`\`\`
`;

    let readme = new Readme("foo", { ...options, content });

    await expect(readme.getTags()).rejects.toThrowError(
      "Multiple input-file definitions for tag package-2025-01-01",
    );
  });

  it("throws if input-file is not string", async () => {
    let content = `
\`\`\`yaml $(tag) == 'package-2025-01-01'
input-file:
  - foo.json
  - invalid-object:
    - bar.json
\`\`\`
`;

    let readme = new Readme("readme.md", { ...options, content });

    await expect(readme.getTags()).rejects.toThrowErrorMatchingInlineSnapshot(`
      [SpecModelError: Unable to parse input-file YAML for tag package-2025-01-01 in ${readme.path}
        Problem File: ${readme.path}
        Readme: ${readme.path}
        Tag: package-2025-01-01
        Cause: [
        {
          "code": "invalid_union",
          "errors": [
            [
              {
                "expected": "string",
                "code": "invalid_type",
                "path": [],
                "message": "Invalid input: expected string, received array"
              }
            ],
            [
              {
                "expected": "string",
                "code": "invalid_type",
                "path": [
                  1
                ],
                "message": "Invalid input: expected string, received object"
              }
            ]
          ],
          "path": [
            "input-file"
          ],
          "message": "Invalid input"
        }
      ]]
    `);
  });

  it("can be created with empty content", async () => {
    const folder = "/fake";
    const readme = new Readme(resolve(folder, "readme.md"), {
      ...options,
      // Simulate empty file
      content: "",
    });

    const tags = await readme.getTags();

    // Ensures code doesn't try to read file `/fake/readme.md` which would throw
    expect(tags.size).toBe(0);
  });
});

describe("TagMatchRegex", () => {
  it.each([
    ["```yaml $(package-A-tag) == 'package-A-[[Version]]'", false, undefined],
    ["``` yaml $(tag)=='package-2017-03' && $(go)", true, "package-2017-03"],
    ["``` yaml $(csharp) && $(tag) == 'release_4_0'", true, "release_4_0"],
    ["``` yaml $(tag) == 'package-2021-12-01-preview'", true, "package-2021-12-01-preview"],
    ['``` yaml $(tag) == "package-2025-06-05"', true, "package-2025-06-05"],
    ["``` yaml $(tag) == 'package-2025-06-05\"", false, undefined],
    ["``` yaml $(tag) == \"package-2025-06-05'", false, undefined],
  ])("matches tags and extracts tag names properly: %s", (example, expectedMatch, expectedTag) => {
    const match = example.match(TagMatchRegex);
    expect(TagMatchRegex.test(example)).toEqual(expectedMatch);
    expect(match?.[2]).toEqual(expectedTag);
  });
});
