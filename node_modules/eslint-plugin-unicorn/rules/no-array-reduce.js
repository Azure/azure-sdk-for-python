'use strict';
const {methodCallSelector} = require('./selectors/index.js');
const {arrayPrototypeMethodSelector, notFunctionSelector} = require('./selectors/index.js');

const MESSAGE_ID = 'no-reduce';
const messages = {
	[MESSAGE_ID]: '`Array#{{method}}()` is not allowed',
};

const prototypeSelector = method => [
	methodCallSelector(method),
	arrayPrototypeMethodSelector({
		path: 'callee.object',
		methods: ['reduce', 'reduceRight'],
	}),
].join('');
const cases = [
	// `array.{reduce,reduceRight}()`
	{
		selector: [
			methodCallSelector({methods: ['reduce', 'reduceRight'], minimumArguments: 1, maximumArguments: 2}),
			notFunctionSelector('arguments.0'),
		].join(''),
		getMethodNode: callExpression => callExpression.callee.property,
		isSimpleOperation(callExpression) {
			const [callback] = callExpression.arguments;

			return (
				callback
				&& (
					// `array.reduce((accumulator, element) => accumulator + element)`
					(callback.type === 'ArrowFunctionExpression' && callback.body.type === 'BinaryExpression')
					// `array.reduce((accumulator, element) => {return accumulator + element;})`
					// `array.reduce(function (accumulator, element){return accumulator + element;})`
					|| (
						(callback.type === 'ArrowFunctionExpression' || callback.type === 'FunctionExpression')
						&& callback.body.type === 'BlockStatement'
						&& callback.body.body.length === 1
						&& callback.body.body[0].type === 'ReturnStatement'
						&& callback.body.body[0].argument.type === 'BinaryExpression'
					)
				)
			);
		},
	},
	// `[].{reduce,reduceRight}.call()` and `Array.{reduce,reduceRight}.call()`
	{
		selector: [
			prototypeSelector('call'),
			notFunctionSelector('arguments.1'),
		].join(''),
		getMethodNode: callExpression => callExpression.callee.object.property,
	},
	// `[].{reduce,reduceRight}.apply()` and `Array.{reduce,reduceRight}.apply()`
	{
		selector: prototypeSelector('apply'),
		getMethodNode: callExpression => callExpression.callee.object.property,
	},
];

const schema = [
	{
		type: 'object',
		additionalProperties: false,
		properties: {
			allowSimpleOperations: {
				type: 'boolean',
				default: true,
			},
		},
	},
];

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const {allowSimpleOperations} = {allowSimpleOperations: true, ...context.options[0]};
	const listeners = {};

	for (const {selector, getMethodNode, isSimpleOperation} of cases) {
		listeners[selector] = callExpression => {
			if (allowSimpleOperations && isSimpleOperation?.(callExpression)) {
				return;
			}

			const methodNode = getMethodNode(callExpression);
			return {
				node: methodNode,
				messageId: MESSAGE_ID,
				data: {method: methodNode.name},
			};
		};
	}

	return listeners;
};

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Disallow `Array#reduce()` and `Array#reduceRight()`.',
		},
		schema,
		messages,
	},
};
