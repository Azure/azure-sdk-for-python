'use strict';
const cleanRegexp = require('clean-regexp');
const {optimize} = require('regexp-tree');
const escapeString = require('./utils/escape-string.js');
const {newExpressionSelector} = require('./selectors/index.js');
const {isStringLiteral} = require('./ast/index.js');

const MESSAGE_ID = 'better-regex';
const MESSAGE_ID_PARSE_ERROR = 'better-regex/parse-error';
const messages = {
	[MESSAGE_ID]: '{{original}} can be optimized to {{optimized}}.',
	[MESSAGE_ID_PARSE_ERROR]: 'Problem parsing {{original}}: {{error}}',
};

const newRegExp = newExpressionSelector({name: 'RegExp', minimumArguments: 1});

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const {sortCharacterClasses} = context.options[0] || {};

	const ignoreList = [];

	if (sortCharacterClasses === false) {
		ignoreList.push('charClassClassrangesMerge');
	}

	return {
		'Literal[regex]'(node) {
			const {raw: original, regex} = node;

			// Regular Expressions with `u` flag are not well handled by `regexp-tree`
			// https://github.com/DmitrySoshnikov/regexp-tree/issues/162
			if (regex.flags.includes('u')) {
				return;
			}

			let optimized = original;

			try {
				optimized = optimize(original, undefined, {blacklist: ignoreList}).toString();
			} catch (error) {
				return {
					node,
					messageId: MESSAGE_ID_PARSE_ERROR,
					data: {
						original,
						error: error.message,
					},
				};
			}

			if (original === optimized) {
				return;
			}

			const problem = {
				node,
				messageId: MESSAGE_ID,
				data: {
					original,
					optimized,
				},
			};

			if (
				node.parent.type === 'MemberExpression'
				&& node.parent.object === node
				&& !node.parent.optional
				&& !node.parent.computed
				&& node.parent.property.type === 'Identifier'
				&& (
					node.parent.property.name === 'toString'
					|| node.parent.property.name === 'source'
				)
			) {
				return problem;
			}

			return Object.assign(problem, {
				fix: fixer => fixer.replaceText(node, optimized),
			});
		},
		[newRegExp](node) {
			const [patternNode, flagsNode] = node.arguments;

			if (!isStringLiteral(patternNode)) {
				return;
			}

			const oldPattern = patternNode.value;
			const flags = isStringLiteral(flagsNode)
				? flagsNode.value
				: '';

			const newPattern = cleanRegexp(oldPattern, flags);

			if (oldPattern !== newPattern) {
				return {
					node,
					messageId: MESSAGE_ID,
					data: {
						original: oldPattern,
						optimized: newPattern,
					},
					fix: fixer => fixer.replaceText(
						patternNode,
						escapeString(newPattern, patternNode.raw.charAt(0)),
					),
				};
			}
		},
	};
};

const schema = [
	{
		type: 'object',
		additionalProperties: false,
		properties: {
			sortCharacterClasses: {
				type: 'boolean',
				default: true,
			},
		},
	},
];

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Improve regexes by making them shorter, consistent, and safer.',
		},
		fixable: 'code',
		schema,
		messages,
	},
};
