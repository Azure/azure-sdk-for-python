'use strict';
const {getParenthesizedText} = require('./utils/parentheses.js');

const MESSAGE_ID = 'prefer-modern-math-apis';
const messages = {
	[MESSAGE_ID]: 'Prefer `{{replacement}}` over `{{description}}`.',
};

const isMathProperty = (node, property) =>
	node.type === 'MemberExpression'
	&& !node.optional
	&& !node.computed
	&& node.object.type === 'Identifier'
	&& node.object.name === 'Math'
	&& node.property.type === 'Identifier'
	&& node.property.name === property;

const isMathMethodCall = (node, method) =>
	node.type === 'CallExpression'
	&& !node.optional
	&& isMathProperty(node.callee, method)
	&& node.arguments.length === 1
	&& node.arguments[0].type !== 'SpreadElement';

// `Math.log(x) * Math.LOG10E` -> `Math.log10(x)`
// `Math.LOG10E * Math.log(x)` -> `Math.log10(x)`
// `Math.log(x) * Math.LOG2E` -> `Math.log2(x)`
// `Math.LOG2E * Math.log(x)` -> `Math.log2(x)`
function createLogCallTimesConstantCheck({constantName, replacementMethod}) {
	const replacement = `Math.${replacementMethod}(…)`;

	return function (node, context) {
		if (!(node.type === 'BinaryExpression' && node.operator === '*')) {
			return;
		}

		let mathLogCall;
		let description;
		if (isMathMethodCall(node.left, 'log') && isMathProperty(node.right, constantName)) {
			mathLogCall = node.left;
			description = `Math.log(…) * Math.${constantName}`;
		} else if (isMathMethodCall(node.right, 'log') && isMathProperty(node.left, constantName)) {
			mathLogCall = node.right;
			description = `Math.${constantName} * Math.log(…)`;
		}

		if (!mathLogCall) {
			return;
		}

		const [valueNode] = mathLogCall.arguments;

		return {
			node,
			messageId: MESSAGE_ID,
			data: {
				replacement,
				description,
			},
			fix: fixer => fixer.replaceText(node, `Math.${replacementMethod}(${getParenthesizedText(valueNode, context.getSourceCode())})`),
		};
	};
}

// `Math.log(x) / Math.LN10` -> `Math.log10(x)`
// `Math.log(x) / Math.LN2` -> `Math.log2(x)`
function createLogCallDivideConstantCheck({constantName, replacementMethod}) {
	const message = {
		messageId: MESSAGE_ID,
		data: {
			replacement: `Math.${replacementMethod}(…)`,
			description: `Math.log(…) / Math.${constantName}`,
		},
	};

	return function (node, context) {
		if (
			!(
				node.type === 'BinaryExpression'
				&& node.operator === '/'
				&& isMathMethodCall(node.left, 'log')
				&& isMathProperty(node.right, constantName)
			)
		) {
			return;
		}

		const [valueNode] = node.left.arguments;

		return {
			...message,
			node,
			fix: fixer => fixer.replaceText(node, `Math.${replacementMethod}(${getParenthesizedText(valueNode, context.getSourceCode())})`),
		};
	};
}

const checkFunctions = [
	createLogCallTimesConstantCheck({constantName: 'LOG10E', replacementMethod: 'log10'}),
	createLogCallTimesConstantCheck({constantName: 'LOG2E', replacementMethod: 'log2'}),
	createLogCallDivideConstantCheck({constantName: 'LN10', replacementMethod: 'log10'}),
	createLogCallDivideConstantCheck({constantName: 'LN2', replacementMethod: 'log2'}),
];

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const nodes = [];

	return {
		BinaryExpression(node) {
			nodes.push(node);
		},
		* 'Program:exit'() {
			for (const node of nodes) {
				for (const getProblem of checkFunctions) {
					const problem = getProblem(node, context);

					if (problem) {
						yield problem;
					}
				}
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
			description: 'Prefer modern `Math` APIs over legacy patterns.',
		},
		fixable: 'code',
		messages,
	},
};
