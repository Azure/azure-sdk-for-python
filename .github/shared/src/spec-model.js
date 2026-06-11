import { readdir } from "fs/promises";
import { inspect } from "util";
import { flatMapAsync, mapAsync } from "./array.js";
import { readme } from "./changed-files.js";
import { resolveCached, resolvePairCached } from "./path.js";
import { Readme } from "./readme.js";
import { SpecModelError } from "./spec-model-error.js";

/**
 * @typedef {import('./readme.js').ReadmeJSON} ReadmeJSON
 * @typedef {import('./swagger.js').Swagger} Swagger
 * @typedef {import('./tag.js').Tag} Tag
 */

/**
 * @typedef {Object} ErrorJSON
 * @prop {string} error
 */

/**
 * @typedef {Object} SpecModelJSON
 * @property {string} folder
 * @property {(ReadmeJSON|ErrorJSON)[]} readmes
 */

/**
 * @typedef {Object} ToJSONOptions
 * @prop {boolean} [embedErrors]
 * @prop {boolean} [includeOperations] Whether to include the operations in each swagger. Increases runtime about 20x, from 6s to 120s for whole specs repo.
 * @prop {boolean} [includeRefs]
 * @prop {boolean} [relativePaths]
 */

/** @type {Map<string, SpecModel>} */
const specModelCache = new Map();

export class SpecModel {
  /** @type {string} absolute path */
  // @ts-expect-error Ignore error that value may not be set in ctor (since we may returned cached value)
  #folder;

  /** @type {import('./logger.js').ILogger | undefined} */
  #logger;

  /** @type {Map<string, Readme> | undefined} */
  #readmes;

  /**
   * @param {string} folder
   * @param {Object} [options]
   * @param {import('./logger.js').ILogger} [options.logger]
   */
  constructor(folder, options = {}) {
    const { logger } = options;

    const resolvedFolder = resolveCached(folder);

    const cachedSpecModel = specModelCache.get(resolvedFolder);
    if (cachedSpecModel !== undefined) {
      return cachedSpecModel;
    }

    this.#folder = resolvedFolder;
    this.#logger = logger;

    specModelCache.set(resolvedFolder, this);
  }

  /**
   * @returns {string} absolute path
   */
  get folder() {
    return this.#folder;
  }

  /**
   * Given a swagger file, return all the tags inside readme files that reference the file (directly or indirectly).
   * @param {string} swaggerPath
   * @returns {Promise<Map<string, Map<string, Tag>>>} map of readme paths to (map of tag names to Tag objects)
   */
  async getAffectedReadmeTags(swaggerPath) {
    const swaggerPathResolved = resolveCached(swaggerPath);

    /** @type {Map<string, Map<string, Tag>>} */
    const affectedReadmeTags = new Map();

    for (const readme of (await this.getReadmes()).values()) {
      for (const tag of (await readme.getTags()).values()) {
        for (const inputFile of tag.inputFiles.values()) {
          if (inputFile.path === swaggerPathResolved) {
            /** @type {Map<string, Tag>} */
            const tags = affectedReadmeTags.get(readme.path) ?? new Map();
            tags.set(tag.name, tag);
            affectedReadmeTags.set(readme.path, tags);

            // No need to check refs if the swagger file is directly referenced
            continue;
          }

          const refs = await inputFile.getRefs();
          if (refs.get(swaggerPathResolved)) {
            /** @type {Map<string, Tag>} */
            const tags = affectedReadmeTags.get(readme.path) ?? new Map();
            tags.set(tag.name, tag);
            affectedReadmeTags.set(readme.path, tags);
          }
        }
      }
    }

    return affectedReadmeTags;
  }

