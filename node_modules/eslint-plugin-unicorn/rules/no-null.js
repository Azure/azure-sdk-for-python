'use strict';
const {
	not,
	methodCallSelector,
	callExpressionSelector,
} = require('./selectors/index.js');

const ERROR_MESSAGE_ID = 'error';
const SUGGESTION_REPLACE_MESSAGE_ID = 'replace';
const SUGGESTION_REMOVE_MESSAGE_ID = 'remove';
const messages = {
	[ERROR_MESSAGE_ID]: 'Use `undefined` instead of `null`.',
	[SUGGESTION_REPLACE_MESSAGE_ID]: 'Replace `null` with `undefined`.',
	[SUGGESTION_REMOVE_MESSAGE_ID]: 'Remove `null`.',
};

const selector = [
	'Literal',
	'[raw="null"]',
	not([
		// `Object.create(null)`, `Object.create(null, foo)`
		`${methodCallSelector({object: 'Object', method: 'create', minimumArguments: 1, maximumArguments: 2})} > .arguments:first-child`,
		// `useRef(null)`
		`${callExpressionSelector({name: 'useRef', argumentsLength: 1})} > .arguments:first-child`,
		// `React.useRef(null)`
		`${methodCallSelector({object: 'React', method: 'useRef', argumentsLength: 1})} > .arguments:first-child`,
		// `foo.insertBefore(bar, null)`
		`${methodCallSelector({method: 'insertBefore', argumentsLength: 2})}[arguments.0.type!="SpreadElement"] > .arguments:nth-child(2)`,
	]),
].join('');

const isLooseEqual = node => node.type === 'BinaryExpression' && ['==', '!='].includes(node.operator);
const isStrictEqual = node => node.type === 'BinaryExpression' && ['===', '!=='].includes(node.operator);

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const {checkStrictEquality} = {
		checkStrictEquality: false,
		...context.options[0],
	};

	return {
		[selector](node) {
			const {parent} = node;
			if (!checkStrictEquality && isStrictEqual(parent)) {
				return;
			}

			const problem = {
				node,
				messageId: ERROR_MESSAGE_ID,
			};

			const useUndefinedFix = fixer => fixer.replaceText(node, 'undefined');

			if (isLooseEqual(parent)) {
				problem.fix = useUndefinedFix;
				return problem;
			}

			const useUndefinedSuggestion = {
				messageId: SUGGESTION_REPLACE_MESSAGE_ID,
				fix: useUndefinedFix,
			};

			if (parent.type === 'ReturnStatement' && parent.argument === node) {
				problem.suggest = [
					{
						messageId: SUGGESTION_REMOVE_MESSAGE_ID,
						fix: fixer => fixer.remove(node),
					},
					useUndefinedSuggestion,
				];
				return problem;
			}

			if (parent.type === 'VariableDeclarator' && parent.init === node && parent.parent.kind !== 'const') {
				problem.suggest = [
					{
						messageId: SUGGESTION_REMOVE_MESSAGE_ID,
						fix: fixer => fixer.removeRange([parent.id.range[1], node.range[1]]),
					},
					useUndefinedSuggestion,
				];
				return problem;
			}

			problem.suggest = [useUndefinedSuggestion];
			return problem;
		},
	};
};

const schema = [
	{
		type: 'object',
		additionalProperties: false,
		properties: {
			checkStrictEquality: {
				type: 'boolean',
				default: false,
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
			description: 'Disallow the use of the `null` literal.',
		},
		fixable: 'code',
		hasSuggestions: true,
		schema,
		messages,
	},
};
