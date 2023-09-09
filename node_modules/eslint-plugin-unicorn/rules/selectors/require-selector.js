'use strict';
const {callExpressionSelector} = require('./call-or-new-expression-selector.js');

const requireCallSelector = callExpressionSelector({
	name: 'require',
	argumentsLength: 1,
	// Do not add check on first argument
	allowSpreadElement: true,
});

module.exports = {
	STATIC_REQUIRE_SELECTOR: `${requireCallSelector}[arguments.0.type="Literal"]`,
	STATIC_REQUIRE_SOURCE_SELECTOR: `${requireCallSelector}  > Literal.arguments`,
};
