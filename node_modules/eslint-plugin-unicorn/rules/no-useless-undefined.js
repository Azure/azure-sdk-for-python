'use strict';
const {isCommaToken} = require('@eslint-community/eslint-utils');
const {replaceNodeOrTokenAndSpacesBefore} = require('./fix/index.js');
const {isUndefined} = require('./ast/index.js');

const messageId = 'no-useless-undefined';
const messages = {
	[messageId]: 'Do not use useless `undefined`.',
};

const getSelector = (parent, property) =>
	`${parent} > Identifier.${property}[name="undefined"]`;

// `return undefined`
const returnSelector = getSelector('ReturnStatement', 'argument');

// `yield undefined`
const yieldSelector = getSelector('YieldExpression[delegate!=true]', 'argument');

// `() => undefined`
const arrowFunctionSelector = getSelector('ArrowFunctionExpression', 'body');

// `let foo = undefined` / `var foo = undefined`
const variableInitSelector = getSelector(
	[
		'VariableDeclaration',
		'[kind!="const"]',
		'>',
		'VariableDeclarator',
	].join(''),
	'init',
);

// `const {foo = undefined} = {}`
const assignmentPatternSelector = getSelector('AssignmentPattern', 'right');

const compareFunctionNames = new Set([
	'is',
	'equal',
	'notEqual',
	'strictEqual',
	'notStrictEqual',
	'propertyVal',
	'notPropertyVal',
	'not',
	'include',
	'property',
	'toBe',
	'toHaveBeenCalledWith',
	'toContain',
	'toContainEqual',
	'toEqual',
	'same',
	'notSame',
	'strictSame',
	'strictNotSame',
]);
const shouldIgnore = node => {
	let name;

	if (node.type === 'Identifier') {
		name = node.name;
	} else if (
		node.type === 'MemberExpression'
		&& node.computed === false
		&& node.property.type === 'Identifier'
	) {
		name = node.property.name;
	}

	return compareFunctionNames.has(name)
		// `array.push(undefined)`
		|| name === 'push'
		// `array.unshift(undefined)`
		|| name === 'unshift'
		// `array.includes(undefined)`
		|| name === 'includes'

		// `set.add(undefined)`
		|| name === 'add'
		// `set.has(undefined)`
		|| name === 'has'

		// `map.set(foo, undefined)`
		|| name === 'set'

		// `React.createContext(undefined)`
		|| name === 'createContext'

		// https://vuejs.org/api/reactivity-core.html#ref
		|| name === 'ref';
};

const getFunction = scope => {
	for (; scope; scope = scope.upper) {
		if (scope.type === 'function') {
			return scope.block;
		}
	}
};

const isFunctionBindCall = node =>
	!node.optional
	&& node.callee.type === 'MemberExpression'
	&& !node.callee.computed
	&& node.callee.property.type === 'Identifier'
	&& node.callee.property.name === 'bind';

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const sourceCode = context.getSourceCode();

	const listener = (fix, checkFunctionReturnType) => node => {
		if (checkFunctionReturnType) {
			const functionNode = getFunction(sourceCode.getScope(node));
			if (functionNode?.returnType) {
				return;
			}
		}

		return {
			node,
			messageId,
			fix: fixer => fix(node, fixer),
		};
	};

	const options = {
		checkArguments: true,
		...context.options[0],
	};

	const removeNodeAndLeadingSpace = (node, fixer) =>
		replaceNodeOrTokenAndSpacesBefore(node, '', fixer, sourceCode);

	const listeners = {
		[returnSelector]: listener(
			removeNodeAndLeadingSpace,
			/* CheckFunctionReturnType */ true,
		),
		[yieldSelector]: listener(removeNodeAndLeadingSpace),
		[arrowFunctionSelector]: listener(
			(node, fixer) => replaceNodeOrTokenAndSpacesBefore(node, ' {}', fixer, sourceCode),
			/* CheckFunctionReturnType */ true,
		),
		[variableInitSelector]: listener(
			(node, fixer) => fixer.removeRange([node.parent.id.range[1], node.range[1]]),
		),
		[assignmentPatternSelector]: listener(
			(node, fixer) => fixer.removeRange([node.parent.left.range[1], node.range[1]]),
		),
	};

	if (options.checkArguments) {
		listeners.CallExpression = node => {
			if (shouldIgnore(node.callee)) {
				return;
			}

			const argumentNodes = node.arguments;

			// Ignore arguments in `Function#bind()`, but not `this` argument
			if (isFunctionBindCall(node) && argumentNodes.length !== 1) {
				return;
			}

			const undefinedArguments = [];
			for (let index = argumentNodes.length - 1; index >= 0; index--) {
				const node = argumentNodes[index];
				if (isUndefined(node)) {
					undefinedArguments.unshift(node);
				} else {
					break;
				}
			}

			if (undefinedArguments.length === 0) {
				return;
			}

			const firstUndefined = undefinedArguments[0];
			const lastUndefined = undefinedArguments[undefinedArguments.length - 1];

			return {
				messageId,
				loc: {
					start: firstUndefined.loc.start,
					end: lastUndefined.loc.end,
				},
				fix(fixer) {
					let start = firstUndefined.range[0];
					let end = lastUndefined.range[1];

					const previousArgument = argumentNodes[argumentNodes.length - undefinedArguments.length - 1];

					if (previousArgument) {
						start = previousArgument.range[1];
					} else {
						// If all arguments removed, and there is trailing comma, we need remove it.
						const tokenAfter = sourceCode.getTokenAfter(lastUndefined);
						if (isCommaToken(tokenAfter)) {
							end = tokenAfter.range[1];
						}
					}

					return fixer.removeRange([start, end]);
				},
			};
		};
	}

	return listeners;
};

const schema = [
	{
		type: 'object',
		additionalProperties: false,
		properties: {
			checkArguments: {
				type: 'boolean',
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
			description: 'Disallow useless `undefined`.',
		},
		fixable: 'code',
		schema,
		messages,
	},
};
