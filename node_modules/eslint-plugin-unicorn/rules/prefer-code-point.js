'use strict';
const {methodCallSelector} = require('./selectors/index.js');

const messages = {
	'error/charCodeAt': 'Prefer `String#codePointAt()` over `String#charCodeAt()`.',
	'error/fromCharCode': 'Prefer `String.fromCodePoint()` over `String.fromCharCode()`.',
	'suggestion/charCodeAt': 'Use `String#codePointAt()`.',
	'suggestion/fromCharCode': 'Use `String.fromCodePoint()`.',
};

const cases = [
	{
		selector: methodCallSelector('charCodeAt'),
		replacement: 'codePointAt',
	},
	{
		selector: methodCallSelector({object: 'String', method: 'fromCharCode'}),
		replacement: 'fromCodePoint',
	},
];

/** @param {import('eslint').Rule.RuleContext} context */
const create = () => Object.fromEntries(
	cases.map(({selector, replacement}) => [
		selector,
		node => {
			const method = node.callee.property;
			const methodName = method.name;
			const fix = fixer => fixer.replaceText(method, replacement);

			return {
				node: method,
				messageId: `error/${methodName}`,
				suggest: [
					{
						messageId: `suggestion/${methodName}`,
						fix,
					},
				],
			};
		},
	]),
);

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer `String#codePointAt(…)` over `String#charCodeAt(…)` and `String.fromCodePoint(…)` over `String.fromCharCode(…)`.',
		},
		hasSuggestions: true,
		messages,
	},
};
