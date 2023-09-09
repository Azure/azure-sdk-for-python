'use strict';
const {
	matches,
	methodCallSelector,
	newExpressionSelector,
	callExpressionSelector,
} = require('./selectors/index.js');
const {fixSpaceAroundKeyword} = require('./fix/index.js');

const MESSAGE_ID_DEFAULT = 'prefer-date';
const MESSAGE_ID_METHOD = 'prefer-date-now-over-methods';
const MESSAGE_ID_NUMBER = 'prefer-date-now-over-number-data-object';
const messages = {
	[MESSAGE_ID_DEFAULT]: 'Prefer `Date.now()` over `new Date()`.',
	[MESSAGE_ID_METHOD]: 'Prefer `Date.now()` over `Date#{{method}}()`.',
	[MESSAGE_ID_NUMBER]: 'Prefer `Date.now()` over `Number(new Date())`.',
};

const createNewDateSelector = path => newExpressionSelector({path, name: 'Date', argumentsLength: 0});
const operatorsSelector = (...operators) => matches(operators.map(operator => `[operator="${operator}"]`));
// `new Date()`
const newDateSelector = createNewDateSelector();
// `new Date().{getTime,valueOf}()`
const methodsSelector = [
	methodCallSelector({
		methods: ['getTime', 'valueOf'],
		argumentsLength: 0,
	}),
	createNewDateSelector('callee.object'),
].join('');
// `{Number,BigInt}(new Date())`
const builtinObjectSelector = [
	callExpressionSelector({names: ['Number', 'BigInt'], argumentsLength: 1}),
	createNewDateSelector('arguments.0'),
].join('');
// https://github.com/estree/estree/blob/master/es5.md#unaryoperator
const unaryExpressionsSelector = [
	'UnaryExpression',
	operatorsSelector('+', '-'),
	createNewDateSelector('argument'),
].join('');
const assignmentExpressionSelector = [
	'AssignmentExpression',
	operatorsSelector('-=', '*=', '/=', '%=', '**='),
	'>',
	`${newDateSelector}.right`,
].join('');
const binaryExpressionSelector = [
	'BinaryExpression',
	operatorsSelector('-', '*', '/', '%', '**'),
	// Both `left` and `right` properties
	'>',
	newDateSelector,
].join('');

const getProblem = (node, problem, sourceCode) => ({
	node,
	messageId: MESSAGE_ID_DEFAULT,
	* fix(fixer) {
		yield fixer.replaceText(node, 'Date.now()');

		if (node.type === 'UnaryExpression') {
			yield * fixSpaceAroundKeyword(fixer, node, sourceCode);
		}
	},
	...problem,
});

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => ({
	[methodsSelector](node) {
		const method = node.callee.property;
		return getProblem(node, {
			node: method,
			messageId: MESSAGE_ID_METHOD,
			data: {method: method.name},
		});
	},
	[builtinObjectSelector](node) {
		const {name} = node.callee;
		if (name === 'Number') {
			return getProblem(node, {
				messageId: MESSAGE_ID_NUMBER,
			});
		}

		return getProblem(node.arguments[0]);
	},
	[unaryExpressionsSelector](node) {
		return getProblem(
			node.operator === '-' ? node.argument : node,
			{},
			context.getSourceCode(),
		);
	},
	[assignmentExpressionSelector](node) {
		return getProblem(node);
	},
	[binaryExpressionSelector](node) {
		return getProblem(node);
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer `Date.now()` to get the number of milliseconds since the Unix Epoch.',
		},
		fixable: 'code',
		messages,
	},
};
