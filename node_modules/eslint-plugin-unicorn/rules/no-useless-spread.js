'use strict';
const {isCommaToken} = require('@eslint-community/eslint-utils');
const {
	matches,
	newExpressionSelector,
	methodCallSelector,
} = require('./selectors/index.js');
const typedArray = require('./shared/typed-array.js');
const {
	removeParentheses,
	fixSpaceAroundKeyword,
	addParenthesizesToReturnOrThrowExpression,
} = require('./fix/index.js');
const isOnSameLine = require('./utils/is-on-same-line.js');
const {
	isParenthesized,
} = require('./utils/parentheses.js');
const {isNewExpression} = require('./ast/index.js');

const SPREAD_IN_LIST = 'spread-in-list';
const ITERABLE_TO_ARRAY = 'iterable-to-array';
const ITERABLE_TO_ARRAY_IN_FOR_OF = 'iterable-to-array-in-for-of';
const ITERABLE_TO_ARRAY_IN_YIELD_STAR = 'iterable-to-array-in-yield-star';
const CLONE_ARRAY = 'clone-array';
const messages = {
	[SPREAD_IN_LIST]: 'Spread an {{argumentType}} literal in {{parentDescription}} is unnecessary.',
	[ITERABLE_TO_ARRAY]: '`{{parentDescription}}` accepts iterable as argument, it\'s unnecessary to convert to an array.',
	[ITERABLE_TO_ARRAY_IN_FOR_OF]: '`for…of` can iterate over iterable, it\'s unnecessary to convert to an array.',
	[ITERABLE_TO_ARRAY_IN_YIELD_STAR]: '`yield*` can delegate iterable, it\'s unnecessary to convert to an array.',
	[CLONE_ARRAY]: 'Unnecessarily cloning an array.',
};

const uselessSpreadInListSelector = matches([
	'ArrayExpression > SpreadElement.elements > ArrayExpression.argument',
	'ObjectExpression > SpreadElement.properties > ObjectExpression.argument',
	'CallExpression > SpreadElement.arguments > ArrayExpression.argument',
	'NewExpression > SpreadElement.arguments > ArrayExpression.argument',
]);

const singleArraySpreadSelector = [
	'ArrayExpression',
	'[elements.length=1]',
	'[elements.0.type="SpreadElement"]',
].join('');
const uselessIterableToArraySelector = matches([
	[
		matches([
			newExpressionSelector({names: ['Map', 'WeakMap', 'Set', 'WeakSet'], argumentsLength: 1}),
			newExpressionSelector({names: typedArray, minimumArguments: 1}),
			methodCallSelector({
				object: 'Promise',
				methods: ['all', 'allSettled', 'any', 'race'],
				argumentsLength: 1,
			}),
			methodCallSelector({
				objects: ['Array', ...typedArray],
				method: 'from',
				argumentsLength: 1,
			}),
			methodCallSelector({object: 'Object', method: 'fromEntries', argumentsLength: 1}),
		]),
		' > ',
		`${singleArraySpreadSelector}.arguments:first-child`,
	].join(''),
	`ForOfStatement > ${singleArraySpreadSelector}.right`,
	`YieldExpression[delegate=true] > ${singleArraySpreadSelector}.argument`,
]);

const uselessArrayCloneSelector = [
	`${singleArraySpreadSelector} > .elements:first-child > .argument`,
	matches([
		// Array methods returns a new array
		methodCallSelector([
			'concat',
			'copyWithin',
			'filter',
			'flat',
			'flatMap',
			'map',
			'slice',
			'splice',
			'toReversed',
			'toSorted',
			'toSpliced',
			'with',
		]),
		// `String#split()`
		methodCallSelector('split'),
		// `Object.keys()` and `Object.values()`
		methodCallSelector({object: 'Object', methods: ['keys', 'values'], argumentsLength: 1}),
		// `await Promise.all()` and `await Promise.allSettled`
		[
			'AwaitExpression',
			methodCallSelector({
				object: 'Promise',
				methods: ['all', 'allSettled'],
				argumentsLength: 1,
				path: 'argument',
			}),
		].join(''),
		// `Array.from()`, `Array.of()`
		methodCallSelector({object: 'Array', methods: ['from', 'of']}),
		// `new Array()`
		newExpressionSelector('Array'),
	]),
].join('');

const parentDescriptions = {
	ArrayExpression: 'array literal',
	ObjectExpression: 'object literal',
	CallExpression: 'arguments',
	NewExpression: 'arguments',
};

function getCommaTokens(arrayExpression, sourceCode) {
	let startToken = sourceCode.getFirstToken(arrayExpression);

	return arrayExpression.elements.map((element, index, elements) => {
		if (index === elements.length - 1) {
			const penultimateToken = sourceCode.getLastToken(arrayExpression, {skip: 1});
			if (isCommaToken(penultimateToken)) {
				return penultimateToken;
			}

			return;
		}

		const commaToken = sourceCode.getTokenAfter(element || startToken, isCommaToken);
		startToken = commaToken;
		return commaToken;
	});
}

