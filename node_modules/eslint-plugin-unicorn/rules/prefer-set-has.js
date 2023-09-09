'use strict';
const {findVariable} = require('@eslint-community/eslint-utils');
const getVariableIdentifiers = require('./utils/get-variable-identifiers.js');
const {
	matches,
	not,
	methodCallSelector,
	callOrNewExpressionSelector,
} = require('./selectors/index.js');

const MESSAGE_ID_ERROR = 'error';
const MESSAGE_ID_SUGGESTION = 'suggestion';
const messages = {
	[MESSAGE_ID_ERROR]: '`{{name}}` should be a `Set`, and use `{{name}}.has()` to check existence or non-existence.',
	[MESSAGE_ID_SUGGESTION]: 'Switch `{{name}}` to `Set`.',
};

// `[]`
const arrayExpressionSelector = [
	'[init.type="ArrayExpression"]',
].join('');

// `Array()` and `new Array()`
const newArraySelector = callOrNewExpressionSelector({name: 'Array', path: 'init'});

// `Array.from()` and `Array.of()`
const arrayStaticMethodSelector = methodCallSelector({
	object: 'Array',
	methods: ['from', 'of'],
	path: 'init',
});

// Array methods that return an array
const arrayMethodSelector = methodCallSelector({
	methods: [
		'concat',
		'copyWithin',
		'fill',
		'filter',
		'flat',
		'flatMap',
		'map',
		'reverse',
		'slice',
		'sort',
		'splice',
		'toReversed',
		'toSorted',
		'toSpliced',
		'with',
	],
	path: 'init',
});

const selector = [
	'VariableDeclaration',
	// Exclude `export const foo = [];`
	not('ExportNamedDeclaration > .declaration'),
	' > ',
	'VariableDeclarator.declarations',
	matches([
		arrayExpressionSelector,
		newArraySelector,
		arrayStaticMethodSelector,
		arrayMethodSelector,
	]),
	' > ',
	'Identifier.id',
].join('');

const isIncludesCall = node => {
	const {type, optional, callee, arguments: includesArguments} = node.parent.parent ?? {};
	return (
		type === 'CallExpression'
		&& !optional
		&& callee.type === 'MemberExpression'
		&& !callee.computed
		&& !callee.optional
		&& callee.object === node
		&& callee.property.type === 'Identifier'
		&& callee.property.name === 'includes'
		&& includesArguments.length === 1
		&& includesArguments[0].type !== 'SpreadElement'
	);
};

const multipleCallNodeTypes = new Set([
	'ForOfStatement',
	'ForStatement',
	'ForInStatement',
	'WhileStatement',
	'DoWhileStatement',
	'FunctionDeclaration',
	'FunctionExpression',
	'ArrowFunctionExpression',
]);

const isMultipleCall = (identifier, node) => {
	const root = node.parent.parent.parent;
	let {parent} = identifier.parent; // `.include()` callExpression
	while (
		parent
		&& parent !== root
	) {
		if (multipleCallNodeTypes.has(parent.type)) {
			return true;
		}

		parent = parent.parent;
	}

	return false;
};

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => ({
	[selector](node) {
		const variable = findVariable(context.getSourceCode().getScope(node), node);

		// This was reported https://github.com/sindresorhus/eslint-plugin-unicorn/issues/1075#issuecomment-768073342
		// But can't reproduce, just ignore this case
		/* c8 ignore next 3 */
		if (!variable) {
			return;
		}

		const identifiers = getVariableIdentifiers(variable).filter(identifier => identifier !== node);

		if (
			identifiers.length === 0
			|| identifiers.some(identifier => !isIncludesCall(identifier))
		) {
			return;
		}

		if (
			identifiers.length === 1
			&& identifiers.every(identifier => !isMultipleCall(identifier, node))
		) {
			return;
		}

		const problem = {
			node,
			messageId: MESSAGE_ID_ERROR,
			data: {
				name: node.name,
			},
		};

		const fix = function * (fixer) {
			yield fixer.insertTextBefore(node.parent.init, 'new Set(');
			yield fixer.insertTextAfter(node.parent.init, ')');

			for (const identifier of identifiers) {
				yield fixer.replaceText(identifier.parent.property, 'has');
			}
		};

		if (node.typeAnnotation) {
			problem.suggest = [
				{
					messageId: MESSAGE_ID_SUGGESTION,
					fix,
				},
			];
		} else {
			problem.fix = fix;
		}

		return problem;
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer `Set#has()` over `Array#includes()` when checking for existence or non-existence.',
		},
		fixable: 'code',
		hasSuggestions: true,
		messages,
	},
};
