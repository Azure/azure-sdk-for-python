'use strict';
const {methodCallSelector, notDomNodeSelector} = require('./selectors/index.js');
const {isStringLiteral, isNullLiteral} = require('./ast/index.js');

const MESSAGE_ID = 'prefer-query-selector';
const messages = {
	[MESSAGE_ID]: 'Prefer `.{{replacement}}()` over `.{{method}}()`.',
};

const selector = [
	methodCallSelector({
		methods: ['getElementById', 'getElementsByClassName', 'getElementsByTagName'],
		argumentsLength: 1,
	}),
	notDomNodeSelector('callee.object'),
].join('');

const disallowedIdentifierNames = new Map([
	['getElementById', 'querySelector'],
	['getElementsByClassName', 'querySelectorAll'],
	['getElementsByTagName', 'querySelectorAll'],
]);

const getReplacementForId = value => `#${value}`;
const getReplacementForClass = value => value.match(/\S+/g).map(className => `.${className}`).join('');

const getQuotedReplacement = (node, value) => {
	const leftQuote = node.raw.charAt(0);
	const rightQuote = node.raw.charAt(node.raw.length - 1);
	return `${leftQuote}${value}${rightQuote}`;
};

function * getLiteralFix(fixer, node, identifierName) {
	let replacement = node.raw;
	if (identifierName === 'getElementById') {
		replacement = getQuotedReplacement(node, getReplacementForId(node.value));
	}

	if (identifierName === 'getElementsByClassName') {
		replacement = getQuotedReplacement(node, getReplacementForClass(node.value));
	}

	yield fixer.replaceText(node, replacement);
}

function * getTemplateLiteralFix(fixer, node, identifierName) {
	yield fixer.insertTextAfter(node, '`');
	yield fixer.insertTextBefore(node, '`');

	for (const templateElement of node.quasis) {
		if (identifierName === 'getElementById') {
			yield fixer.replaceText(
				templateElement,
				getReplacementForId(templateElement.value.cooked),
			);
		}

		if (identifierName === 'getElementsByClassName') {
			yield fixer.replaceText(
				templateElement,
				getReplacementForClass(templateElement.value.cooked),
			);
		}
	}
}

const canBeFixed = node =>
	isNullLiteral(node)
	|| (isStringLiteral(node) && Boolean(node.value.trim()))
	|| (
		node.type === 'TemplateLiteral'
		&& node.expressions.length === 0
		&& node.quasis.some(templateElement => templateElement.value.cooked.trim())
	);

const hasValue = node => {
	if (node.type === 'Literal') {
		return node.value;
	}

	return true;
};

const fix = (node, identifierName, preferredSelector) => {
	const nodeToBeFixed = node.arguments[0];
	if (identifierName === 'getElementsByTagName' || !hasValue(nodeToBeFixed)) {
		return fixer => fixer.replaceText(node.callee.property, preferredSelector);
	}

	const getArgumentFix = nodeToBeFixed.type === 'Literal' ? getLiteralFix : getTemplateLiteralFix;
	return function * (fixer) {
		yield * getArgumentFix(fixer, nodeToBeFixed, identifierName);
		yield fixer.replaceText(node.callee.property, preferredSelector);
	};
};

/** @param {import('eslint').Rule.RuleContext} context */
const create = () => ({
	[selector](node) {
		const method = node.callee.property.name;
		const preferredSelector = disallowedIdentifierNames.get(method);

		const problem = {
			node: node.callee.property,
			messageId: MESSAGE_ID,
			data: {
				replacement: preferredSelector,
				method,
			},
		};

		if (canBeFixed(node.arguments[0])) {
			problem.fix = fix(node, method, preferredSelector);
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
			description: 'Prefer `.querySelector()` over `.getElementById()`, `.querySelectorAll()` over `.getElementsByClassName()` and `.getElementsByTagName()`.',
		},
		fixable: 'code',
		messages,
	},
};
