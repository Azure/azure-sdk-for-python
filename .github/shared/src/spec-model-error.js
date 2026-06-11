export class SpecModelError extends Error {
  /**
   * Path to file that caused the error
   *
   * @type {string|undefined}
   */
  #source;

  /**
   * Path to readme that caused the error (if known)
   * @type {string|undefined}
   */
  #readme;

  /**
   * Name of tag that caused the error (if known)
   * @type {string|undefined}
   */
  #tag;

  /**
   * @param {string} message
   * @param {Object} [options]
   * @param {Error} [options.cause]
   * @param {string} [options.source] Path to file that caused the error
   * @param {string} [options.readme] Path to readme that caused the error (if known)
   * @param {string} [options.tag] Name of tag that caused the error (if known)
   */
  constructor(message, options = {}) {
    const { cause, source, readme, tag } = options;

    const fullMessage =
      message +
      (source ? `\n  Problem File: ${source}` : "") +
      (readme ? `\n  Readme: ${readme}` : "") +
      (tag ? `\n  Tag: ${tag}` : "") +
      (cause ? `\n  Cause: ${cause}` : "");

    super(fullMessage, { cause });

    this.name = this.constructor.name;

    this.#source = source;
    this.#readme = readme;
    this.#tag = tag;
  }

  get source() {
    return this.#source;
  }

  get readme() {
    return this.#readme;
  }

  get tag() {
    return this.#tag;
  }
}
