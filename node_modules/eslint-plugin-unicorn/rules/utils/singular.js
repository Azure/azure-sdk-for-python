'use strict';

const {singular: pluralizeSingular} = require('pluralize');

/**
Singularizes a word/name, i.e. `items` to `item`.

@param {string} original - The word/name to singularize.
@returns {string|undefined} - The singularized result, or `undefined` if attempting singularization resulted in no change.
*/
const singular = original => {
	const singularized = pluralizeSingular(original);
	if (singularized !== original) {
		return singularized;
	}
};

module.exports = singular;
