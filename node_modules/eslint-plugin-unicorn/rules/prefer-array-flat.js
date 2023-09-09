'use strict';
const {
	methodCallSelector,
	arrayPrototypeMethodSelector,
	emptyArraySelector,
	callExpressionSelector,
} = require('./selectors/index.js');
const needsSemicolon = require('./utils/needs-semicolon.js');
const shouldAddParenthesesToMemberExpressionObject = require('./utils/should-add-parentheses-to-member-expression-object.js');
const {isNodeMatches, isNodeMatchesNameOrPath} = require('./utils/is-node-matches.js');
const {getParenthesizedText, isParenthesized} = require('./utils/parentheses.js');
const {fixSpaceAroundKeyword} = require('./fix/index.js');

const MESSAGE_ID = 'prefer-array-flat';
const messages = {
	[MESSAGE_ID]: 'Prefer `Array#flat()` over `{{description}}` to flatten an array.',
};

// `array.flatMap(x => x)`
const arrayFlatMap = {
	selector: [
		methodCallSelector({
			method: 'flatMap',
			argumentsLength: 1,
		}),
		'[arguments.0.type="ArrowFunctionExpression"]',
		'[arguments.0.async!=true]',
		'[arguments.0.generator!=true]',
		'[arguments.0.params.length=1]',
		'[arguments.0.params.0.type="Identifier"]',
		'[arguments.0.body.type="Identifier"]',
	].join(''),
	testFunction: node => node.arguments[0].params[0].name === node.arguments[0].body.name,
	getArrayNode: node => node.callee.object,
	description: 'Array#flatMap()',
};

// `array.reduce((a, b) => a.concat(b), [])`
const arrayReduce = {
	selector: [
		methodCallSelector({
			method: 'reduce',
			argumentsLength: 2,
		}),
		'[arguments.0.type="ArrowFunctionExpression"]',
		'[arguments.0.async!=true]',
		'[arguments.0.generator!=true]',
		'[arguments.0.params.length=2]',
		'[arguments.0.params.0.type="Identifier"]',
		'[arguments.0.params.1.type="Identifier"]',
		methodCallSelector({
			method: 'concat',
			argumentsLength: 1,
			path: 'arguments.0.body',
		}),
		'[arguments.0.body.callee.object.type="Identifier"]',
		'[arguments.0.body.arguments.0.type="Identifier"]',
		emptyArraySelector('arguments.1'),
	].join(''),
	testFunction: node =>
		node.arguments[0].params[0].name === node.arguments[0].body.callee.object.name
		&& node.arguments[0].params[1].name === node.arguments[0].body.arguments[0].name,
	getArrayNode: node => node.callee.object,
	description: 'Array#reduce()',
};

// `array.reduce((a, b) => [...a, ...b], [])`
const arrayReduce2 = {
	selector: [
		methodCallSelector({
			method: 'reduce',
			argumentsLength: 2,
		}),
		'[arguments.0.type="ArrowFunctionExpression"]',
		'[arguments.0.async!=true]',
		'[arguments.0.generator!=true]',
		'[arguments.0.params.length=2]',
		'[arguments.0.params.0.type="Identifier"]',
		'[arguments.0.params.1.type="Identifier"]',
		'[arguments.0.body.type="ArrayExpression"]',
		'[arguments.0.body.elements.length=2]',
		'[arguments.0.body.elements.0.type="SpreadElement"]',
		'[arguments.0.body.elements.0.argument.type="Identifier"]',
		'[arguments.0.body.elements.1.type="SpreadElement"]',
		'[arguments.0.body.elements.1.argument.type="Identifier"]',
		emptyArraySelector('arguments.1'),
	].join(''),
	testFunction: node =>
		node.arguments[0].params[0].name === node.arguments[0].body.elements[0].argument.name
		&& node.arguments[0].params[1].name === node.arguments[0].body.elements[1].argument.name,
	getArrayNode: node => node.callee.object,
	description: 'Array#reduce()',
};

// `[].concat(maybeArray)` and `[].concat(...array)`
const emptyArrayConcat = {
	selector: [
		methodCallSelector({
			method: 'concat',
			argumentsLength: 1,
			allowSpreadElement: true,
		}),
		emptyArraySelector('callee.object'),
	].join(''),
	getArrayNode(node) {
		const argumentNode = node.arguments[0];
		return argumentNode.type === 'SpreadElement' ? argumentNode.argument : argumentNode;
	},
	description: '[].concat()',
	shouldSwitchToArray: node => node.arguments[0].type !== 'SpreadElement',
};

