import $RefParser from "@apidevtools/json-schema-ref-parser";
import { readFile } from "fs/promises";
import { dirname, relative } from "path";
import { inspect } from "util";
import { z } from "zod";
import { mapAsync } from "./array.js";
import { KeyedCache } from "./cache.js";
import { example, preview } from "./changed-files.js";
import { resolveCached, resolvePairCached } from "./path.js";
import { SpecModelError } from "./spec-model-error.js";
import { embedError } from "./spec-model.js";

/**
 * @typedef {import('./spec-model.js').ErrorJSON} ErrorJSON
 * @typedef {import('./spec-model.js').Tag} Tag
 * @typedef {import('./spec-model.js').ToJSONOptions} ToJSONOptions
 */

/**
 * @typedef {Object} Operation
 * @property {string} id - The operation ID
 * @property {string} path - API path
 * @property {string} httpMethod - HTTP method (GET, POST, etc.)
 */

/**
 * @typedef {Object} SwaggerJSON
 * @property {string} path
 * @property {Operation[]} [operations]
 * @property {Object[]} [refs]
 */

const infoSchema = z.object({
  "x-typespec-generated": z.array(z.object({ emitter: z.string().optional() })).optional(),
});
/**
 * @typedef {import("zod").infer<typeof infoSchema>} InfoObject
 */

// https://swagger.io/specification/v2/#operation-object
const operationSchema = z.object({ operationId: z.string().optional() });
/**
 * @typedef {import("zod").infer<typeof operationSchema>} OperationObject
 */

// TODO: Consider narrowing to only the field names in the spec ("get", "put", etc)
// https://swagger.io/specification/v2/#path-item-object
const pathSchema = z
  .object({
    parameters: z.array(z.unknown()).optional(),
  })
  .catchall(operationSchema);
/**
 * @typedef {import("zod").infer<typeof pathSchema>} PathObject
 */

// https://swagger.io/specification/v2/#paths-object
const pathsSchema = z.record(z.string(), pathSchema);
/**
 * @typedef {import("zod").infer<typeof pathsSchema>} PathsObject
 */

// https://swagger.io/specification/v2/#swagger-object
const swaggerSchema = z.object({
  info: infoSchema.optional(),
  paths: pathsSchema.optional(),
  "x-ms-paths": pathsSchema.optional(),
});
/**
 * @typedef {import("zod").infer<typeof swaggerSchema>} SwaggerObject
 *
 * @example
 * const swagger = {
 *   "paths": {
 *     "/foo": {
 *       "parameters": [ ... ],
 *       "get": {
 *         "operationId": "Foo_Get"
 *       },
 *       "put": {
 *         "operationId": "Foo_CreateOrUpdate"
 *       }
 *     },
 *     "/bar": { ... }
 *   },
 *   "x-ms-paths": {
 *     "/baz": { ... }
 *   }
 * };
 */

/**
 * @type {import('@apidevtools/json-schema-ref-parser').ResolverOptions}
 */
const excludeExamples = {
  order: 1,
  canRead: true,
  read: async (
    /** @type import('@apidevtools/json-schema-ref-parser').FileInfo */
    file,
  ) => {
    if (example(file.url)) {
      return "";
    }
    return await readFile(file.url, { encoding: "utf8" });
  },
};

export class Swagger {
  /**
   * Caches the contents of files on disk, using the resolved path as the key.
   *
   * @type {KeyedCache<string, Promise<string>>}
   */
  static #contentCache = new KeyedCache();

  /**
   * Caches JSON objects parsed from text, using the resolved path (or content string itself) as the key.
   *
   * @type {KeyedCache<string, Promise<unknown>>}
   * */
  static #contentJsonCache = new KeyedCache();

  /**
   * Caches SwaggerObject objects parsed from JSON objects, using the resolved path (or content string itself) as the key.
   *
   * @type {KeyedCache<string, Promise<SwaggerObject>>}
   */
  static #contentObjectCache = new KeyedCache();

  /**
   * Caches operations extracted from a SwaggerObject, using the resolved path (or content string itself) as the key.
   *
   * @type {KeyedCache<string, Promise<Map<string, Operation>>>}
   */
  static #operationsCache = new KeyedCache();

  /**
   * Caches reference paths extracted from a JSON object, using the resolved path (or content string itself) as the key.
   *
   * Swagger objects should not be cached statically, because they may belong to different Tags, Readmes, or SpecModels.
   *
   * @type {KeyedCache<string, Promise<string[]>>}
   */
  static #refPathCache = new KeyedCache();

