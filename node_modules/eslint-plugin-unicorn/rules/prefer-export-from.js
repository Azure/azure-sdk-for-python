'use strict';
const {
	isCommaToken,
	isOpeningBraceToken,
	isClosingBraceToken,
} = require('@eslint-community/eslint-utils');

const MESSAGE_ID_ERROR = 'error';
const MESSAGE_ID_SUGGESTION = 'suggestion';
const messages = {
	[MESSAGE_ID_ERROR]: 'Use `export…from` to re-export `{{exported}}`.',
	[MESSAGE_ID_SUGGESTION]: 'Switch to `export…from`.',
};

// Default import/export can be `Identifier`, have to use `Symbol.for`
const DEFAULT_SPECIFIER_NAME = Symbol.for('default');
const NAMESPACE_SPECIFIER_NAME = Symbol('NAMESPACE_SPECIFIER_NAME');

const getSpecifierName = node => {
	switch (node.type) {
		case 'Identifier': {
			return Symbol.for(node.name);
		}

		case 'Literal': {
			return node.value;
		}
		// No default
	}
};

const isTypeExport = specifier => specifier.exportKind === 'type' || specifier.parent.exportKind === 'type';

const isTypeImport = specifier => specifier.importKind === 'type' || specifier.parent.importKind === 'type';

function * removeSpecifier(node, fixer, sourceCode) {
	const {parent} = node;
	const {specifiers} = parent;

	if (specifiers.length === 1) {
		yield * removeImportOrExport(parent, fixer, sourceCode);
		return;
	}

	switch (node.type) {
		case 'ImportSpecifier': {
			const hasOtherSpecifiers = specifiers.some(specifier => specifier !== node && specifier.type === node.type);
			if (!hasOtherSpecifiers) {
				const closingBraceToken = sourceCode.getTokenAfter(node, isClosingBraceToken);

				// If there are other specifiers, they have to be the default import specifier
				// And the default import has to write before the named import specifiers
				// So there must be a comma before
				const commaToken = sourceCode.getTokenBefore(node, isCommaToken);
				yield fixer.replaceTextRange([commaToken.range[0], closingBraceToken.range[1]], '');
				return;
			}
			// Fallthrough
		}

		case 'ExportSpecifier':
		case 'ImportNamespaceSpecifier':
		case 'ImportDefaultSpecifier': {
			yield fixer.remove(node);

			const tokenAfter = sourceCode.getTokenAfter(node);
			if (isCommaToken(tokenAfter)) {
				yield fixer.remove(tokenAfter);
			}

			break;
		}

		// No default
	}
}

function * removeImportOrExport(node, fixer, sourceCode) {
	switch (node.type) {
		case 'ImportSpecifier':
		case 'ExportSpecifier':
		case 'ImportDefaultSpecifier':
		case 'ImportNamespaceSpecifier': {
			yield * removeSpecifier(node, fixer, sourceCode);
			return;
		}

		case 'ImportDeclaration':
		case 'ExportDefaultDeclaration':
		case 'ExportNamedDeclaration': {
			yield fixer.remove(node);
		}

		// No default
	}
}

function getSourceAndAssertionsText(declaration, sourceCode) {
	const keywordFromToken = sourceCode.getTokenBefore(
		declaration.source,
		token => token.type === 'Identifier' && token.value === 'from',
	);
	const [start] = keywordFromToken.range;
	const [, end] = declaration.range;
	return sourceCode.text.slice(start, end);
}

function getFixFunction({
	sourceCode,
	imported,
	exported,
	exportDeclarations,
	program,
}) {
	const importDeclaration = imported.declaration;
	const sourceNode = importDeclaration.source;
	const sourceValue = sourceNode.value;
	const shouldExportAsType = imported.isTypeImport || exported.isTypeExport;

	let exportDeclaration;
	if (shouldExportAsType) {
		// If a type export declaration already exists, reuse it, else use a value export declaration with an inline type specifier.
		exportDeclaration = exportDeclarations.find(({source, exportKind}) => source.value === sourceValue && exportKind === 'type');
	}

	if (!exportDeclaration) {
		exportDeclaration = exportDeclarations.find(({source, exportKind}) => source.value === sourceValue && exportKind !== 'type');
	}

	/** @param {import('eslint').Rule.RuleFixer} fixer */
	return function * (fixer) {
		if (imported.name === NAMESPACE_SPECIFIER_NAME) {
			yield fixer.insertTextAfter(
				program,
				`\nexport * as ${exported.text} ${getSourceAndAssertionsText(importDeclaration, sourceCode)}`,
			);
		} else {
			let specifierText = exported.name === imported.name
				? exported.text
				: `${imported.text} as ${exported.text}`;

			// Add an inline type specifier if the value is a type and the export deceleration is a value deceleration
			if (shouldExportAsType && (!exportDeclaration || exportDeclaration.exportKind !== 'type')) {
				specifierText = `type ${specifierText}`;
			}

			if (exportDeclaration) {
				const lastSpecifier = exportDeclaration.specifiers[exportDeclaration.specifiers.length - 1];

				// `export {} from 'foo';`
				if (lastSpecifier) {
					yield fixer.insertTextAfter(lastSpecifier, `, ${specifierText}`);
				} else {
					const openingBraceToken = sourceCode.getFirstToken(exportDeclaration, isOpeningBraceToken);
					yield fixer.insertTextAfter(openingBraceToken, specifierText);
				}
			} else {
				yield fixer.insertTextAfter(
					program,
					`\nexport {${specifierText}} ${getSourceAndAssertionsText(importDeclaration, sourceCode)}`,
				);
			}
		}

		if (imported.variable.references.length === 1) {
			yield * removeImportOrExport(imported.node, fixer, sourceCode);
		}

		yield * removeImportOrExport(exported.node, fixer, sourceCode);
	};
}

