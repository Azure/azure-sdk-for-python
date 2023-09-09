'use strict';
const {findVariable, getFunctionHeadLocation} = require('@eslint-community/eslint-utils');
const {matches, not, memberExpressionSelector} = require('./selectors/index.js');

const ERROR_PROMISE = 'promise';
const ERROR_IIFE = 'iife';
const ERROR_IDENTIFIER = 'identifier';
const SUGGESTION_ADD_AWAIT = 'add-await';
const messages = {
	[ERROR_PROMISE]: 'Prefer top-level await over using a promise chain.',
	[ERROR_IIFE]: 'Prefer top-level await over an async IIFE.',
	[ERROR_IDENTIFIER]: 'Prefer top-level await over an async function `{{name}}` call.',
	[SUGGESTION_ADD_AWAIT]: 'Insert `await`.',
};

const promiseMethods = ['then', 'catch', 'finally'];

const topLevelCallExpression = [
	'CallExpression',
	not([':function *', 'ClassDeclaration *', 'ClassExpression *']),
].join('');
const iife = [
	topLevelCallExpression,
	matches([
		'[callee.type="FunctionExpression"]',
		'[callee.type="ArrowFunctionExpression"]',
	]),
	'[callee.async!=false]',
	'[callee.generator!=true]',
].join('');
const promise = [
	topLevelCallExpression,
	memberExpressionSelector({
		path: 'callee',
		properties: promiseMethods,
		includeOptional: true,
	}),
].join('');
const identifier = [
	topLevelCallExpression,
	'[callee.type="Identifier"]',
].join('');

const isPromiseMethodCalleeObject = node =>
	node.parent.type === 'MemberExpression'
	&& node.parent.object === node
	&& !node.parent.computed
	&& node.parent.property.type === 'Identifier'
	&& promiseMethods.includes(node.parent.property.name)
	&& node.parent.parent.type === 'CallExpression'
	&& node.parent.parent.callee === node.parent;
const isAwaitArgument = node => {
	if (node.parent.type === 'ChainExpression') {
		node = node.parent;
	}

	return node.parent.type === 'AwaitExpression' && node.parent.argument === node;
};

/** @param {import('eslint').Rule.RuleContext} context */
function create(context) {
	if (context.getFilename().toLowerCase().endsWith('.cjs')) {
		return;
	}

	const sourceCode = context.getSourceCode();

	return {
		[promise](node) {
			if (isPromiseMethodCalleeObject(node) || isAwaitArgument(node)) {
				return;
			}

			return {
				node: node.callee.property,
				messageId: ERROR_PROMISE,
			};
		},
		[iife](node) {
			if (isPromiseMethodCalleeObject(node) || isAwaitArgument(node)) {
				return;
			}

			return {
				node,
				loc: getFunctionHeadLocation(node.callee, sourceCode),
				messageId: ERROR_IIFE,
			};
		},
		[identifier](node) {
			if (isPromiseMethodCalleeObject(node) || isAwaitArgument(node)) {
				return;
			}

			const variable = findVariable(sourceCode.getScope(node), node.callee);
			if (!variable || variable.defs.length !== 1) {
				return;
			}

			const [definition] = variable.defs;
			const value = definition.type === 'Variable' && definition.kind === 'const'
				? definition.node.init
				: definition.node;
			if (
				!value
				|| !(
					(
						value.type === 'ArrowFunctionExpression'
						|| value.type === 'FunctionExpression'
						|| value.type === 'FunctionDeclaration'
					) && !value.generator && value.async
				)
			) {
				return;
			}

			return {
				node,
				messageId: ERROR_IDENTIFIER,
				data: {name: node.callee.name},
				suggest: [
					{
						messageId: SUGGESTION_ADD_AWAIT,
						fix: fixer => fixer.insertTextBefore(node, 'await '),
					},
				],
			};
		},
	};
}

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer top-level await over top-level promises and async function calls.',
		},
		hasSuggestions: true,
		messages,
	},
};