  /**
   * Optional content of swagger file, passed in via `options`.  If undefined, content is loaded from `#path`.
   *
   * @type {string | undefined}
   */
  #content;

  /** @type {import('./logger.js').ILogger | undefined} */
  #logger;

  /** @type {string} absolute path */
  #path;

  /** @type {Tag | undefined} Tag that contains this Swagger */
  #tag;

  /** @type {Map<string, Swagger> | undefined} all references, safe to cache in instance (but not statically) */
  #allRefs;

  /** @type {Map<string, Swagger> | undefined} referenced swaggers (excluding examples), safe to cache in instance (but not statically) */
  #refs;

  /** @type {Map<string, Swagger> | undefined} referenced examples (excluding swaggers), safe to cache in instance (but not statically) */
  #examples;

  /**
   * @param {string} path
   * @param {Object} [options]
   * @param {string} [options.content] If specified, is used instead of reading path from disk
   * @param {import('./logger.js').ILogger} [options.logger]
   * @param {Tag} [options.tag]
   */
  constructor(path, options = {}) {
    const { content, logger, tag } = options;

    const rootDir = dirname(tag?.readme?.path ?? "");
    this.#path = resolvePairCached(rootDir, path);

    this.#content = content;
    this.#logger = logger;
    this.#tag = tag;
  }

