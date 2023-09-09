'use strict';
const {defaultsDeep} = require('lodash');
const {getStringIfConstant} = require('@eslint-community/eslint-utils');
const {callExpressionSelector} = require('./selectors/index.js');

const MESSAGE_ID = 'importStyle';
const messages = {
	[MESSAGE_ID]: 'Use {{allowedStyles}} import for module `{{moduleName}}`.',
};

const getActualImportDeclarationStyles = importDeclaration => {
	const {specifiers} = importDeclaration;

	if (specifiers.length === 0) {
		return ['unassigned'];
	}

	const styles = new Set();

	for (const specifier of specifiers) {
		if (specifier.type === 'ImportDefaultSpecifier') {
			styles.add('default');
			continue;
		}

		if (specifier.type === 'ImportNamespaceSpecifier') {
			styles.add('namespace');
			continue;
		}

		if (specifier.type === 'ImportSpecifier') {
			if (specifier.imported.type === 'Identifier' && specifier.imported.name === 'default') {
				styles.add('default');
				continue;
			}

			styles.add('named');
			continue;
		}
	}

	return [...styles];
};

const getActualExportDeclarationStyles = exportDeclaration => {
	const {specifiers} = exportDeclaration;

	if (specifiers.length === 0) {
		return ['unassigned'];
	}

	const styles = new Set();

	for (const specifier of specifiers) {
		if (specifier.type === 'ExportSpecifier') {
			if (specifier.exported.type === 'Identifier' && specifier.exported.name === 'default') {
				styles.add('default');
				continue;
			}

			styles.add('named');
			continue;
		}
	}

	return [...styles];
};

const getActualAssignmentTargetImportStyles = assignmentTarget => {
	if (assignmentTarget.type === 'Identifier' || assignmentTarget.type === 'ArrayPattern') {
		return ['namespace'];
	}

	if (assignmentTarget.type === 'ObjectPattern') {
		if (assignmentTarget.properties.length === 0) {
			return ['unassigned'];
		}

		const styles = new Set();

		for (const property of assignmentTarget.properties) {
			if (property.type === 'RestElement') {
				styles.add('named');
				continue;
			}

			if (property.key.type === 'Identifier') {
				if (property.key.name === 'default') {
					styles.add('default');
				} else {
					styles.add('named');
				}
			}
		}

		return [...styles];
	}

	// Next line is not test-coverable until unforceable changes to the language
	// like an addition of new AST node types usable in `const __HERE__ = foo;`.
	// An exotic custom parser or a bug in one could cover it too.
	/* c8 ignore next */
	return [];
};

const joinOr = words => words
	.map((word, index) => {
		if (index === words.length - 1) {
			return word;
		}

		if (index === words.length - 2) {
			return word + ' or';
		}

		return word + ',';
	})
	.join(' ');

// Keep this alphabetically sorted for easier maintenance
const defaultStyles = {
	chalk: {
		default: true,
	},
	path: {
		default: true,
	},
	util: {
		named: true,
	},
};

const assignedDynamicImportSelector = [
	'VariableDeclarator',
	'[init.type="AwaitExpression"]',
	'[init.argument.type="ImportExpression"]',
].join('');

