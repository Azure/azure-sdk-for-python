'use strict';
const {isParenthesized, getStaticValue} = require('@eslint-community/eslint-utils');
const {checkVueTemplate} = require('./utils/rule.js');
const isLogicalExpression = require('./utils/is-logical-expression.js');
const {isBooleanNode, getBooleanAncestor} = require('./utils/boolean.js');
const {memberExpressionSelector} = require('./selectors/index.js');
const {fixSpaceAroundKeyword} = require('./fix/index.js');
const {isLiteral} = require('./ast/index.js');

const TYPE_NON_ZERO = 'non-zero';
const TYPE_ZERO = 'zero';
const MESSAGE_ID_SUGGESTION = 'suggestion';
const messages = {
	[TYPE_NON_ZERO]: 'Use `.{{property}} {{code}}` when checking {{property}} is not zero.',
	[TYPE_ZERO]: 'Use `.{{property}} {{code}}` when checking {{property}} is zero.',
	[MESSAGE_ID_SUGGESTION]: 'Replace `.{{property}}` with `.{{property}} {{code}}`.',
};

const isCompareRight = (node, operator, value) =>
	node.type === 'BinaryExpression'
	&& node.operator === operator
	&& isLiteral(node.right, value);
const isCompareLeft = (node, operator, value) =>
	node.type === 'BinaryExpression'
	&& node.operator === operator
	&& isLiteral(node.left, value);
const nonZeroStyles = new Map([
	[
		'greater-than',
		{
			code: '> 0',
			test: node => isCompareRight(node, '>', 0),
		},
	],
	[
		'not-equal',
		{
			code: '!== 0',
			test: node => isCompareRight(node, '!==', 0),
		},
	],
]);
const zeroStyle = {
	code: '=== 0',
	test: node => isCompareRight(node, '===', 0),
};

const lengthSelector = memberExpressionSelector(['length', 'size']);

function getLengthCheckNode(node) {
	node = node.parent;

	// Zero length check
	if (
		// `foo.length === 0`
		isCompareRight(node, '===', 0)
		// `foo.length == 0`
		|| isCompareRight(node, '==', 0)
		// `foo.length < 1`
		|| isCompareRight(node, '<', 1)
		// `0 === foo.length`
		|| isCompareLeft(node, '===', 0)
		// `0 == foo.length`
		|| isCompareLeft(node, '==', 0)
		// `1 > foo.length`
		|| isCompareLeft(node, '>', 1)
	) {
		return {isZeroLengthCheck: true, node};
	}

	// Non-Zero length check
	if (
		// `foo.length !== 0`
		isCompareRight(node, '!==', 0)
		// `foo.length != 0`
		|| isCompareRight(node, '!=', 0)
		// `foo.length > 0`
		|| isCompareRight(node, '>', 0)
		// `foo.length >= 1`
		|| isCompareRight(node, '>=', 1)
		// `0 !== foo.length`
		|| isCompareLeft(node, '!==', 0)
		// `0 !== foo.length`
		|| isCompareLeft(node, '!=', 0)
		// `0 < foo.length`
		|| isCompareLeft(node, '<', 0)
		// `1 <= foo.length`
		|| isCompareLeft(node, '<=', 1)
	) {
		return {isZeroLengthCheck: false, node};
	}

	return {};
}

function create(context) {
	const options = {
		'non-zero': 'greater-than',
		...context.options[0],
	};
	const nonZeroStyle = nonZeroStyles.get(options['non-zero']);
	const sourceCode = context.getSourceCode();

	function getProblem({node, isZeroLengthCheck, lengthNode, autoFix}) {
		const {code, test} = isZeroLengthCheck ? zeroStyle : nonZeroStyle;
		if (test(node)) {
			return;
		}

		let fixed = `${sourceCode.getText(lengthNode)} ${code}`;
		if (
			!isParenthesized(node, sourceCode)
			&& node.type === 'UnaryExpression'
			&& (node.parent.type === 'UnaryExpression' || node.parent.type === 'AwaitExpression')
		) {
			fixed = `(${fixed})`;
		}

		const fix = function * (fixer) {
			yield fixer.replaceText(node, fixed);
			yield * fixSpaceAroundKeyword(fixer, node, sourceCode);
		};

		const problem = {
			node,
			messageId: isZeroLengthCheck ? TYPE_ZERO : TYPE_NON_ZERO,
			data: {code, property: lengthNode.property.name},
		};

		if (autoFix) {
			problem.fix = fix;
		} else {
			problem.suggest = [
				{
					messageId: MESSAGE_ID_SUGGESTION,
					fix,
				},
			];
		}

		return problem;
	}

	return {
		[lengthSelector](lengthNode) {
			if (lengthNode.object.type === 'ThisExpression') {
				return;
			}

			const staticValue = getStaticValue(lengthNode, sourceCode.getScope(lengthNode));
			if (staticValue && (!Number.isInteger(staticValue.value) || staticValue.value < 0)) {
				// Ignore known, non-positive-integer length properties.
				return;
			}

			let node;
			let autoFix = true;
			let {isZeroLengthCheck, node: lengthCheckNode} = getLengthCheckNode(lengthNode);
			if (lengthCheckNode) {
				const {isNegative, node: ancestor} = getBooleanAncestor(lengthCheckNode);
				node = ancestor;
				if (isNegative) {
					isZeroLengthCheck = !isZeroLengthCheck;
				}
			} else {
				const {isNegative, node: ancestor} = getBooleanAncestor(lengthNode);
				if (isBooleanNode(ancestor)) {
					isZeroLengthCheck = isNegative;
					node = ancestor;
				} else if (isLogicalExpression(lengthNode.parent)) {
					isZeroLengthCheck = isNegative;
					node = lengthNode;
					autoFix = false;
				}
			}

			if (node) {
				return getProblem({node, isZeroLengthCheck, lengthNode, autoFix});
			}
		},
	};
}

const schema = [
	{
		type: 'object',
		additionalProperties: false,
		properties: {
			'non-zero': {
				enum: [...nonZeroStyles.keys()],
				default: 'greater-than',
			},
		},
	},
];

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create: checkVueTemplate(create),
	meta: {
		type: 'problem',
		docs: {
			description: 'Enforce explicitly comparing the `length` or `size` property of a value.',
		},
		fixable: 'code',
		schema,
		messages,
		hasSuggestions: true,
	},
};
