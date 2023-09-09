'use strict';
const {methodCallSelector, matches, memberExpressionSelector} = require('./selectors/index.js');
const isSameReference = require('./utils/is-same-reference.js');
const {getParenthesizedRange} = require('./utils/parentheses.js');

const messages = {
	'non-zero': 'The non-empty check is useless as `Array#some()` returns `false` for an empty array.',
	zero: 'The empty check is useless as `Array#every()` returns `true` for an empty array.',
};

const logicalExpressionSelector = [
	'LogicalExpression',
	matches(['[operator="||"]', '[operator="&&"]']),
].join('');
// We assume the user already follows `unicorn/explicit-length-check`. These are allowed in that rule.
const lengthCompareZeroSelector = [
	logicalExpressionSelector,
	' > ',
	'BinaryExpression',
	memberExpressionSelector({path: 'left', property: 'length'}),
	'[right.type="Literal"]',
	'[right.raw="0"]',
].join('');
const zeroLengthCheckSelector = [
	lengthCompareZeroSelector,
	'[operator="==="]',
].join('');
const nonZeroLengthCheckSelector = [
	lengthCompareZeroSelector,
	matches(['[operator=">"]', '[operator="!=="]']),
].join('');
const arraySomeCallSelector = methodCallSelector('some');
const arrayEveryCallSelector = methodCallSelector('every');

function flatLogicalExpression(node) {
	return [node.left, node.right].flatMap(child =>
		child.type === 'LogicalExpression' && child.operator === node.operator
			? flatLogicalExpression(child)
			: [child],
	);
}

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const logicalExpressions = [];
	const zeroLengthChecks = new Set();
	const nonZeroLengthChecks = new Set();
	const arraySomeCalls = new Set();
	const arrayEveryCalls = new Set();

	function isUselessLengthCheckNode({node, operator, siblings}) {
		return (
			(
				operator === '||'
				&& zeroLengthChecks.has(node)
				&& siblings.some(condition =>
					arrayEveryCalls.has(condition)
					&& isSameReference(node.left.object, condition.callee.object),
				)
			)
			|| (
				operator === '&&'
				&& nonZeroLengthChecks.has(node)
				&& siblings.some(condition =>
					arraySomeCalls.has(condition)
					&& isSameReference(node.left.object, condition.callee.object),
				)
			)
		);
	}

	function getUselessLengthCheckNode(logicalExpression) {
		const {operator} = logicalExpression;
		return flatLogicalExpression(logicalExpression)
			.filter((node, index, conditions) => isUselessLengthCheckNode({
				node,
				operator,
				siblings: [
					conditions[index - 1],
					conditions[index + 1],
				].filter(Boolean),
			}));
	}

	return {
		[zeroLengthCheckSelector](node) {
			zeroLengthChecks.add(node);
		},
		[nonZeroLengthCheckSelector](node) {
			nonZeroLengthChecks.add(node);
		},
		[arraySomeCallSelector](node) {
			arraySomeCalls.add(node);
		},
		[arrayEveryCallSelector](node) {
			arrayEveryCalls.add(node);
		},
		[logicalExpressionSelector](node) {
			logicalExpressions.push(node);
		},
		* 'Program:exit'() {
			const nodes = new Set(
				logicalExpressions.flatMap(logicalExpression =>
					getUselessLengthCheckNode(logicalExpression),
				),
			);

			for (const node of nodes) {
				yield {
					loc: {
						start: node.left.property.loc.start,
						end: node.loc.end,
					},
					messageId: zeroLengthChecks.has(node) ? 'zero' : 'non-zero',
					/** @param {import('eslint').Rule.RuleFixer} fixer */
					fix(fixer) {
						const sourceCode = context.getSourceCode();
						const {left, right} = node.parent;
						const leftRange = getParenthesizedRange(left, sourceCode);
						const rightRange = getParenthesizedRange(right, sourceCode);
						const range = [];
						if (left === node) {
							range[0] = leftRange[0];
							range[1] = rightRange[0];
						} else {
							range[0] = leftRange[1];
							range[1] = rightRange[1];
						}

						return fixer.removeRange(range);
					},
				};
			}
		},
	};
};

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Disallow useless array length check.',
		},
		fixable: 'code',
		messages,
	},
};
