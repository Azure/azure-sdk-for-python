'use strict';
const matches = require('./matches-any.js');
const memberExpressionSelector = require('./member-expression-selector.js');
const emptyArraySelector = require('./empty-array-selector.js');
const emptyObjectSelector = require('./empty-object-selector.js');

/**
@param {
	{
		path?: string,
		object?: string,
		method?: string,
		methods?: string[],
	}
} [options]
@returns {string}
*/
function prototypeMethodSelector(options) {
	const {
		path,
		object,
		method,
		methods,
	} = {
		path: '',
		method: '',
		methods: [],
		...options,
	};

	const objectPath = path ? `${path}.object` : 'object';

	const prototypeSelectors = [
		memberExpressionSelector({path: objectPath, property: 'prototype', object}),
	];

	switch (object) {
		case 'Array': {
			// `[].method` or `Array.prototype.method`
			prototypeSelectors.push(emptyArraySelector(objectPath));
			break;
		}

		case 'Object': {
			// `{}.method` or `Object.prototype.method`
			prototypeSelectors.push(emptyObjectSelector(objectPath));
			break;
		}
		// No default
	}

	return [
		memberExpressionSelector({
			path,
			property: method,
			properties: methods,
		}),
		matches(prototypeSelectors),
	].join('');
}

const arrayPrototypeMethodSelector = options => prototypeMethodSelector({...options, object: 'Array'});
const objectPrototypeMethodSelector = options => prototypeMethodSelector({...options, object: 'Object'});

module.exports = {
	arrayPrototypeMethodSelector,
	objectPrototypeMethodSelector,
};
