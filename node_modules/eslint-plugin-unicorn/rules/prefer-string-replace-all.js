'use strict';
const {getStaticValue} = require('@eslint-community/eslint-utils');
const {parse: parseRegExp} = require('regjsparser');
const escapeString = require('./utils/escape-string.js');
const {methodCallSelector} = require('./selectors/index.js');
const {isRegexLiteral, isNewExpression} = require('./ast/index.js');

const MESSAGE_ID_USE_REPLACE_ALL = 'method';
const MESSAGE_ID_USE_STRING = 'pattern';
const messages = {
	[MESSAGE_ID_USE_REPLACE_ALL]: 'Prefer `String#replaceAll()` over `String#replace()`.',
	[MESSAGE_ID_USE_STRING]: 'This pattern can be replaced with {{replacement}}.',
};

const selector = methodCallSelector({
	methods: ['replace', 'replaceAll'],
	argumentsLength: 2,
});

function getPatternReplacement(node) {
	if (!isRegexLiteral(node)) {
		return;
	}

	const {pattern, flags} = node.regex;
	if (flags.replace('u', '') !== 'g') {
		return;
	}

	let tree;

	try {
		tree = parseRegExp(pattern, flags, {
			unicodePropertyEscape: true,
			namedGroups: true,
			lookbehind: true,
		});
	} catch {
		return;
	}

	const parts = tree.type === 'alternative' ? tree.body : [tree];
	if (parts.some(part => part.type !== 'value')) {
		return;
	}

	// TODO: Preserve escape
	const string = String.fromCodePoint(...parts.map(part => part.codePoint));

	return escapeString(string);
}

const isRegExpWithGlobalFlag = (node, scope) => {
	if (isRegexLiteral(node)) {
		return node.regex.flags.includes('g');
	}

	if (
		isNewExpression(node, {name: 'RegExp'})
		&& node.arguments[0]?.type !== 'SpreadElement'
		&& node.arguments[1]?.type === 'Literal'
		&& typeof node.arguments[1].value === 'string'
	) {
		return node.arguments[1].value.includes('g');
	}

	const staticResult = getStaticValue(node, scope);

	// Don't know if there is `g` flag
	if (!staticResult) {
		return false;
	}

	const {value} = staticResult;
	return (
		Object.prototype.toString.call(value) === '[object RegExp]'
		&& value.global
	);
};

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => ({
	[selector](node) {
		const {
			arguments: [pattern],
			callee: {property},
		} = node;

		if (!isRegExpWithGlobalFlag(pattern, context.getSourceCode().getScope(pattern))) {
			return;
		}

		const methodName = property.name;
		const patternReplacement = getPatternReplacement(pattern);

		if (methodName === 'replaceAll') {
			if (!patternReplacement) {
				return;
			}

			return {
				node: pattern,
				messageId: MESSAGE_ID_USE_STRING,
				data: {
					// Show `This pattern can be replaced with a string literal.` for long strings
					replacement: patternReplacement.length < 20 ? patternReplacement : 'a string literal',
				},
				/** @param {import('eslint').Rule.RuleFixer} fixer */
				fix: fixer => fixer.replaceText(pattern, patternReplacement),
			};
		}

		return {
			node: property,
			messageId: MESSAGE_ID_USE_REPLACE_ALL,
			/** @param {import('eslint').Rule.RuleFixer} fixer */
			* fix(fixer) {
				yield fixer.insertTextAfter(property, 'All');

				if (!patternReplacement) {
					return;
				}

				yield fixer.replaceText(pattern, patternReplacement);
			},
		};
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer `String#replaceAll()` over regex searches with the global flag.',
		},
		fixable: 'code',
		messages,
	},
};
