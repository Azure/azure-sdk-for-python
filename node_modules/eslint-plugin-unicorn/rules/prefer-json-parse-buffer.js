'use strict';
const {findVariable, getStaticValue, getPropertyName} = require('@eslint-community/eslint-utils');
const {methodCallSelector} = require('./selectors/index.js');
const {removeArgument} = require('./fix/index.js');

const MESSAGE_ID = 'prefer-json-parse-buffer';
const messages = {
	[MESSAGE_ID]: 'Prefer reading the JSON file as a buffer.',
};

const jsonParseArgumentSelector = [
	methodCallSelector({
		object: 'JSON',
		method: 'parse',
		argumentsLength: 1,
	}),
	' > .arguments:first-child',
].join('');

const getAwaitExpressionArgument = node => {
	while (node.type === 'AwaitExpression') {
		node = node.argument;
	}

	return node;
};

function getIdentifierDeclaration(node, scope) {
	if (!node) {
		return;
	}

	node = getAwaitExpressionArgument(node);

	if (!node || node.type !== 'Identifier') {
		return node;
	}

	const variable = findVariable(scope, node);
	if (!variable) {
		return;
	}

	const {identifiers, references} = variable;

	if (identifiers.length !== 1 || references.length !== 2) {
		return;
	}

	const [identifier] = identifiers;

	if (
		identifier.parent.type !== 'VariableDeclarator'
		|| identifier.parent.id !== identifier
	) {
		return;
	}

	return getIdentifierDeclaration(identifier.parent.init, variable.scope);
}

const isUtf8EncodingStringNode = (node, scope) =>
	isUtf8EncodingString(getStaticValue(node, scope)?.value);

const isUtf8EncodingString = value => {
	if (typeof value !== 'string') {
		return false;
	}

	value = value.toLowerCase();

	// eslint-disable-next-line unicorn/text-encoding-identifier-case
	return value === 'utf8' || value === 'utf-8';
};

function isUtf8Encoding(node, scope) {
	if (
		node.type === 'ObjectExpression'
		&& node.properties.length === 1
		&& node.properties[0].type === 'Property'
		&& getPropertyName(node.properties[0], scope) === 'encoding'
		&& isUtf8EncodingStringNode(node.properties[0].value, scope)
	) {
		return true;
	}

	if (isUtf8EncodingStringNode(node, scope)) {
		return true;
	}

	const staticValue = getStaticValue(node, scope);
	if (!staticValue) {
		return false;
	}

	const {value} = staticValue;
	if (
		typeof value === 'object'
		&& Object.keys(value).length === 1
		&& isUtf8EncodingString(value.encoding)
	) {
		return true;
	}

	return false;
}

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => ({
	[jsonParseArgumentSelector](node) {
		const sourceCode = context.getSourceCode();
		const scope = sourceCode.getScope(node);
		node = getIdentifierDeclaration(node, scope);
		if (
			!(
				node
				&& node.type === 'CallExpression'
				&& !node.optional
				&& node.arguments.length === 2
				&& !node.arguments.some(node => node.type === 'SpreadElement')
				&& node.callee.type === 'MemberExpression'
				&& !node.callee.optional
			)
		) {
			return;
		}

		const method = getPropertyName(node.callee, scope);
		if (method !== 'readFile' && method !== 'readFileSync') {
			return;
		}

		const [, charsetNode] = node.arguments;
		if (!isUtf8Encoding(charsetNode, scope)) {
			return;
		}

		return {
			node: charsetNode,
			messageId: MESSAGE_ID,
			fix: fixer => removeArgument(fixer, charsetNode, sourceCode),
		};
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer reading a JSON file as a buffer.',
		},
		fixable: 'code',
		messages,
	},
};
