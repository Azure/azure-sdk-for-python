'use strict';
const {isClosingParenToken, getStaticValue} = require('@eslint-community/eslint-utils');
const avoidCapture = require('./utils/avoid-capture.js');
const getScopes = require('./utils/get-scopes.js');
const singular = require('./utils/singular.js');
const toLocation = require('./utils/to-location.js');
const getReferences = require('./utils/get-references.js');
const {isLiteral} = require('./ast/index.js');

const MESSAGE_ID = 'no-for-loop';
const messages = {
	[MESSAGE_ID]: 'Use a `for-of` loop instead of this `for` loop.',
};

const defaultElementName = 'element';
const isLiteralZero = node => isLiteral(node, 0);
const isLiteralOne = node => isLiteral(node, 1);

const isIdentifierWithName = (node, name) => node?.type === 'Identifier' && node.name === name;

const getIndexIdentifierName = forStatement => {
	const {init: variableDeclaration} = forStatement;

	if (
		!variableDeclaration
		|| variableDeclaration.type !== 'VariableDeclaration'
	) {
		return;
	}

	if (variableDeclaration.declarations.length !== 1) {
		return;
	}

	const [variableDeclarator] = variableDeclaration.declarations;

	if (!isLiteralZero(variableDeclarator.init)) {
		return;
	}

	if (variableDeclarator.id.type !== 'Identifier') {
		return;
	}

	return variableDeclarator.id.name;
};

const getStrictComparisonOperands = binaryExpression => {
	if (binaryExpression.operator === '<') {
		return {
			lesser: binaryExpression.left,
			greater: binaryExpression.right,
		};
	}

	if (binaryExpression.operator === '>') {
		return {
			lesser: binaryExpression.right,
			greater: binaryExpression.left,
		};
	}
};

const getArrayIdentifierFromBinaryExpression = (binaryExpression, indexIdentifierName) => {
	const operands = getStrictComparisonOperands(binaryExpression);

	if (!operands) {
		return;
	}

	const {lesser, greater} = operands;

	if (!isIdentifierWithName(lesser, indexIdentifierName)) {
		return;
	}

	if (greater.type !== 'MemberExpression') {
		return;
	}

	if (
		greater.object.type !== 'Identifier'
		|| greater.property.type !== 'Identifier'
	) {
		return;
	}

	if (greater.property.name !== 'length') {
		return;
	}

	return greater.object;
};

const getArrayIdentifier = (forStatement, indexIdentifierName) => {
	const {test} = forStatement;

	if (!test || test.type !== 'BinaryExpression') {
		return;
	}

	return getArrayIdentifierFromBinaryExpression(test, indexIdentifierName);
};

const isLiteralOnePlusIdentifierWithName = (node, identifierName) => {
	if (node?.type === 'BinaryExpression' && node.operator === '+') {
		return (isIdentifierWithName(node.left, identifierName) && isLiteralOne(node.right))
			|| (isIdentifierWithName(node.right, identifierName) && isLiteralOne(node.left));
	}

	return false;
};

const checkUpdateExpression = (forStatement, indexIdentifierName) => {
	const {update} = forStatement;

	if (!update) {
		return false;
	}

	if (update.type === 'UpdateExpression') {
		return update.operator === '++' && isIdentifierWithName(update.argument, indexIdentifierName);
	}

	if (
		update.type === 'AssignmentExpression'
		&& isIdentifierWithName(update.left, indexIdentifierName)
	) {
		if (update.operator === '+=') {
			return isLiteralOne(update.right);
		}

		if (update.operator === '=') {
			return isLiteralOnePlusIdentifierWithName(update.right, indexIdentifierName);
		}
	}

	return false;
};

const isOnlyArrayOfIndexVariableRead = (arrayReferences, indexIdentifierName) => arrayReferences.every(reference => {
	const node = reference.identifier.parent;

	if (node.type !== 'MemberExpression') {
		return false;
	}

	if (node.property.name !== indexIdentifierName) {
		return false;
	}

	if (
		node.parent.type === 'AssignmentExpression'
		&& node.parent.left === node
	) {
		return false;
	}

	return true;
});

const getRemovalRange = (node, sourceCode) => {
	const declarationNode = node.parent;

	if (declarationNode.declarations.length === 1) {
		const {line} = declarationNode.loc.start;
		const lineText = sourceCode.lines[line - 1];

		const isOnlyNodeOnLine = lineText.trim() === sourceCode.getText(declarationNode);

		return isOnlyNodeOnLine ? [
			sourceCode.getIndexFromLoc({line, column: 0}),
			sourceCode.getIndexFromLoc({line: line + 1, column: 0}),
		] : declarationNode.range;
	}

	const index = declarationNode.declarations.indexOf(node);

	if (index === 0) {
		return [
			node.range[0],
			declarationNode.declarations[1].range[0],
		];
	}

	return [
		declarationNode.declarations[index - 1].range[1],
		node.range[1],
	];
};

const resolveIdentifierName = (name, scope) => {
	while (scope) {
		const variable = scope.set.get(name);

		if (variable) {
			return variable;
		}

		scope = scope.upper;
	}
};

const scopeContains = (ancestor, descendant) => {
	while (descendant) {
		if (descendant === ancestor) {
			return true;
		}

		descendant = descendant.upper;
	}

	return false;
};

const nodeContains = (ancestor, descendant) => {
	while (descendant) {
		if (descendant === ancestor) {
			return true;
		}

		descendant = descendant.parent;
	}

	return false;
};

