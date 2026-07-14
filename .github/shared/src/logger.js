/**
 * @typedef {Object} ILogger
 * @property {(message:string) => void} debug
 * @property {(message:string) => void} error
 * @property {(message:string) => void} info
 * @property {(message:string) => void} warning
 * @property {() => boolean} isDebug
 */

/**
 * @implements {ILogger}
 */
export class ConsoleLogger {
  /** @type {boolean} */
  #isDebug;

  /**
   * @param {boolean} [isDebug] - If true, debug logs will be printed.  Default: false.
   */
  constructor(isDebug = false) {
    this.#isDebug = isDebug;
  }

  /**
   * @param {string} message
   */
  debug(message) {
    if (this.isDebug()) {
      console.debug(message);
    }
  }

  /**
   * @param {string} message
   */
  error(message) {
    console.error(message);
  }

  /**
   * @param {string} message
   */
  info(message) {
    console.log(message);
  }

  /**
   * @returns {boolean}
   */
  isDebug() {
    return this.#isDebug;
  }

  /**
   * @param {string} message
   */
  warning(message) {
    console.warn(message);
  }
}

// Singleton loggers
export const defaultLogger = new ConsoleLogger();
export const debugLogger = new ConsoleLogger(/*isDebug*/ true);
