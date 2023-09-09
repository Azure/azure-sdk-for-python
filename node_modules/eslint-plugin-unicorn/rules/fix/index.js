'use strict';

module.exports = {
	// Utilities
	extendFixRange: require('./extend-fix-range.js'),
	removeParentheses: require('./remove-parentheses.js'),

	appendArgument: require('./append-argument.js'),
	removeArgument: require('./remove-argument.js'),
	replaceArgument: require('./replace-argument.js'),
	switchNewExpressionToCallExpression: require('./switch-new-expression-to-call-expression.js'),
	switchCallExpressionToNewExpression: require('./switch-call-expression-to-new-expression.js'),
	removeMemberExpressionProperty: require('./remove-member-expression-property.js'),
	removeMethodCall: require('./remove-method-call.js'),
	replaceTemplateElement: require('./replace-template-element.js'),
	replaceReferenceIdentifier: require('./replace-reference-identifier.js'),
	renameVariable: require('./rename-variable.js'),
	replaceNodeOrTokenAndSpacesBefore: require('./replace-node-or-token-and-spaces-before.js'),
	removeSpacesAfter: require('./remove-spaces-after.js'),
	fixSpaceAroundKeyword: require('./fix-space-around-keywords.js'),
	replaceStringLiteral: require('./replace-string-literal.js'),
	addParenthesizesToReturnOrThrowExpression: require('./add-parenthesizes-to-return-or-throw-expression.js'),
};
