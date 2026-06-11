/**
 * @template T
 * @param {T[]} array
 * @param {(item: T, index: number, array: T[]) => Promise<boolean>} asyncPredicate
 * @returns {Promise<T[]>}
 */
export async function filterAsync(array, asyncPredicate) {
  const results = await mapAsync(array, asyncPredicate);
  return array.filter((_, i) => results[i]);
}

/**
 * @template T,U
 * @param {T[]} array
 * @param {(item: T, index: number, array: T[]) => Promise<U[]>} asyncMapper
 * @returns {Promise<U[]>}
 */
export async function flatMapAsync(array, asyncMapper) {
  const mapped = await mapAsync(array, asyncMapper);
  return mapped.flat();
}

/**
 *  Returns true if `array` includes no elements from `values`
 *
 * @template T,U
 * @param {T[]} array
 * @param {(item: T, index: number, array: T[]) => Promise<U>} asyncMapper
 * @returns {Promise<U[]>}
 */
export async function mapAsync(array, asyncMapper) {
  return Promise.all(array.map(asyncMapper));
}

/**
 *  Returns true if `array` includes every element from `values`
 *
 * @template T
 * @param {T[]} array
 * @param {T[]} values
 * @returns {boolean}
 */
export function includesEvery(array, values) {
  return values.every((value) => array.includes(value));
}

/**
 * @template T
 * @param {T[]} array
 * @param {T[]} values
 * @returns {boolean}
 */
export function includesNone(array, values) {
  return values.every((value) => !array.includes(value));
}