function getExported(identifier, sourceCode) {
	const {parent} = identifier;
	switch (parent.type) {
		case 'ExportDefaultDeclaration': {
			return {
				node: parent,
				name: DEFAULT_SPECIFIER_NAME,
				text: 'default',
				isTypeExport: isTypeExport(parent),
			};
		}

		case 'ExportSpecifier': {
			return {
				node: parent,
				name: getSpecifierName(parent.exported),
				text: sourceCode.getText(parent.exported),
				isTypeExport: isTypeExport(parent),
			};
		}

		case 'VariableDeclarator': {
			if (
				parent.init === identifier
				&& parent.id.type === 'Identifier'
				&& !parent.id.typeAnnotation
				&& parent.parent.type === 'VariableDeclaration'
				&& parent.parent.kind === 'const'
				&& parent.parent.declarations.length === 1
				&& parent.parent.declarations[0] === parent
				&& parent.parent.parent.type === 'ExportNamedDeclaration'
				&& isVariableUnused(parent, sourceCode)
			) {
				return {
					node: parent.parent.parent,
					name: Symbol.for(parent.id.name),
					text: sourceCode.getText(parent.id),
				};
			}

			break;
		}

		// No default
	}
}

function isVariableUnused(node, sourceCode) {
	const variables = sourceCode.getDeclaredVariables(node);

	/* c8 ignore next 3 */
	if (variables.length !== 1) {
		return false;
	}

	const [{identifiers, references}] = variables;
	return identifiers.length === 1
		&& identifiers[0] === node.id
		&& references.length === 1
		&& references[0].identifier === node.id;
}

function getImported(variable, sourceCode) {
	const specifier = variable.defs[0].node;
	const result = {
		node: specifier,
		declaration: specifier.parent,
		variable,
		isTypeImport: isTypeImport(specifier),
	};

	switch (specifier.type) {
		case 'ImportDefaultSpecifier': {
			return {
				name: DEFAULT_SPECIFIER_NAME,
				text: 'default',
				...result,
			};
		}

		case 'ImportSpecifier': {
			return {
				name: getSpecifierName(specifier.imported),
				text: sourceCode.getText(specifier.imported),
				...result,
			};
		}

		case 'ImportNamespaceSpecifier': {
			return {
				name: NAMESPACE_SPECIFIER_NAME,
				text: '*',
				...result,
			};
		}

		// No default
	}
}

function getExports(imported, sourceCode) {
	const exports = [];
	for (const {identifier} of imported.variable.references) {
		const exported = getExported(identifier, sourceCode);

		if (!exported) {
			continue;
		}

		/*
		There is no substitution for:

		```js
		import * as foo from 'foo';
		export default foo;
		```
		*/
		if (imported.name === NAMESPACE_SPECIFIER_NAME && exported.name === DEFAULT_SPECIFIER_NAME) {
			continue;
		}

		exports.push(exported);
	}

	return exports;
}

const schema = [
	{
		type: 'object',
		additionalProperties: false,
		properties: {
			ignoreUsedVariables: {
				type: 'boolean',
				default: false,
			},
		},
	},
];

/** @param {import('eslint').Rule.RuleContext} context */
function create(context) {
	const sourceCode = context.getSourceCode();
	const {ignoreUsedVariables} = {ignoreUsedVariables: false, ...context.options[0]};
	const importDeclarations = new Set();
	const exportDeclarations = [];

	return {
		'ImportDeclaration[specifiers.length>0]'(node) {
			importDeclarations.add(node);
		},
		// `ExportAllDeclaration` and `ExportDefaultDeclaration` can't be reused
		'ExportNamedDeclaration[source.type="Literal"]'(node) {
			exportDeclarations.push(node);
		},
		* 'Program:exit'(program) {
			for (const importDeclaration of importDeclarations) {
				let variables = sourceCode.getDeclaredVariables(importDeclaration);

				if (variables.some(variable => variable.defs.length !== 1 || variable.defs[0].parent !== importDeclaration)) {
					continue;
				}

				variables = variables.map(variable => {
					const imported = getImported(variable, sourceCode);
					const exports = getExports(imported, sourceCode);

					return {
						variable,
						imported,
						exports,
					};
				});

				if (
					ignoreUsedVariables
					&& variables.some(({variable, exports}) => variable.references.length !== exports.length)
				) {
					continue;
				}

				const shouldUseSuggestion = ignoreUsedVariables
					&& variables.some(({variable}) => variable.references.length === 0);

				for (const {imported, exports} of variables) {
					for (const exported of exports) {
						const problem = {
							node: exported.node,
							messageId: MESSAGE_ID_ERROR,
							data: {
								exported: exported.text,
							},
						};
						const fix = getFixFunction({
							sourceCode,
							imported,
							exported,
							exportDeclarations,
							program,
						});

						if (shouldUseSuggestion) {
							problem.suggest = [
								{
									messageId: MESSAGE_ID_SUGGESTION,
									fix,
								},
							];
						} else {
							problem.fix = fix;
						}

						yield problem;
					}
				}
			}
		},
	};
}

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer `export…from` when re-exporting.',
		},
		fixable: 'code',
		hasSuggestions: true,
		schema,
		messages,
	},
};
