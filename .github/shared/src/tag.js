import { inspect } from "util";
import { mapAsync } from "./array.js";
import { embedError } from "./spec-model.js";
import { Swagger } from "./swagger.js";

/**
 * @typedef {import('./spec-model.js').ErrorJSON} ErrorJSON
 * @typedef {import('./readme.js').Readme} Readme
 * @typedef {import('./swagger.js').SwaggerJSON} SwaggerJSON
 * @typedef {import('./spec-model.js').ToJSONOptions} ToJSONOptions
 */

/**
 * @typedef {Object} TagJSON
 * @property {string} name
 * @property {(SwaggerJSON|ErrorJSON)[]} inputFiles
 */

export class Tag {
  /** @type {Map<string, Swagger>} */
  #inputFiles;

  /** @type {import('./logger.js').ILogger | undefined} */
  #logger;

  /** @type {string} */
  #name;

  /**
   * Readme that contains this Tag
   * @type {Readme | undefined}
   */
  #readme;

  /**
   * @param {string} name
   * @param {string[]} inputFilePaths
   * @param {Object} [options]
   * @param {import('./logger.js').ILogger} [options.logger]
   * @param {Readme} [options.readme]
   */
  constructor(name, inputFilePaths, options = {}) {
    const { logger, readme } = options;

    this.#name = name;
    this.#logger = logger;
    this.#readme = readme;

    this.#inputFiles = new Map(
      inputFilePaths.map((p) => {
        let swagger = new Swagger(p, { logger: this.#logger, tag: this });
        return [swagger.path, swagger];
      }),
    );
  }

  /**
   * @returns {Map<string, Swagger>}
   */
  get inputFiles() {
    return this.#inputFiles;
  }

  /**
   * @returns {string}
   */
  get name() {
    return this.#name;
  }

  /**
   * @returns {Readme | undefined} Readme that contains this Tag
   */
  get readme() {
    return this.#readme;
  }

  /**
   * @param {ToJSONOptions} [options]
   * @returns {Promise<TagJSON|ErrorJSON>}
   */
  async toJSONAsync(options = {}) {
    return await embedError(
      async () => ({
        name: this.#name,
        inputFiles: await mapAsync(
          [...this.#inputFiles.values()].sort((a, b) => a.path.localeCompare(b.path)),
          async (s) => await s.toJSONAsync(options),
        ),
      }),
      options,
    );
  }

  toString() {
    return `Tag(${this.#name}, {logger: ${inspect(this.#logger)}})`;
  }
}
