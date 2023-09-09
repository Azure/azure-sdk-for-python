'use strict';
const {findVariable} = require('@eslint-community/eslint-utils');
const avoidCapture = require('./utils/avoid-capture.js');
const {renameVariable} = require('./fix/index.js');
const {matches, methodCallSelector} = require('./selectors/index.js');

const MESSAGE_ID = 'catch-error-name';
const messages = {
	[MESSAGE_ID]: 'The catch parameter `{{originalName}}` should be named `{{fixedName}}`.',
};

const selector = matches([
	// `try {} catch (foo) {}`
	[
		'CatchClause',
		' > ',
		'Identifier.param',
	].join(''),
	// - `promise.then(…, foo => {})`
	// - `promise.then(…, function(foo) {})`
	// - `promise.catch(foo => {})`
	// - `promise.catch(function(foo) {})`
	[
		matches([
			methodCallSelector({method: 'then', argumentsLength: 2}),
			methodCallSelector({method: 'catch', argumentsLength: 1}),
		]),
		' > ',
		':matches(FunctionExpression, ArrowFunctionExpression).arguments:last-child',
		' > ',
		'Identifier.params:first-child',
	].join(''),
]);

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const options = {
		name: 'error',
		ignore: [],
		...context.options[0],
	};
	const {name: expectedName} = options;
	const ignore = options.ignore.map(
		pattern => pattern instanceof RegExp ? pattern : new RegExp(pattern, 'u'),
	);
	const isNameAllowed = name =>
		name === expectedName
		|| ignore.some(regexp => regexp.test(name))
		|| name.endsWith(expectedName)
		|| name.endsWith(expectedName.charAt(0).toUpperCase() + expectedName.slice(1));

	return {
		[selector](node) {
			const originalName = node.name;

			if (
				isNameAllowed(originalName)
				|| isNameAllowed(originalName.replace(/_+$/g, ''))
			) {
				return;
			}

			const scope = context.getSourceCode().getScope(node);
			const variable = findVariable(scope, node);

			// This was reported https://github.com/sindresorhus/eslint-plugin-unicorn/issues/1075#issuecomment-768072967
			// But can't reproduce, just ignore this case
			/* c8 ignore next 3 */
			if (!variable) {
				return;
			}

			if (originalName === '_' && variable.references.length === 0) {
				return;
			}

			const scopes = [
				variable.scope,
				...variable.references.map(({from}) => from),
			];
			const fixedName = avoidCapture(expectedName, scopes);

			const problem = {
				node,
				messageId: MESSAGE_ID,
				data: {
					originalName,
					fixedName: fixedName || expectedName,
				},
			};

			if (fixedName) {
				problem.fix = fixer => renameVariable(variable, fixedName, fixer);
			}

			return problem;
		},
	};
};

const schema = [
	{
		type: 'object',
		additionalProperties: false,
		properties: {
			name: {
				type: 'string',
			},
			ignore: {
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
			description: 'Enforce a specific parameter name in catch clauses.',
		},
		fixable: 'code',
		schema,
		messages,
	},
};