const assignedRequireSelector = [
	'VariableDeclarator',
	'[init.type="CallExpression"]',
	'[init.callee.type="Identifier"]',
	'[init.callee.name="require"]',
].join('');

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	let [
		{
			styles = {},
			extendDefaultStyles = true,
			checkImport = true,
			checkDynamicImport = true,
			checkExportFrom = false,
			checkRequire = true,
		} = {},
	] = context.options;

	styles = extendDefaultStyles
		? defaultsDeep({}, styles, defaultStyles)
		: styles;

	styles = new Map(
		Object.entries(styles).map(
			([moduleName, styles]) =>
				[moduleName, new Set(Object.entries(styles).filter(([, isAllowed]) => isAllowed).map(([style]) => style))],
		),
	);

	const sourceCode = context.getSourceCode();

	const report = (node, moduleName, actualImportStyles, allowedImportStyles, isRequire = false) => {
		if (!allowedImportStyles || allowedImportStyles.size === 0) {
			return;
		}

		let effectiveAllowedImportStyles = allowedImportStyles;

		// For `require`, `'default'` style allows both `x = require('x')` (`'namespace'` style) and
		// `{default: x} = require('x')` (`'default'` style) since we don't know in advance
		// whether `'x'` is a compiled ES6 module (with `default` key) or a CommonJS module and `require`
		// does not provide any automatic interop for this, so the user may have to use either of these.
		if (isRequire && allowedImportStyles.has('default') && !allowedImportStyles.has('namespace')) {
			effectiveAllowedImportStyles = new Set(allowedImportStyles);
			effectiveAllowedImportStyles.add('namespace');
		}

		if (actualImportStyles.every(style => effectiveAllowedImportStyles.has(style))) {
			return;
		}

		const data = {
			allowedStyles: joinOr([...allowedImportStyles.keys()]),
			moduleName,
		};

		context.report({
			node,
			messageId: MESSAGE_ID,
			data,
		});
	};

	let visitor = {};

	if (checkImport) {
		visitor = {
			...visitor,

			ImportDeclaration(node) {
				const moduleName = getStringIfConstant(node.source, sourceCode.getScope(node.source));

				const allowedImportStyles = styles.get(moduleName);
				const actualImportStyles = getActualImportDeclarationStyles(node);

				report(node, moduleName, actualImportStyles, allowedImportStyles);
			},
		};
	}

	if (checkDynamicImport) {
		visitor = {
			...visitor,

			'ExpressionStatement > ImportExpression'(node) {
				const moduleName = getStringIfConstant(node.source, sourceCode.getScope(node.source));
				const allowedImportStyles = styles.get(moduleName);
				const actualImportStyles = ['unassigned'];

				report(node, moduleName, actualImportStyles, allowedImportStyles);
			},

			[assignedDynamicImportSelector](node) {
				const assignmentTargetNode = node.id;
				const moduleNameNode = node.init.argument.source;
				const moduleName = getStringIfConstant(moduleNameNode, sourceCode.getScope(moduleNameNode));

				if (!moduleName) {
					return;
				}

				const allowedImportStyles = styles.get(moduleName);
				const actualImportStyles = getActualAssignmentTargetImportStyles(assignmentTargetNode);

				report(node, moduleName, actualImportStyles, allowedImportStyles);
			},
		};
	}

	if (checkExportFrom) {
		visitor = {
			...visitor,

			ExportAllDeclaration(node) {
				const moduleName = getStringIfConstant(node.source, sourceCode.getScope(node.source));

				const allowedImportStyles = styles.get(moduleName);
				const actualImportStyles = ['namespace'];

				report(node, moduleName, actualImportStyles, allowedImportStyles);
			},

			ExportNamedDeclaration(node) {
				const moduleName = getStringIfConstant(node.source, sourceCode.getScope(node.source));

				const allowedImportStyles = styles.get(moduleName);
				const actualImportStyles = getActualExportDeclarationStyles(node);

				report(node, moduleName, actualImportStyles, allowedImportStyles);
			},
		};
	}

	if (checkRequire) {
		visitor = {
			...visitor,

			[`ExpressionStatement > ${callExpressionSelector({name: 'require', argumentsLength: 1})}.expression`](node) {
				const moduleName = getStringIfConstant(node.arguments[0], sourceCode.getScope(node.arguments[0]));
				const allowedImportStyles = styles.get(moduleName);
				const actualImportStyles = ['unassigned'];

				report(node, moduleName, actualImportStyles, allowedImportStyles, true);
			},

			[assignedRequireSelector](node) {
				const assignmentTargetNode = node.id;
				const moduleNameNode = node.init.arguments[0];
				const moduleName = getStringIfConstant(moduleNameNode, sourceCode.getScope(moduleNameNode));

				if (!moduleName) {
					return;
				}

				const allowedImportStyles = styles.get(moduleName);
				const actualImportStyles = getActualAssignmentTargetImportStyles(assignmentTargetNode);

				report(node, moduleName, actualImportStyles, allowedImportStyles, true);
			},
		};
	}

	return visitor;
};

const schema = {
	type: 'array',
	additionalItems: false,
	items: [
		{
			type: 'object',
			additionalProperties: false,
			properties: {
				checkImport: {
					type: 'boolean',
				},
				checkDynamicImport: {
					type: 'boolean',
				},
				checkExportFrom: {
					type: 'boolean',
				},
				checkRequire: {
					type: 'boolean',
				},
				extendDefaultStyles: {
					type: 'boolean',
				},
				styles: {
					$ref: '#/definitions/moduleStyles',
				},
			},
		},
	],
	definitions: {
		moduleStyles: {
			type: 'object',
			additionalProperties: {
				$ref: '#/definitions/styles',
			},
		},
		styles: {
			anyOf: [
				{
					enum: [
						false,
					],
				},
				{
					$ref: '#/definitions/booleanObject',
				},
			],
		},
		booleanObject: {
			type: 'object',
			additionalProperties: {
				type: 'boolean',
			},
		},
	},
};

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'problem',
		docs: {
			description: 'Enforce specific import styles per module.',
		},
		schema,
		messages,
	},
};
