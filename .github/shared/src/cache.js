/**
 * Caches values in memory with a single key of any type.
 *
 * @template K, V
 */
export class KeyedCache {
  /** @type {Map<K, V>} */
  #map = new Map();

  /**
   * Returns cached value, initializing if necessary
   *
   * @param {K} key
   * @param {() => V} factory
   * @returns {V} cached value
   *
   * @example
   * const result = cache.getOrCreate(42, async () => await doWork(42));
   */
  getOrCreate(key, factory) {
    let value = this.#map.get(key);

    if (value === undefined) {
      value = factory();
      this.#map.set(key, value);
    }

    return value;
  }
}

/**
 * Caches values in memory with an ordered pair of keys of any types.
 *
 * @template K1, K2, V
 */
export class KeyedPairCache {
  // Two-layer nested cache
  /** @type {KeyedCache<K1, KeyedCache<K2, V>>} */
  #cache1 = new KeyedCache();

  /**
   * Returns cached value, initializing if necessary.
   * Keys are ordered, so (key1, key2) != (key2, key1).
   *
   * @param {K1} key1
   * @param {K2} key2
   * @param {() => V} factory
   * @returns {V} cached value
   *
   * @example
   * const result = cache.getOrCreate(42, 7 async () => await doWork(42, 7));
   */
  getOrCreate(key1, key2, factory) {
    // key1 => cache for the next layer
    const cache2 = this.#cache1.getOrCreate(key1, () => new KeyedCache());

    // key2 => final value
    return cache2.getOrCreate(key2, factory);
  }
}
