/* eslint-disable prefer-rest-params */
'use strict';

/** Memoize a function using a custom cache and a key formatter
 *
 * (rambda does not include a memoizeWith function)
 *
 * @param {Function} keyGen The function to generate the cache key.
 * @param {Function} fn The function to memoize.
 * @return {Function} Memoized version of `fn`.
 */
const memoizeWith = (keyGen, fn) => {
    const cache = new Map();

    return function () {
        const key = keyGen(arguments);

        if (!cache.has(key)) {
            cache.set(key, fn.apply(this, arguments));
        }

        return cache.get(key);
    };
};

module.exports = {
    memoizeWith
};
