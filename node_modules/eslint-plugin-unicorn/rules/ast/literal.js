'use strict';

function isLiteral(node, value) {
	if (node?.type !== 'Literal') {
		return false;
	}

	if (value === null) {
		return node.raw === 'null';
	}

	return node.value === value;
}

const isStringLiteral = node => node?.type === 'Literal' && typeof node.value === 'string';
const isNumberLiteral = node => node.type === 'Literal' && typeof node.value === 'number';
const isRegexLiteral = node => node.type === 'Literal' && Boolean(node.regex);
// eslint-disable-next-line unicorn/no-null
const isNullLiteral = node => isLiteral(node, null);
const isBigIntLiteral = node => node.type === 'Literal' && Boolean(node.bigint);

module.exports = {
	isLiteral,
	isStringLiteral,
	isNumberLiteral,
	isBigIntLiteral,
	isNullLiteral,
	isRegexLiteral,
};
