import { afterEach, describe, expect, it, vi } from "vitest";

const mockDiff = vi.hoisted(() => vi.fn().mockResolvedValue(""));

vi.mock("simple-git", () => ({
  simpleGit: vi.fn().mockReturnValue({
    diff: mockDiff,
  }),
}));

import { resolve } from "path";
import * as simpleGit from "simple-git";
import {
  dataPlane,
  example,
  getChangedFiles,
  getChangedFilesStatuses,
  json,
  markdown,
  preview,
  quickstartTemplate,
  readme,
  resourceManager,
  scenario,
  stable,
  swagger,
  typespec,
} from "../src/changed-files.js";
import { debugLogger } from "../src/logger.js";

describe("changedFiles", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it.each([{}, { logger: debugLogger }])(`getChangedFiles(%o)`, async (options) => {
    const files = [
      ".github/src/changed-files.js",
      "specification/contosowidgetmanager/Contoso.Management/main.tsp",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/contoso.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/examples/Employees_Get.json",
    ];

    mockDiff.mockResolvedValue(files.join("\n"));

    await expect(getChangedFiles(options)).resolves.toEqual(files);
    expect(mockDiff).toHaveBeenCalledWith(["--name-only", "HEAD^", "HEAD"]);

    const specFiles = files.filter((f) => f.startsWith("specification"));
    mockDiff.mockResolvedValue(specFiles.join("\n"));
    await expect(getChangedFiles({ ...options, paths: ["specification"] })).resolves.toEqual(
      specFiles,
    );
    expect(mockDiff).toHaveBeenCalledWith(["--name-only", "HEAD^", "HEAD", "--", "specification"]);
  });

  it("getChangedFiles returns empty array when no files are changed", async () => {
    mockDiff.mockResolvedValue("");
    await expect(getChangedFiles()).resolves.toEqual([]);
    expect(mockDiff).toHaveBeenCalledWith(["--name-only", "HEAD^", "HEAD"]);
  });

  it("getChangedFiles accepts gitOptions parameter", async () => {
    const files = ["file1.json", "file2.json"];
    mockDiff.mockResolvedValue(files.join("\n"));

    await expect(getChangedFiles({ gitOptions: ["--no-renames"] })).resolves.toEqual(files);
    expect(mockDiff).toHaveBeenCalledWith(["--name-only", "--no-renames", "HEAD^", "HEAD"]);
  });

  it("getChangedFiles accepts multiple gitOptions", async () => {
    const files = ["file1.json"];
    mockDiff.mockResolvedValue(files.join("\n"));

    await expect(
      getChangedFiles({ gitOptions: ["--no-renames", "--find-copies"] }),
    ).resolves.toEqual(files);
    expect(mockDiff).toHaveBeenCalledWith([
      "--name-only",
      "--no-renames",
      "--find-copies",
      "HEAD^",
      "HEAD",
    ]);
  });

  const files = [
    "CONTRIBUTING.MD",
    "cspell.json",
    "cspell.yaml",
    "MixedCase.jSoN",
    "MixedCase.mD",
    "README.MD",
    "not-spec/contosowidgetmanager/data-plane/readme.md",
    "not-spec/contosowidgetmanager/resource-manager/readme.md",
    "not-spec/contosowidgetmanager/Contoso.Management/main.tsp",
    "not-spec/contosowidgetmanager/Contoso.Management/tspconfig.yaml",
    "not-spec/contosowidgetmanager/Contoso.Management/examples/2021-11-01/Employees_Get.json",
    "not-spec/contosowidgetmanager/Contoso.Management/examples/2021-12-01-preview/Employees_Get.json",
    "not-spec/contosowidgetmanager/Contoso.Management/scenarios/2021-11-01/Employees_Get.json",
    "not-spec/contosowidgetmanager/Contoso.Management/scenarios/2021-12-01-preview/Employees_Get.json",
    "not-spec/contosowidgetmanager/resource-manager/Microsoft.Contoso/preview/2021-12-01-preview/contoso.json",
    "not-spec/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/contoso.json",
    "specification/contosowidgetmanager/data-plane/readme.md",
    "specification/contosowidgetmanager/Contoso.Management/main.tsp",
    "specification/contosowidgetmanager/Contoso.Management/tspconfig.yaml",
    "specification/contosowidgetmanager/Contoso.Management/examples/2021-11-01/Employees_Get.json",
    "specification/contosowidgetmanager/Contoso.Management/examples/2021-12-01-preview/Employees_Get.json",
    "specification/contosowidgetmanager/resource-manager/readme.md",
    "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/preview/2021-12-01-preview/contoso.json",
    "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/preview/2021-12-01-preview/examples/Employees_Get.json",
    "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/contoso.json",
    "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/examples/Employees_Get.json",
    "specification/contosowidgetmanager/Contoso.Management/scenarios/2021-11-01/Employees_Get.json",
    "specification/contosowidgetmanager/Contoso.Management/scenarios/2021-12-01-preview/Employees_Get.json",
    "specification/compute/quickstart-templates/swagger.json",
  ];

  const filesResolved = files.map((f) => resolve(f));

  it("filter:json", () => {
    const expected = [
      "cspell.json",
      "MixedCase.jSoN",
      "not-spec/contosowidgetmanager/Contoso.Management/examples/2021-11-01/Employees_Get.json",
      "not-spec/contosowidgetmanager/Contoso.Management/examples/2021-12-01-preview/Employees_Get.json",
      "not-spec/contosowidgetmanager/Contoso.Management/scenarios/2021-11-01/Employees_Get.json",
      "not-spec/contosowidgetmanager/Contoso.Management/scenarios/2021-12-01-preview/Employees_Get.json",
      "not-spec/contosowidgetmanager/resource-manager/Microsoft.Contoso/preview/2021-12-01-preview/contoso.json",
      "not-spec/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/contoso.json",
      "specification/contosowidgetmanager/Contoso.Management/examples/2021-11-01/Employees_Get.json",
      "specification/contosowidgetmanager/Contoso.Management/examples/2021-12-01-preview/Employees_Get.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/preview/2021-12-01-preview/contoso.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/preview/2021-12-01-preview/examples/Employees_Get.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/contoso.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/examples/Employees_Get.json",
      "specification/contosowidgetmanager/Contoso.Management/scenarios/2021-11-01/Employees_Get.json",
      "specification/contosowidgetmanager/Contoso.Management/scenarios/2021-12-01-preview/Employees_Get.json",
      "specification/compute/quickstart-templates/swagger.json",
    ];

    expect(files.filter(json)).toEqual(expected);
    expect(filesResolved.filter(json)).toEqual(expected.map((f) => resolve(f)));
  });

  it("filter:markdown", () => {
    const expected = [
      "CONTRIBUTING.MD",
      "MixedCase.mD",
      "README.MD",
      "not-spec/contosowidgetmanager/data-plane/readme.md",
      "not-spec/contosowidgetmanager/resource-manager/readme.md",
      "specification/contosowidgetmanager/data-plane/readme.md",
      "specification/contosowidgetmanager/resource-manager/readme.md",
    ];

    expect(files.filter(markdown)).toEqual(expected);
    expect(filesResolved.filter(markdown)).toEqual(expected.map((f) => resolve(f)));
  });

  it("filter:readme", () => {
    const expected = [
      "README.MD",
      "not-spec/contosowidgetmanager/data-plane/readme.md",
      "not-spec/contosowidgetmanager/resource-manager/readme.md",
      "specification/contosowidgetmanager/data-plane/readme.md",
      "specification/contosowidgetmanager/resource-manager/readme.md",
    ];

    expect(files.filter(readme)).toEqual(expected);
    expect(filesResolved.filter(readme)).toEqual(expected.map((f) => resolve(f)));
  });

  it("filter:typespec", () => {
    const expected = [
      "not-spec/contosowidgetmanager/Contoso.Management/main.tsp",
      "not-spec/contosowidgetmanager/Contoso.Management/tspconfig.yaml",
      "specification/contosowidgetmanager/Contoso.Management/main.tsp",
      "specification/contosowidgetmanager/Contoso.Management/tspconfig.yaml",
    ];
    expect(files.filter(typespec)).toEqual(expected);
  });

  it("filter:data-plane", () => {
    const expected = [
      "not-spec/contosowidgetmanager/data-plane/readme.md",
      "specification/contosowidgetmanager/data-plane/readme.md",
    ];

    expect(files.filter(dataPlane)).toEqual(expected);
    expect(filesResolved.filter(dataPlane)).toEqual(expected.map((f) => resolve(f)));
  });

  it("filter:resource-manager", () => {
    const expected = [
      "not-spec/contosowidgetmanager/resource-manager/readme.md",
      "not-spec/contosowidgetmanager/resource-manager/Microsoft.Contoso/preview/2021-12-01-preview/contoso.json",
      "not-spec/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/contoso.json",
      "specification/contosowidgetmanager/resource-manager/readme.md",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/preview/2021-12-01-preview/contoso.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/preview/2021-12-01-preview/examples/Employees_Get.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/contoso.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/examples/Employees_Get.json",
    ];

    expect(files.filter(resourceManager)).toEqual(expected);
    expect(filesResolved.filter(resourceManager)).toEqual(expected.map((f) => resolve(f)));
  });

  it("filter:preview", () => {
    const expected = [
      "not-spec/contosowidgetmanager/resource-manager/Microsoft.Contoso/preview/2021-12-01-preview/contoso.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/preview/2021-12-01-preview/contoso.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/preview/2021-12-01-preview/examples/Employees_Get.json",
    ];

    expect(files.filter(preview)).toEqual(expected);
    expect(filesResolved.filter(preview)).toEqual(expected.map((f) => resolve(f)));
  });

  it("filter:stable", () => {
    const expected = [
      "not-spec/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/contoso.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/contoso.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/examples/Employees_Get.json",
    ];

    expect(files.filter(stable)).toEqual(expected);
    expect(filesResolved.filter(stable)).toEqual(expected.map((f) => resolve(f)));
  });

  it("filter:example", () => {
    const expected = [
      "not-spec/contosowidgetmanager/Contoso.Management/examples/2021-11-01/Employees_Get.json",
      "not-spec/contosowidgetmanager/Contoso.Management/examples/2021-12-01-preview/Employees_Get.json",
      "specification/contosowidgetmanager/Contoso.Management/examples/2021-11-01/Employees_Get.json",
      "specification/contosowidgetmanager/Contoso.Management/examples/2021-12-01-preview/Employees_Get.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/preview/2021-12-01-preview/examples/Employees_Get.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/examples/Employees_Get.json",
    ];

    expect(files.filter(example)).toEqual(expected);
    expect(filesResolved.filter(example)).toEqual(expected.map((f) => resolve(f)));
  });

  it("filter:quickstartTemplate", () => {
    const expected = ["specification/compute/quickstart-templates/swagger.json"];

    expect(files.filter(quickstartTemplate)).toEqual(expected);
  });

  it("filter:scenarios", () => {
    const expected = [
      "not-spec/contosowidgetmanager/Contoso.Management/scenarios/2021-11-01/Employees_Get.json",
      "not-spec/contosowidgetmanager/Contoso.Management/scenarios/2021-12-01-preview/Employees_Get.json",
      "specification/contosowidgetmanager/Contoso.Management/scenarios/2021-11-01/Employees_Get.json",
      "specification/contosowidgetmanager/Contoso.Management/scenarios/2021-12-01-preview/Employees_Get.json",
    ];

    expect(files.filter(scenario)).toEqual(expected);
    expect(filesResolved.filter(scenario)).toEqual(expected.map((f) => resolve(f)));
  });

  it("filter:swagger", () => {
    const expected = [
      "not-spec/contosowidgetmanager/resource-manager/Microsoft.Contoso/preview/2021-12-01-preview/contoso.json",
      "not-spec/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/contoso.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/preview/2021-12-01-preview/contoso.json",
      "specification/contosowidgetmanager/resource-manager/Microsoft.Contoso/stable/2021-11-01/contoso.json",
    ];

    expect(files.filter(swagger)).toEqual(expected);
    expect(filesResolved.filter(swagger)).toEqual(expected.map((f) => resolve(f)));
  });

  describe("getChangedFilesStatuses", () => {
    it.each([{}, { logger: debugLogger }])(
      "should categorize files correctly with all types of changes (%o)",
      async (options) => {
        const gitOutput = [
          "M\t.github/src/changed-files.js",
          "A\tspecification/new-service/readme.md",
          "M\tspecification/existing-service/main.tsp",
          "D\tspecification/old-service/contoso.json",
          "R100\tspecification/service/old-name.json\tspecification/service/new-name.json",
          "C90\tspecification/template/base.json\tspecification/service/derived.json",
          "T\tspecification/service/type-changed.json",
        ].join("\n");

        mockDiff.mockResolvedValue(gitOutput);
        let result = await getChangedFilesStatuses(options);
        expect(result).toEqual({
          additions: ["specification/new-service/readme.md", "specification/service/derived.json"],
          modifications: [
            ".github/src/changed-files.js",
            "specification/existing-service/main.tsp",
            "specification/service/type-changed.json",
          ],
          deletions: ["specification/old-service/contoso.json"],
          renames: [
            {
              from: "specification/service/old-name.json",
              to: "specification/service/new-name.json",
            },
          ],
          total: 7,
        });
        expect(mockDiff).toHaveBeenCalledWith(["--name-status", "HEAD^", "HEAD"]);

        const specGitOutput = gitOutput
          .split("\n")
          .filter((f) => f.includes("specification/"))
          .join("\n");
        mockDiff.mockResolvedValue(specGitOutput);
        result = await getChangedFilesStatuses({ ...options, paths: ["specification"] });
        expect(result).toEqual({
          additions: ["specification/new-service/readme.md", "specification/service/derived.json"],
          modifications: [
            "specification/existing-service/main.tsp",
            "specification/service/type-changed.json",
          ],
          deletions: ["specification/old-service/contoso.json"],
          renames: [
            {
              from: "specification/service/old-name.json",
              to: "specification/service/new-name.json",
            },
          ],
          total: 6,
        });
        expect(mockDiff).toHaveBeenCalledWith([
          "--name-status",
          "HEAD^",
          "HEAD",
          "--",
          "specification",
        ]);
      },
    );

    it("should handle empty git output", async () => {
      mockDiff.mockResolvedValue("");
      const result = await getChangedFilesStatuses();
      expect(result).toEqual({
        additions: [],
        modifications: [],
        deletions: [],
        renames: [],
        total: 0,
      });
    });

    it("should handle only additions", async () => {
      const gitOutput = [
        "A\tspecification/service1/readme.md",
        "A\tspecification/service2/main.tsp",
      ].join("\n");

      mockDiff.mockResolvedValue(gitOutput);
      const result = await getChangedFilesStatuses();
      expect(result).toEqual({
        additions: ["specification/service1/readme.md", "specification/service2/main.tsp"],
        modifications: [],
        deletions: [],
        renames: [],
        total: 2,
      });
    });

    it("should handle only renames", async () => {
      const gitOutput = [
        "R95\told/path/file1.json\tnew/path/file1.json",
        "R100\tservice/old.tsp\tservice/new.tsp",
      ].join("\n");

      mockDiff.mockResolvedValue(gitOutput);
      const result = await getChangedFilesStatuses();
      expect(result).toEqual({
        additions: [],
        modifications: [],
        deletions: [],
        renames: [
          {
            from: "old/path/file1.json",
            to: "new/path/file1.json",
          },
          {
            from: "service/old.tsp",
            to: "service/new.tsp",
          },
        ],
        total: 2,
      });
    });

    it("should pass git options correctly", async () => {
      const options = {
        baseCommitish: "origin/main",
        headCommitish: "feature-branch",
        cwd: "/custom/path",
      };

      mockDiff.mockResolvedValue("A\ttest.json");
      await getChangedFilesStatuses(options);
      expect(simpleGit.simpleGit).toHaveBeenCalledWith("/custom/path");
      expect(mockDiff).toHaveBeenCalledWith(["--name-status", "origin/main", "feature-branch"]);
    });

    it("should accept gitOptions parameter", async () => {
      mockDiff.mockResolvedValue("A\tfile1.json\nM\tfile2.json");
      const result = await getChangedFilesStatuses({ gitOptions: ["--no-renames"] });
      expect(result).toEqual({
        additions: ["file1.json"],
        modifications: ["file2.json"],
        deletions: [],
        renames: [],
        total: 2,
      });
      expect(mockDiff).toHaveBeenCalledWith(["--name-status", "--no-renames", "HEAD^", "HEAD"]);
    });

    it("should accept multiple gitOptions", async () => {
      mockDiff.mockResolvedValue("A\tfile1.json");
      const result = await getChangedFilesStatuses({
        gitOptions: ["--no-renames", "--find-copies"],
      });
      expect(result).toEqual({
        additions: ["file1.json"],
        modifications: [],
        deletions: [],
        renames: [],
        total: 1,
      });
      expect(mockDiff).toHaveBeenCalledWith([
        "--name-status",
        "--no-renames",
        "--find-copies",
        "HEAD^",
        "HEAD",
      ]);
    });

    it("should log categories selectively with a logger", async () => {
      // When only some categories are populated and a logger is provided, the per-category
      // if-blocks whose category is empty should take their false branch.
      const gitOutput = [
        "A\tspecification/service1/readme.md",
        "A\tspecification/service2/main.tsp",
      ].join("\n");

      mockDiff.mockResolvedValue(gitOutput);
      const result = await getChangedFilesStatuses({ logger: debugLogger });
      expect(result).toEqual({
        additions: ["specification/service1/readme.md", "specification/service2/main.tsp"],
        modifications: [],
        deletions: [],
        renames: [],
        total: 2,
      });

      // Also test with no additions so the additions log block's false branch is covered
      const gitOutputNoAdditions = "M\tspecification/service1/readme.md";
      mockDiff.mockResolvedValue(gitOutputNoAdditions);
      const result2 = await getChangedFilesStatuses({ logger: debugLogger });
      expect(result2).toEqual({
        additions: [],
        modifications: ["specification/service1/readme.md"],
        deletions: [],
        renames: [],
        total: 1,
      });
    });
  });
});