  /**
   * @returns {Promise<string>} Content of swagger file, represented as a string, either loaded from `#path` or passed in via `options`
   * @throws {SpecModelError}
   */
  async #getContent() {
    return (
      this.#content ??
      (await Swagger.#contentCache.getOrCreate(
        this.#path,
        async () =>
          await this.#wrapError(
            async () => await readFile(this.#path, { encoding: "utf8" }),
            "Failed to read file for swagger",
          ),
      ))
    );
  }

  /**
   * @returns {Promise<unknown>} Content of swagger file, represented as an untyped JSON object
   * @throws {SpecModelError}
   */
  async #getContentJSON() {
    return await Swagger.#contentJsonCache.getOrCreate(
      this.#content ?? this.#path,
      async () =>
        await this.#wrapError(
          async () => /** @type {unknown} */ (JSON.parse(await this.#getContent())),
          "Failed to parse JSON for swagger",
        ),
    );
  }

  /**
   * @returns {Promise<SwaggerObject>} Content of swagger file, represented as a typed object
   * @throws {SpecModelError}
   */
  async #getContentObject() {
    return await Swagger.#contentObjectCache.getOrCreate(
      this.#content ?? this.#path,
      async () =>
        await this.#wrapError(
          async () => swaggerSchema.parse(await this.#getContentJSON()),
          "Failed to parse schema for swagger",
        ),
    );
  }

  /**
   * @returns {Promise<Map<string, Swagger>>} Map of swaggers referenced from this swagger, using `path` as key
   */
  async getRefs() {
    if (this.#refs === undefined) {
      const allRefs = await this.#getRefs();

      // filter out any paths that are examples
      const filtered = new Map([...allRefs].filter(([path]) => !example(path)));

      this.#refs = filtered;
    }
    return this.#refs;
  }

  async #getRefs() {
    if (this.#allRefs === undefined) {
      // Safe to cache refPaths statically, since it's just an array of string paths
      const refPaths = await Swagger.#refPathCache.getOrCreate(
        this.#content ?? this.#path,
        async () => {
          const contentJSON = await this.#getContentJSON();

          const schema = await this.#wrapError(
            async () =>
              await $RefParser.resolve(this.#path, contentJSON, {
                resolve: { file: excludeExamples, http: false },
              }),
            "Failed to resolve file for swagger",
          );

          return (
            schema
              .paths("file")
              // Exclude ourself
              .filter((p) => resolveCached(p) !== resolveCached(this.#path))
          );
        },
      );

      // Swagger objects should not be cached statically, because they may belong to different Tags, Readmes, or SpecModels.
      // But, they are safe to cache in this instance.
      this.#allRefs = new Map(
        refPaths.map((p) => {
          const swagger = new Swagger(p, {
            logger: this.#logger,
            tag: this.#tag,
          });
          return [swagger.path, swagger];
        }),
      );
    }

    return this.#allRefs;
  }

  /**
   * @returns {Promise<Map<string, Swagger>>} Map of examples referenced from this swagger, using `path` as key
   */
  async getExamples() {
    if (this.#examples === undefined) {
      const allRefs = await this.#getRefs();

      // filter out any paths that are examples
      const filtered = new Map([...allRefs].filter(([path]) => example(path)));

      this.#examples = filtered;
    }
    return this.#examples;
  }

  /**
   * @returns {Promise<Map<string, Operation>>} Map of the operations in this swagger, using `operationId` as key
   */
  async getOperations() {
    return await Swagger.#operationsCache.getOrCreate(this.#content ?? this.#path, async () => {
      const contentObject = await this.#getContentObject();

      /** @type {Map<string, Operation>} */
      const operations = new Map();

      // Process regular paths
      if (contentObject.paths) {
        for (const [path, pathObject] of Object.entries(contentObject.paths)) {
          this.#addOperations(operations, path, pathObject);
        }
      }

      // Process x-ms-paths (Azure extension)
      if (contentObject["x-ms-paths"]) {
        for (const [path, pathObject] of Object.entries(contentObject["x-ms-paths"])) {
          this.#addOperations(operations, path, pathObject);
        }
      }

      return operations;
    });
  }

  /**
   * @returns {Promise<boolean>} True if the spec was generated from TypeSpec
   */
  async getTypeSpecGenerated() {
    const contentObject = await this.#getContentObject();
    return contentObject.info?.["x-typespec-generated"] !== undefined;
  }

  /**
   *
   * @param {Map<string, Operation>} operations
   * @param {string} path
   * @param {PathObject} pathObject
   * @returns {void}
   */
  #addOperations(operations, path, pathObject) {
    for (const [method, operation] of Object.entries(
      /** @type {Omit<PathObject, "parameters">} */ (pathObject),
    )) {
      if (method !== "parameters" && operation.operationId !== undefined) {
        const operationObj = {
          id: operation.operationId,
          httpMethod: method.toUpperCase(),
          path: path,
        };
        operations.set(operation.operationId, operationObj);
      }
    }
  }

  /**
   * @returns {string} absolute path
   */
  get path() {
    return this.#path;
  }

  /**
   * @returns {Tag | undefined} Tag that contains this Swagger
   */
  get tag() {
    return this.#tag;
  }

  /**
   * @returns {string} version kind (stable or preview)
   */
  get versionKind() {
    return preview(this.#path)
      ? API_VERSION_LIFECYCLE_STAGES.PREVIEW
      : API_VERSION_LIFECYCLE_STAGES.STABLE;
  }

  /**
   * @param {ToJSONOptions} [options]
   * @returns {Promise<SwaggerJSON|ErrorJSON>}
   */
  async toJSONAsync(options = {}) {
    const { includeOperations, includeRefs, relativePaths } = options;

    return await embedError(
      async () => ({
        path:
          relativePaths && this.#tag?.readme?.specModel
            ? relative(this.#tag?.readme?.specModel.folder, this.#path)
            : this.#path,
        operations: includeOperations
          ? [...(await this.getOperations()).values()].map((o) => {
              // Create new object with properties in preferred output order
              return { path: o.path, httpMethod: o.httpMethod, id: o.id };
            })
          : undefined,
        refs: includeRefs
          ? await mapAsync(
              [...(await this.getRefs()).values()].sort((a, b) => a.path.localeCompare(b.path)),
              async (s) =>
                // Do not include swagger refs transitively, otherwise we could get in infinite loop
                await s.toJSONAsync({ ...options, includeRefs: false }),
            )
          : undefined,
      }),
      options,
    );
  }

  toString() {
    return `Swagger(${this.#path}, {logger: ${inspect(this.#logger)}})`;
  }

  /**
   * Returns value of `func()`, wrapping any `Error` in `SpecModelError`
   *
   * @template T
   * @param {() => T | Promise<T>} func
   * @param {string} message
   * @returns {Promise<T>}
   * @throws {SpecModelError}
   */
  async #wrapError(func, message) {
    try {
      return await func();
    } catch (error) {
      /* v8 ignore else -- defensive rethrow */
      if (error instanceof Error) {
        throw new SpecModelError(`${message}: ${this.#path}`, {
          cause: error,
          source: this.#path,
          tag: this.#tag?.name,
          readme: this.#tag?.readme?.path,
        });
      } else {
        throw error;
      }
    }
  }
}

// API version lifecycle stages
export const API_VERSION_LIFECYCLE_STAGES = Object.freeze({
  PREVIEW: "preview",
  STABLE: "stable",
});
