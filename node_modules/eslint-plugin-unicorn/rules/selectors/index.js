'use strict';

module.exports = {
	// Utilities
	matches: require('./matches-any.js'),
	not: require('./negation.js'),

	arrayPrototypeMethodSelector: require('./prototype-method-selector.js').arrayPrototypeMethodSelector,
	objectPrototypeMethodSelector: require('./prototype-method-selector.js').objectPrototypeMethodSelector,
	emptyArraySelector: require('./empty-array-selector.js'),
	emptyObjectSelector: require('./empty-object-selector.js'),
	memberExpressionSelector: require('./member-expression-selector.js'),
	methodCallSelector: require('./method-call-selector.js'),
	notDomNodeSelector: require('./not-dom-node.js').notDomNodeSelector,
	notFunctionSelector: require('./not-function.js').notFunctionSelector,
	referenceIdentifierSelector: require('./reference-identifier-selector.js'),
	callExpressionSelector: require('./call-or-new-expression-selector.js').callExpressionSelector,
	newExpressionSelector: require('./call-or-new-expression-selector.js').newExpressionSelector,
	callOrNewExpressionSelector: require('./call-or-new-expression-selector.js').callOrNewExpressionSelector,
	STATIC_REQUIRE_SELECTOR: require('./require-selector.js').STATIC_REQUIRE_SELECTOR,
	STATIC_REQUIRE_SOURCE_SELECTOR: require('./require-selector.js').STATIC_REQUIRE_SOURCE_SELECTOR,
};