// - `[].concat.apply([], array)` and `Array.prototype.concat.apply([], array)`
// - `[].concat.call([], maybeArray)` and `Array.prototype.concat.call([], maybeArray)`
// - `[].concat.call([], ...array)` and `Array.prototype.concat.call([], ...array)`
const arrayPrototypeConcat = {
	selector: [
		methodCallSelector({
			methods: ['apply', 'call'],
			argumentsLength: 2,
			allowSpreadElement: true,
		}),
		emptyArraySelector('arguments.0'),
		arrayPrototypeMethodSelector({
			path: 'callee.object',
			method: 'concat',
		}),
	].join(''),
	testFunction: node => node.arguments[1].type !== 'SpreadElement' || node.callee.property.name === 'call',
	getArrayNode(node) {
		const argumentNode = node.arguments[1];
		return argumentNode.type === 'SpreadElement' ? argumentNode.argument : argumentNode;
	},
	description: 'Array.prototype.concat()',
	shouldSwitchToArray: node => node.arguments[1].type !== 'SpreadElement' && node.callee.property.name === 'call',
};

const lodashFlattenFunctions = [
	'_.flatten',
	'lodash.flatten',
	'underscore.flatten',
];
const anyCall = {
	selector: callExpressionSelector({argumentsLength: 1}),
	getArrayNode: node => node.arguments[0],
};

function fix(node, array, sourceCode, shouldSwitchToArray) {
	if (typeof shouldSwitchToArray === 'function') {
		shouldSwitchToArray = shouldSwitchToArray(node);
	}

	return function * (fixer) {
		let fixed = getParenthesizedText(array, sourceCode);
		if (shouldSwitchToArray) {
			// `array` is an argument, when it changes to `array[]`, we don't need add extra parentheses
			fixed = `[${fixed}]`;
			// And we don't need to add parentheses to the new array to call `.flat()`
		} else if (
			!isParenthesized(array, sourceCode)
			&& shouldAddParenthesesToMemberExpressionObject(array, sourceCode)
		) {
			fixed = `(${fixed})`;
		}

		fixed = `${fixed}.flat()`;

		const tokenBefore = sourceCode.getTokenBefore(node);
		if (needsSemicolon(tokenBefore, sourceCode, fixed)) {
			fixed = `;${fixed}`;
		}

		yield fixer.replaceText(node, fixed);

		yield * fixSpaceAroundKeyword(fixer, node, sourceCode);
	};
}

function create(context) {
	const {functions: configFunctions} = {
		functions: [],
		...context.options[0],
	};
	const functions = [...configFunctions, ...lodashFlattenFunctions];
	const sourceCode = context.getSourceCode();
	const listeners = {};

	const cases = [
		arrayFlatMap,
		arrayReduce,
		arrayReduce2,
		emptyArrayConcat,
		arrayPrototypeConcat,
		{
			...anyCall,
			testFunction: node => isNodeMatches(node.callee, functions),
			description: node => `${functions.find(nameOrPath => isNodeMatchesNameOrPath(node.callee, nameOrPath)).trim()}()`,
		},
	];

	for (const {selector, testFunction, description, getArrayNode, shouldSwitchToArray} of cases) {
		listeners[selector] = function (node) {
			if (testFunction && !testFunction(node)) {
				return;
			}

			const array = getArrayNode(node);

			const data = {
				description: typeof description === 'string' ? description : description(node),
			};

			const problem = {
				node,
				messageId: MESSAGE_ID,
				data,
			};

			// Don't fix if it has comments.
			if (
				sourceCode.getCommentsInside(node).length
				=== sourceCode.getCommentsInside(array).length
			) {
				problem.fix = fix(node, array, sourceCode, shouldSwitchToArray);
			}

			return problem;
		};
	}

	return listeners;
}

const schema = [
	{
		type: 'object',
		additionalProperties: false,
		properties: {
			functions: {
				type: 'array',
				uniqueItems: true,
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
			description: 'Prefer `Array#flat()` over legacy techniques to flatten arrays.',
		},
		fixable: 'code',
		schema,
		messages,
	},
};
