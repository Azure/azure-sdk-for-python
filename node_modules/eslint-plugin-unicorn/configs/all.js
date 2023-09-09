'use strict';
const {rules, ...baseConfigs} = require('./recommended.js');

module.exports = {
	...baseConfigs,
	rules: Object.fromEntries(Object.entries(rules).map(
		([ruleId, severity]) => [ruleId, ruleId.startsWith('unicorn/') ? 'error' : severity],
	)),
};
