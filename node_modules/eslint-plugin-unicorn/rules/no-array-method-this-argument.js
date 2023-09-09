'use strict';
const {hasSideEffect} = require('@eslint-community/eslint-utils');
const {methodCallSelector, notFunctionSelector} = require('./selectors/index.js');
const {removeArgument} = require('./fix/index.js');
const {getParentheses, getParenthesizedText} = require('./utils/parentheses.js');
const shouldAddParenthesesToMemberExpressionObject = require('./utils/should-add-parentheses-to-member-expression-object.js');
const {isNodeMatches} = require('./utils/is-node-matches.js');

const ERROR = 'error';
const SUGGESTION_BIND = 'suggestion-bind';
const SUGGESTION_REMOVE = 'suggestion-remove';
const messages = {
	[ERROR]: 'Do not use the `this` argument in `Array#{{method}}()`.',
	[SUGGESTION_REMOVE]: 'Remove the second argument.',
	[SUGGESTION_BIND]: 'Use a bound function.',
};

const ignored = [
	'lodash.every',
	'_.every',
	'underscore.every',

	'lodash.filter',
	'_.filter',
	'underscore.filter',
	'Vue.filter',
	'R.filter',

	'lodash.find',
	'_.find',
	'underscore.find',
	'R.find',

	'lodash.findLast',
	'_.findLast',
	'underscore.findLast',
	'R.findLast',

	'lodash.findIndex',
	'_.findIndex',
	'underscore.findIndex',
	'R.findIndex',

	'lodash.findLastIndex',
	'_.findLastIndex',
	'underscore.findLastIndex',
	'R.findLastIndex',

	'lodash.flatMap',
	'_.flatMap',

	'lodash.forEach',
	'_.forEach',
	'React.Children.forEach',
	'Children.forEach',
	'R.forEach',

	'lodash.map',
	'_.map',
	'underscore.map',
	'React.Children.map',
	'Children.map',
	'jQuery.map',
	'$.map',
	'R.map',

	'lodash.some',
	'_.some',
	'underscore.some',
];

const selector = [
	methodCallSelector({
		methods: [
			'every',
			'filter',
			'find',
			'findLast',
			'findIndex',
			'findLastIndex',
			'flatMap',
			'forEach',
			'map',
			'some',
		],
		argumentsLength: 2,
	}),
	notFunctionSelector('arguments.0'),
].join('');

function removeThisArgument(callExpression, sourceCode) {
	return fixer => removeArgument(fixer, callExpression.arguments[1], sourceCode);
}

function useBoundFunction(callExpression, sourceCode) {
	return function * (fixer) {
		yield removeThisArgument(callExpression, sourceCode)(fixer);

		const [callback, thisArgument] = callExpression.arguments;

		const callbackParentheses = getParentheses(callback, sourceCode);
		const isParenthesized = callbackParentheses.length > 0;
		const callbackLastToken = isParenthesized
			? callbackParentheses[callbackParentheses.length - 1]
			: callback;
		if (
			!isParenthesized
			&& shouldAddParenthesesToMemberExpressionObject(callback, sourceCode)
		) {
			yield fixer.insertTextBefore(callbackLastToken, '(');
			yield fixer.insertTextAfter(callbackLastToken, ')');
		}

		const thisArgumentText = getParenthesizedText(thisArgument, sourceCode);
		// `thisArgument` was a argument, no need add extra parentheses
		yield fixer.insertTextAfter(callbackLastToken, `.bind(${thisArgumentText})`);
	};
}

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const sourceCode = context.getSourceCode();

	return {
		[selector](callExpression) {
			const {callee} = callExpression;
			if (isNodeMatches(callee, ignored)) {
				return;
			}

			const method = callee.property.name;
			const [callback, thisArgument] = callExpression.arguments;

			const problem = {
				node: thisArgument,
				messageId: ERROR,
				data: {method},
			};

			const thisArgumentHasSideEffect = hasSideEffect(thisArgument, sourceCode);
			const isArrowCallback = callback.type === 'ArrowFunctionExpression';

			if (isArrowCallback) {
				if (thisArgumentHasSideEffect) {
					problem.suggest = [
						{
							messageId: SUGGESTION_REMOVE,
							fix: removeThisArgument(callExpression, sourceCode),
						},
					];
				} else {
					problem.fix = removeThisArgument(callExpression, sourceCode);
				}

				return problem;
			}

			problem.suggest = [
				{
					messageId: SUGGESTION_REMOVE,
					fix: removeThisArgument(callExpression, sourceCode),
				},
				{
					messageId: SUGGESTION_BIND,
					fix: useBoundFunction(callExpression, sourceCode),
				},
			];

			return problem;
		},
	};
};

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Disallow using the `this` argument in array methods.',
		},
		fixable: 'code',
		hasSuggestions: true,
		messages,
	},
};