  /**
   * Given a swagger file, return the swagger files that are affected by the
   * changes in the given swagger file.
   * @param {string} swaggerPath
   * @returns {Promise<Map<string, Swagger>>} map of swagger paths to Swagger objects
   */
  async getAffectedSwaggers(swaggerPath) {
    const swaggerPathResolved = resolveCached(swaggerPath);

    /** @type {Map<string, Swagger>} */
    const affectedSwaggers = new Map();

    for (const readme of (await this.getReadmes()).values()) {
      for (const tag of (await readme.getTags()).values()) {
        for (const swagger of tag.inputFiles.values()) {
          // readme.md includes swaggerPath
          if (swagger.path === swaggerPathResolved) {
            affectedSwaggers.set(swagger.path, swagger);
          }

          const refs = await swagger.getRefs();

          // readme.md includes a.json
          //   a.json references swaggerPath
          const refToSwaggerPath = refs.get(swaggerPathResolved);
          if (refToSwaggerPath) {
            // Add the Swagger object for swaggerPath
            affectedSwaggers.set(refToSwaggerPath.path, refToSwaggerPath);

            // Add the Swagger object that references swaggerPath
            //
            // Example: a.json
            affectedSwaggers.set(swagger.path, swagger);
          }

          // readme.md includes a.json
          //   a.json references b.json
          //     b.json references swaggerPath
          for (const ref of refs.values()) {
            const refRefs = await ref.getRefs();
            const refRefToSwaggerPath = refRefs.get(swaggerPathResolved);
            if (refRefToSwaggerPath) {
              // Add the Swagger object for swaggerPath
              affectedSwaggers.set(refRefToSwaggerPath.path, refRefToSwaggerPath);

              // Add the Swagger object that references swaggerPath
              //
              // Example: b.json
              affectedSwaggers.set(ref.path, ref);

              // Add the Swagger object that references the Swagger object
              // that references swaggerPath
              //
              // Example: a.json
              //
              // Note: This may not be strictly necessary, since getRefs() includes
              // transitive references, so "a.json" should have already been added
              // above.  However, it's safer to add it, in case somehow it wasn't added
              // earlier, since we know it's in the dependency chain.
              affectedSwaggers.set(swagger.path, swagger);
            }
          }
        }
      }
    }

    // The swagger file supplied does not exist in the given specModel
    if (affectedSwaggers.size === 0) {
      throw new SpecModelError(
        `Swagger file ${swaggerPath} not found in specModel.\n` +
          `It must be referenced in the "input-file" section of a tag in a readme.md file ` +
          `or in a swagger JSON file using $ref.`,
        { source: swaggerPath },
      );
    }

    return affectedSwaggers;
  }

  /**
   * @returns {Promise<Map<string, Readme>>} map of readme paths to readme Objects
   */
  async getReadmes() {
    if (!this.#readmes) {
      const files = await readdir(this.#folder, {
        recursive: true,
      });

      const readmePaths = files
        // filter before resolve to (slightly) improve perf, since filter only needs filename
        .filter(readme)
        .map((p) => resolvePairCached(this.#folder, p));

      this.#logger?.debug(`Found ${readmePaths.length} readme files`);

      this.#readmes = new Map(
        readmePaths.map((p) => {
          const readme = new Readme(p, {
            logger: this.#logger,
            specModel: this,
          });
          return [readme.path, readme];
        }),
      );
    }

    return this.#readmes;
  }

  async getSwaggers() {
    const readmes = [...(await this.getReadmes()).values()];
    const tags = await flatMapAsync(readmes, async (r) => [...(await r.getTags()).values()]);
    const swaggers = tags.flatMap((t) => [...t.inputFiles.values()]);
    const refs = await flatMapAsync(swaggers, async (s) => [...(await s.getRefs()).values()]);
    return [...swaggers, ...refs];
  }

  /**
   * @param {ToJSONOptions} [options]
   * @returns {Promise<SpecModelJSON|ErrorJSON>}
   */
  async toJSONAsync(options = {}) {
    return await embedError(async () => {
      const readmes = await mapAsync(
        [...(await this.getReadmes()).values()].sort((a, b) => a.path.localeCompare(b.path)),
        async (r) => await r.toJSONAsync(options),
      );
      return {
        folder: this.#folder,
        readmes,
      };
    }, options);
  }

  /**
   * @returns {string}
   */
  toString() {
    return `SpecModel(${this.#folder}, {logger: ${inspect(this.#logger)}}})`;
  }
}

/**
 * @template T
 * @param {() => Promise<T>} fn
 * @param {Object} [options]
 * @param {boolean} [options.embedErrors]
 * @returns {Promise<T|ErrorJSON>}
 */
export async function embedError(fn, options = {}) {
  const { embedErrors } = options;

  try {
    return await fn();
  } catch (error) {
    if (embedErrors && error instanceof Error) {
      return { error: error.message };
    } else {
      throw error;
    }
  }
}
