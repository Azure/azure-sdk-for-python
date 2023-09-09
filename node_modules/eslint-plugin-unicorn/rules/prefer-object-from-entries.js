'use strict';
const {isCommaToken, isArrowToken, isClosingParenToken} = require('@eslint-community/eslint-utils');
const getDocumentationUrl = require('./utils/get-documentation-url.js');
const {matches, methodCallSelector} = require('./selectors/index.js');
const {removeParentheses} = require('./fix/index.js');
const {getParentheses, getParenthesizedText} = require('./utils/parentheses.js');
const {isNodeMatches, isNodeMatchesNameOrPath} = require('./utils/is-node-matches.js');

const MESSAGE_ID_REDUCE = 'reduce';
const MESSAGE_ID_FUNCTION = 'function';
const messages = {
	[MESSAGE_ID_REDUCE]: 'Prefer `Object.fromEntries()` over `Array#reduce()`.',
	[MESSAGE_ID_FUNCTION]: 'Prefer `Object.fromEntries()` over `{{functionName}}()`.',
};

const createEmptyObjectSelector = path => {
	const prefix = path ? `${path}.` : '';
	return matches([
		// `{}`
		`[${prefix}type="ObjectExpression"][${prefix}properties.length=0]`,
		// `Object.create(null)`
		[
			methodCallSelector({path, object: 'Object', method: 'create', argumentsLength: 1}),
			`[${prefix}arguments.0.type="Literal"]`,
			`[${prefix}arguments.0.raw="null"]`,
		].join(''),
	]);
};

const createArrowCallbackSelector = path => {
	const prefix = path ? `${path}.` : '';
	return [
		`[${prefix}type="ArrowFunctionExpression"]`,
		`[${prefix}async!=true]`,
		`[${prefix}generator!=true]`,
		`[${prefix}params.length>=1]`,
		`[${prefix}params.0.type="Identifier"]`,
	].join('');
};

const createPropertySelector = path => {
	const prefix = path ? `${path}.` : '';
	return [
		`[${prefix}type="Property"]`,
		`[${prefix}kind="init"]`,
		`[${prefix}method!=true]`,
	].join('');
};

// - `pairs.reduce(…, {})`
// - `pairs.reduce(…, Object.create(null))`
const arrayReduceWithEmptyObject = [
	methodCallSelector({method: 'reduce', argumentsLength: 2}),
	createEmptyObjectSelector('arguments.1'),
].join('');

const fixableArrayReduceCases = [
	{
		selector: [
			arrayReduceWithEmptyObject,
			// () => Object.assign(object, {key})
			createArrowCallbackSelector('arguments.0'),
			methodCallSelector({path: 'arguments.0.body', object: 'Object', method: 'assign', argumentsLength: 2}),
			'[arguments.0.body.arguments.0.type="Identifier"]',
			'[arguments.0.body.arguments.1.type="ObjectExpression"]',
			'[arguments.0.body.arguments.1.properties.length=1]',
			createPropertySelector('arguments.0.body.arguments.1.properties.0'),
		].join(''),
		test: callback => callback.params[0].name === callback.body.arguments[0].name,
		getProperty: callback => callback.body.arguments[1].properties[0],
	},
	{
		selector: [
			arrayReduceWithEmptyObject,
			// () => ({...object, key})
			createArrowCallbackSelector('arguments.0'),
			'[arguments.0.body.type="ObjectExpression"]',
			'[arguments.0.body.properties.length=2]',
			'[arguments.0.body.properties.0.type="SpreadElement"]',
			'[arguments.0.body.properties.0.argument.type="Identifier"]',
			createPropertySelector('arguments.0.body.properties.1'),
		].join(''),
		test: callback => callback.params[0].name === callback.body.properties[0].argument.name,
		getProperty: callback => callback.body.properties[1],
	},
];

// `_.flatten(array)`
const lodashFromPairsFunctions = [
	'_.fromPairs',
	'lodash.fromPairs',
];
const anyCall = [
	'CallExpression',
	'[optional!=true]',
	'[arguments.length=1]',
	'[arguments.0.type!="SpreadElement"]',
	' > .callee',
].join('');

