'use strict';
const isValueNotUsable = require('./utils/is-value-not-usable.js');
const {methodCallSelector} = require('./selectors/index.js');

const messages = {
	replaceChildOrInsertBefore:
		'Prefer `{{oldChildNode}}.{{preferredMethod}}({{newChildNode}})` over `{{parentNode}}.{{method}}({{newChildNode}}, {{oldChildNode}})`.',
	insertAdjacentTextOrInsertAdjacentElement:
		'Prefer `{{reference}}.{{preferredMethod}}({{content}})` over `{{reference}}.{{method}}({{position}}, {{content}})`.',
};

const replaceChildOrInsertBeforeSelector = [
	methodCallSelector({
		methods: ['replaceChild', 'insertBefore'],
		argumentsLength: 2,
	}),
	// We only allow Identifier for now
	'[arguments.0.type="Identifier"]',
	'[arguments.0.name!="undefined"]',
	'[arguments.1.type="Identifier"]',
	'[arguments.1.name!="undefined"]',
	// This check makes sure that only the first method of chained methods with same identifier name e.g: parentNode.insertBefore(alfa, beta).insertBefore(charlie, delta); gets reported
	'[callee.object.type="Identifier"]',
].join('');

const disallowedMethods = new Map([
	['replaceChild', 'replaceWith'],
	['insertBefore', 'before'],
]);

const checkForReplaceChildOrInsertBefore = (context, node) => {
	const method = node.callee.property.name;
	const parentNode = node.callee.object.name;
	const [newChildNode, oldChildNode] = node.arguments.map(({name}) => name);
	const preferredMethod = disallowedMethods.get(method);

	const fix = isValueNotUsable(node)
		? fixer => fixer.replaceText(
			node,
			`${oldChildNode}.${preferredMethod}(${newChildNode})`,
		)
		: undefined;

	return {
		node,
		messageId: 'replaceChildOrInsertBefore',
		data: {
			parentNode,
			method,
			preferredMethod,
			newChildNode,
			oldChildNode,
		},
		fix,
	};
};

const insertAdjacentTextOrInsertAdjacentElementSelector = [
	methodCallSelector({
		methods: ['insertAdjacentText', 'insertAdjacentElement'],
		argumentsLength: 2,
	}),
	// Position argument should be `string`
	'[arguments.0.type="Literal"]',
	// TODO: remove this limits on second argument
	':matches([arguments.1.type="Literal"], [arguments.1.type="Identifier"])',
	// TODO: remove this limits on callee
	'[callee.object.type="Identifier"]',
].join('');

const positionReplacers = new Map([
	['beforebegin', 'before'],
	['afterbegin', 'prepend'],
	['beforeend', 'append'],
	['afterend', 'after'],
]);

const checkForInsertAdjacentTextOrInsertAdjacentElement = (context, node) => {
	const method = node.callee.property.name;
	const [positionNode, contentNode] = node.arguments;

	const position = positionNode.value;
	// Return early when specified position value of first argument is not a recognized value.
	if (!positionReplacers.has(position)) {
		return;
	}

	const preferredMethod = positionReplacers.get(position);
	const content = context.getSource(contentNode);
	const reference = context.getSource(node.callee.object);

	const fix = method === 'insertAdjacentElement' && !isValueNotUsable(node)
		? undefined
		// TODO: make a better fix, don't touch reference
		: fixer => fixer.replaceText(
			node,
			`${reference}.${preferredMethod}(${content})`,
		);

	return {
		node,
		messageId: 'insertAdjacentTextOrInsertAdjacentElement',
		data: {
			reference,
			method,
			preferredMethod,
			position: context.getSource(positionNode),
			content,
		},
		fix,
	};
};

/** @param {import('eslint').Rule.RuleContext} context */
const create = context => ({
	[replaceChildOrInsertBeforeSelector](node) {
		return checkForReplaceChildOrInsertBefore(context, node);
	},
	[insertAdjacentTextOrInsertAdjacentElementSelector](node) {
		return checkForInsertAdjacentTextOrInsertAdjacentElement(context, node);
	},
});

/** @type {import('eslint').Rule.RuleModule} */
module.exports = {
	create,
	meta: {
		type: 'suggestion',
		docs: {
			description: 'Prefer `.before()` over `.insertBefore()`, `.replaceWith()` over `.replaceChild()`, prefer one of `.before()`, `.after()`, `.append()` or `.prepend()` over `insertAdjacentText()` and `insertAdjacentElement()`.',
		},
		fixable: 'code',
		messages,
	},
};
