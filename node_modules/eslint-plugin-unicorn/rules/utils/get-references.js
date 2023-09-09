'use strict';

const getScopes = require('./get-scopes.js');

const getReferences = scope => [...new Set(
	getScopes(scope).flatMap(({references}) => references),
)];

module.exports = getReferences;