function * unwrapSingleArraySpread(fixer, arrayExpression, sourceCode) {
	const [
		openingBracketToken,
		spreadToken,
		thirdToken,
	] = sourceCode.getFirstTokens(arrayExpression, 3);

	// `[...value]`
	//  ^
	yield fixer.remove(openingBracketToken);

	// `[...value]`
	//   ^^^
	yield fixer.remove(spreadToken);

	const [
		commaToken,
		closingBracketToken,
	] = sourceCode.getLastTokens(arrayExpression, 2);

	// `[...value]`
	//           ^
	yield fixer.remove(closingBracketToken);

	// `[...value,]`
	//           ^
	if (isCommaToken(commaToken)) {
		yield fixer.remove(commaToken);
	}

	/*
	```js
	function foo() {
		return [
			...value,
		];
	}
	```
	*/
	const {parent} = arrayExpression;
	if (
		(parent.type === 'ReturnStatement' || parent.type === 'ThrowStatement')
		&& parent.argument === arrayExpression
		&& !isOnSameLine(openingBracketToken, thirdToken)
		&& !isParenthesized(arrayExpression, sourceCode)
	) {
		yield * addParenthesizesToReturnOrThrowExpression(fixer, parent, sourceCode);
		return;
	}

	yield * fixSpaceAroundKeyword(fixer, arrayExpression, sourceCode);
}

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const sourceCode = context.getSourceCode();

	return {
		[uselessSpreadInListSelector](spreadObject) {
			const spreadElement = spreadObject.parent;
			const spreadToken = sourceCode.getFirstToken(spreadElement);
			const parentType = spreadElement.parent.type;

			return {
				node: spreadToken,
				messageId: SPREAD_IN_LIST,
				data: {
					argumentType: spreadObject.type === 'ArrayExpression' ? 'array' : 'object',
					parentDescription: parentDescriptions[parentType],
				},
				/** @param {import('eslint').Rule.RuleFixer} fixer */
				* fix(fixer) {
					// `[...[foo]]`
					//   ^^^
					yield fixer.remove(spreadToken);

					// `[...(( [foo] ))]`
					//      ^^       ^^
					yield * removeParentheses(spreadObject, fixer, sourceCode);

					// `[...[foo]]`
					//      ^
					const firstToken = sourceCode.getFirstToken(spreadObject);
					yield fixer.remove(firstToken);

					const [
						penultimateToken,
						lastToken,
					] = sourceCode.getLastTokens(spreadObject, 2);

					// `[...[foo]]`
					//          ^
					yield fixer.remove(lastToken);

					// `[...[foo,]]`
					//          ^
					if (isCommaToken(penultimateToken)) {
						yield fixer.remove(penultimateToken);
					}

					if (parentType !== 'CallExpression' && parentType !== 'NewExpression') {
						return;
					}

					const commaTokens = getCommaTokens(spreadObject, sourceCode);
					for (const [index, commaToken] of commaTokens.entries()) {
						if (spreadObject.elements[index]) {
							continue;
						}

						// `call(...[foo, , bar])`
						//               ^ Replace holes with `undefined`
						yield fixer.insertTextBefore(commaToken, 'undefined');
					}
				},
			};
		},
		[uselessIterableToArraySelector](arrayExpression) {
			const {parent} = arrayExpression;
			let parentDescription = '';
			let messageId = ITERABLE_TO_ARRAY;
			switch (parent.type) {
				case 'ForOfStatement': {
					messageId = ITERABLE_TO_ARRAY_IN_FOR_OF;
					break;
				}

				case 'YieldExpression': {
					messageId = ITERABLE_TO_ARRAY_IN_YIELD_STAR;
					break;
				}

				case 'NewExpression': {
					parentDescription = `new ${parent.callee.name}(…)`;
					break;
				}

				case 'CallExpression': {
					parentDescription = `${parent.callee.object.name}.${parent.callee.property.name}(…)`;
					break;
				}
				// No default
			}

			return {
				node: arrayExpression,
				messageId,
				data: {parentDescription},
				fix: fixer => unwrapSingleArraySpread(fixer, arrayExpression, sourceCode),
			};
		},
		[uselessArrayCloneSelector](node) {
			const arrayExpression = node.parent.parent;
			const problem = {
				node: arrayExpression,
				messageId: CLONE_ARRAY,
			};

			if (
				// `[...new Array(1)]` -> `new Array(1)` is not safe to fix since there are holes
				isNewExpression(node, {name: 'Array'})
				// `[...foo.slice(1)]` -> `foo.slice(1)` is not safe to fix since `foo` can be a string
				|| (
					node.type === 'CallExpression'
					&& node.callee.type === 'MemberExpression'
					&& node.callee.property.type === 'Identifier'
					&& node.callee.property.name === 'slice'
				)
			) {
				return problem;
			}

			return Object.assign(problem, {
				fix: fixer => unwrapSingleArraySpread(fixer, arrayExpression, sourceCode),
			});
		},
	};
};

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Disallow unnecessary spread.',
		},
		fixable: 'code',
		messages,
	},
};
