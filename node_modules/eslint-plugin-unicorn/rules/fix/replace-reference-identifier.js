'use strict';

const isShorthandPropertyValue = require('../utils/is-shorthand-property-value.js');
const isShorthandPropertyAssignmentPatternLeft = require('../utils/is-shorthand-property-assignment-pattern-left.js');
const isShorthandImportLocal = require('../utils/is-shorthand-import-local.js');
const isShorthandExportLocal = require('../utils/is-shorthand-export-local.js');

function replaceReferenceIdentifier(identifier, replacement, fixer) {
	if (
		isShorthandPropertyValue(identifier)
		|| isShorthandPropertyAssignmentPatternLeft(identifier)
	) {
		return fixer.replaceText(identifier, `${identifier.name}: ${replacement}`);
	}

	if (isShorthandImportLocal(identifier)) {
		return fixer.replaceText(identifier, `${identifier.name} as ${replacement}`);
	}

	if (isShorthandExportLocal(identifier)) {
		return fixer.replaceText(identifier, `${replacement} as ${identifier.name}`);
	}

	// `typeAnnotation`
	if (identifier.typeAnnotation) {
		return fixer.replaceTextRange(
			[identifier.range[0], identifier.typeAnnotation.range[0]],
			`${replacement}${identifier.optional ? '?' : ''}`,
		);
	}

	return fixer.replaceText(identifier, replacement);
}

module.exports = replaceReferenceIdentifier;
