'use strict';
const getVariableIdentifiers = require('../utils/get-variable-identifiers.js');
const replaceReferenceIdentifier = require('./replace-reference-identifier.js');

const renameVariable = (variable, name, fixer) =>
	getVariableIdentifiers(variable)
		.map(identifier => replaceReferenceIdentifier(identifier, name, fixer));

module.exports = renameVariable;
