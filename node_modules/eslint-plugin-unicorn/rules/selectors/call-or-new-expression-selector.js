'use strict';

const matches = require('./matches-any.js');

/**
@typedef {
	{
		path?: string,
		name?: string,
		names?: string[],
		argumentsLength?: number,
		minimumArguments?: number,
		maximumArguments?: number,
		includeOptional?: boolean,
		allowSpreadElement?: boolean,
	} | string | string[]
} CallOrNewExpressionOptions
*/
function create(options, types) {
	if (typeof options === 'string') {
		options = {names: [options]};
	}

	if (Array.isArray(options)) {
		options = {names: options};
	}

	let {
		path,
		name,
		names,
		argumentsLength,
		minimumArguments,
		maximumArguments,
		includeOptional,
		allowSpreadElement,
	} = {
		path: '',
		minimumArguments: 0,
		maximumArguments: Number.POSITIVE_INFINITY,
		includeOptional: false,
		allowSpreadElement: false,
		...options,
	};

	const prefix = path ? `${path}.` : '';
	if (name) {
		names = [name];
	}

	const parts = [
		matches(types.map(type => `[${prefix}type="${type}"]`)),
	];

	if (!includeOptional) {
		parts.push(`[${prefix}optional!=true]`);
	}

	if (typeof argumentsLength === 'number') {
		parts.push(`[${prefix}arguments.length=${argumentsLength}]`);
	}

	if (minimumArguments !== 0) {
		parts.push(`[${prefix}arguments.length>=${minimumArguments}]`);
	}

	if (Number.isFinite(maximumArguments)) {
		parts.push(`[${prefix}arguments.length<=${maximumArguments}]`);
	}

	if (!allowSpreadElement) {
		const maximumArgumentsLength = Number.isFinite(maximumArguments) ? maximumArguments : argumentsLength;
		if (typeof maximumArgumentsLength === 'number') {
			// Exclude arguments with `SpreadElement` type
			for (let index = 0; index < maximumArgumentsLength; index += 1) {
				parts.push(`[${prefix}arguments.${index}.type!="SpreadElement"]`);
			}
		}
	}

	if (Array.isArray(names) && names.length > 0) {
		parts.push(
			`[${prefix}callee.type="Identifier"]`,
			matches(names.map(property => `[${prefix}callee.name="${property}"]`)),
		);
	}

	return parts.join('');
}

/**
@param {CallOrNewExpressionOptions} [options]
@returns {string}
*/
const callExpressionSelector = options => create(options, ['CallExpression']);

/**
@param {CallOrNewExpressionOptions} [options]
@returns {string}
*/
const newExpressionSelector = options => create(options, ['NewExpression']);

/**
@param {CallOrNewExpressionOptions} [options]
@returns {string}
*/
const callOrNewExpressionSelector = options => create(options, ['CallExpression', 'NewExpression']);

module.exports = {
	newExpressionSelector,
	callExpressionSelector,
	callOrNewExpressionSelector,
};