const isIndexVariableUsedElsewhereInTheLoopBody = (indexVariable, bodyScope, arrayIdentifierName) => {
	const inBodyReferences = indexVariable.references.filter(reference => scopeContains(bodyScope, reference.from));

	const referencesOtherThanArrayAccess = inBodyReferences.filter(reference => {
		const node = reference.identifier.parent;

		if (node.type !== 'MemberExpression') {
			return true;
		}

		if (node.object.name !== arrayIdentifierName) {
			return true;
		}

		return false;
	});

	return referencesOtherThanArrayAccess.length > 0;
};

const isIndexVariableAssignedToInTheLoopBody = (indexVariable, bodyScope) =>
	indexVariable.references
		.filter(reference => scopeContains(bodyScope, reference.from))
		.some(inBodyReference => inBodyReference.isWrite());

const someVariablesLeakOutOfTheLoop = (forStatement, variables, forScope) =>
	variables.some(
		variable => !variable.references.every(
			reference => scopeContains(forScope, reference.from) || nodeContains(forStatement, reference.identifier),
		),
	);

const getReferencesInChildScopes = (scope, name) =>
	getReferences(scope).filter(reference => reference.identifier.name === name);

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => {
	const sourceCode = context.getSourceCode();
	const {scopeManager, text: sourceCodeText} = sourceCode;

	return {
		ForStatement(node) {
			const indexIdentifierName = getIndexIdentifierName(node);

			if (!indexIdentifierName) {
				return;
			}

			const arrayIdentifier = getArrayIdentifier(node, indexIdentifierName);
			if (!arrayIdentifier) {
				return;
			}

			const arrayIdentifierName = arrayIdentifier.name;

			const scope = sourceCode.getScope(node);
			const staticResult = getStaticValue(arrayIdentifier, scope);
			if (staticResult && !Array.isArray(staticResult.value)) {
				// Bail out if we can tell that the array variable has a non-array value (i.e. we're looping through the characters of a string constant).
				return;
			}

			if (!checkUpdateExpression(node, indexIdentifierName)) {
				return;
			}

			if (!node.body || node.body.type !== 'BlockStatement') {
				return;
			}

			const forScope = scopeManager.acquire(node);
			const bodyScope = scopeManager.acquire(node.body);

			if (!bodyScope) {
				return;
			}

			const indexVariable = resolveIdentifierName(indexIdentifierName, bodyScope);

			if (isIndexVariableAssignedToInTheLoopBody(indexVariable, bodyScope)) {
				return;
			}

			const arrayReferences = getReferencesInChildScopes(bodyScope, arrayIdentifierName);

			if (arrayReferences.length === 0) {
				return;
			}

			if (!isOnlyArrayOfIndexVariableRead(arrayReferences, indexIdentifierName)) {
				return;
			}

			const [start] = node.range;
			const [, end] = sourceCode.getTokenBefore(node.body, isClosingParenToken).range;

			const problem = {
				loc: toLocation([start, end], sourceCode),
				messageId: MESSAGE_ID,
			};

			const elementReference = arrayReferences.find(reference => {
				const node = reference.identifier.parent;

				if (node.parent.type !== 'VariableDeclarator') {
					return false;
				}

				return true;
			});
			const elementNode = elementReference?.identifier.parent.parent;
			const elementIdentifierName = elementNode?.id.name;
			const elementVariable = elementIdentifierName && resolveIdentifierName(elementIdentifierName, bodyScope);

			const shouldFix = !someVariablesLeakOutOfTheLoop(node, [indexVariable, elementVariable].filter(Boolean), forScope);

			if (shouldFix) {
				problem.fix = function * (fixer) {
					const shouldGenerateIndex = isIndexVariableUsedElsewhereInTheLoopBody(indexVariable, bodyScope, arrayIdentifierName);

					const index = indexIdentifierName;
					const element = elementIdentifierName
						|| avoidCapture(singular(arrayIdentifierName) || defaultElementName, getScopes(bodyScope));
					const array = arrayIdentifierName;

					let declarationElement = element;
					let declarationType = 'const';
					let removeDeclaration = true;
					let typeAnnotation;

					if (elementNode) {
						if (elementNode.id.type === 'ObjectPattern' || elementNode.id.type === 'ArrayPattern') {
							removeDeclaration = arrayReferences.length === 1;
						}

						if (removeDeclaration) {
							declarationType = element.type === 'VariableDeclarator' ? elementNode.kind : elementNode.parent.kind;
							if (elementNode.id.typeAnnotation && shouldGenerateIndex) {
								declarationElement = sourceCodeText.slice(elementNode.id.range[0], elementNode.id.typeAnnotation.range[0]).trim();
								typeAnnotation = sourceCode.getText(
									elementNode.id.typeAnnotation,
									-1, // Skip leading `:`
								).trim();
							} else {
								declarationElement = sourceCode.getText(elementNode.id);
							}
						}
					}

					const parts = [declarationType];
					if (shouldGenerateIndex) {
						parts.push(` [${index}, ${declarationElement}]`);
						if (typeAnnotation) {
							parts.push(`: [number, ${typeAnnotation}]`);
						}

						parts.push(` of ${array}.entries()`);
					} else {
						parts.push(` ${declarationElement} of ${array}`);
					}

					const replacement = parts.join('');

					yield fixer.replaceTextRange([
						node.init.range[0],
						node.update.range[1],
					], replacement);

					for (const reference of arrayReferences) {
						if (reference !== elementReference) {
							yield fixer.replaceText(reference.identifier.parent, element);
						}
					}

					if (elementNode) {
						yield removeDeclaration
							? fixer.removeRange(getRemovalRange(elementNode, sourceCode))
							: fixer.replaceText(elementNode.init, element);
					}
				};
			}

			return problem;
		},
	};
};

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Do not use a `for` loop that can be replaced with a `for-of` loop.',
		},
		fixable: 'code',
		messages,
		hasSuggestion: true,
	},
};
