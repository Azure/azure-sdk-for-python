'use strict';
const matches = require('./matches-any.js');

/**
@param {
	{
		path?: string,
		property?: string,
		properties?: string[],
		object?: string,
		objects?: string[],
		includeOptional?: boolean,
		allowComputed?: boolean
	} | string | string[]
} [options]
@returns {string}
*/
function memberExpressionSelector(options) {
	if (typeof options === 'string') {
		options = {properties: [options]};
	}

	if (Array.isArray(options)) {
		options = {properties: options};
	}

	let {
		path,
		property,
		properties,
		object,
		objects,
		includeOptional,
		allowComputed,
	} = {
		path: '',
		property: '',
		properties: [],
		object: '',
		includeOptional: false,
		allowComputed: false,
		...options,
	};

	const prefix = path ? `${path}.` : '';
	if (property) {
		properties = [property];
	}

	if (object) {
		objects = [object];
	}

	const parts = [
		`[${prefix}type="MemberExpression"]`,
	];

	if (!allowComputed) {
		parts.push(
			`[${prefix}computed!=true]`,
			`[${prefix}property.type="Identifier"]`,
		);
	}

	if (!includeOptional) {
		parts.push(`[${prefix}optional!=true]`);
	}

	if (Array.isArray(properties) && properties.length > 0) {
		parts.push(matches(properties.map(property => `[${prefix}property.name="${property}"]`)));
	}

	if (Array.isArray(objects) && objects.length > 0) {
		parts.push(
			`[${prefix}object.type="Identifier"]`,
			matches(objects.map(object => `[${prefix}object.name="${object}"]`)),
		);
	}

	return parts.join('');
}

module.exports = memberExpressionSelector;