function fixReduceAssignOrSpread({sourceCode, node, property}) {
	const removeInitObject = fixer => {
		const initObject = node.arguments[1];
		const parentheses = getParentheses(initObject, sourceCode);
		const firstToken = parentheses[0] || initObject;
		const lastToken = parentheses[parentheses.length - 1] || initObject;
		const startToken = sourceCode.getTokenBefore(firstToken);
		const [start] = startToken.range;
		const [, end] = lastToken.range;
		return fixer.replaceTextRange([start, end], '');
	};

	function * removeFirstParameter(fixer) {
		const parameters = node.arguments[0].params;
		const [firstParameter] = parameters;
		const tokenAfter = sourceCode.getTokenAfter(firstParameter);

		if (isCommaToken(tokenAfter)) {
			yield fixer.remove(tokenAfter);
		}

		let shouldAddParentheses = false;
		if (parameters.length === 1) {
			const arrowToken = sourceCode.getTokenAfter(firstParameter, isArrowToken);
			const tokenBeforeArrowToken = sourceCode.getTokenBefore(arrowToken);

			if (!isClosingParenToken(tokenBeforeArrowToken)) {
				shouldAddParentheses = true;
			}
		}

		yield fixer.replaceText(firstParameter, shouldAddParentheses ? '()' : '');
	}

	const getKeyValueText = () => {
		const {key, value} = property;
		let keyText = getParenthesizedText(key, sourceCode);
		const valueText = getParenthesizedText(value, sourceCode);

		if (!property.computed && key.type === 'Identifier') {
			keyText = `'${keyText}'`;
		}

		return {keyText, valueText};
	};

	function * replaceFunctionBody(fixer) {
		const functionBody = node.arguments[0].body;
		const {keyText, valueText} = getKeyValueText();
		yield fixer.replaceText(functionBody, `[${keyText}, ${valueText}]`);
		yield * removeParentheses(functionBody, fixer, sourceCode);
	}

	return function * (fixer) {
		// Wrap `array.reduce()` with `Object.fromEntries()`
		yield fixer.insertTextBefore(node, 'Object.fromEntries(');
		yield fixer.insertTextAfter(node, ')');

		// Switch `.reduce` to `.map`
		yield fixer.replaceText(node.callee.property, 'map');

		// Remove empty object
		yield removeInitObject(fixer);

		// Remove the first parameter
		yield * removeFirstParameter(fixer);

		// Replace function body
		yield * replaceFunctionBody(fixer);
	};
}

/** @param {import('eslint').Rule.RuleContext} context */
function create(context) {
	const {functions: configFunctions} = {
		functions: [],
		...context.options[0],
	};
	const functions = [...configFunctions, ...lodashFromPairsFunctions];
	const sourceCode = context.getSourceCode();
	const listeners = {};
	const arrayReduce = new Map();

	for (const {selector, test, getProperty} of fixableArrayReduceCases) {
		listeners[selector] = node => {
			const [callbackFunction] = node.arguments;
			if (!test(callbackFunction)) {
				return;
			}

			const [firstParameter] = callbackFunction.params;
			const variables = sourceCode.getDeclaredVariables(callbackFunction);
			const firstParameterVariable = variables.find(variable => variable.identifiers.length === 1 && variable.identifiers[0] === firstParameter);
			if (!firstParameterVariable || firstParameterVariable.references.length !== 1) {
				return;
			}

			arrayReduce.set(
				node,
				// The fix function
				fixReduceAssignOrSpread({
					sourceCode,
					node,
					property: getProperty(callbackFunction),
				}),
			);
		};
	}

	listeners['Program:exit'] = () => {
		for (const [node, fix] of arrayReduce.entries()) {
			context.report({
				node: node.callee.property,
				messageId: MESSAGE_ID_REDUCE,
				fix,
			});
		}
	};

	listeners[anyCall] = node => {
		if (!isNodeMatches(node, functions)) {
			return;
		}

		const functionName = functions.find(nameOrPath => isNodeMatchesNameOrPath(node, nameOrPath)).trim();
		context.report({
			node,
			messageId: MESSAGE_ID_FUNCTION,
			data: {functionName},
			fix: fixer => fixer.replaceText(node, 'Object.fromEntries'),
		});
	};

	return listeners;
}

const schema = [
	{
		type: 'object',
		additionalProperties: false,
		properties: {
			functions: {
				type: 'array',
				uniqueItems: true,
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
			description: 'Prefer using `Object.fromEntries(…)` to transform a list of key-value pairs into an object.',
			url: getDocumentationUrl(__filename),
		},
		fixable: 'code',
		schema,
		messages,
	},
};
