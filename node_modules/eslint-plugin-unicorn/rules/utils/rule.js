'use strict';
const path = require('node:path');
const fs = require('node:fs');
const getDocumentationUrl = require('./get-documentation-url.js');

const isIterable = object => typeof object?.[Symbol.iterator] === 'function';

class FixAbortError extends Error {}
const fixOptions = {
	abort() {
		throw new FixAbortError('Fix aborted.');
	},
};

function wrapFixFunction(fix) {
	return fixer => {
		const result = fix(fixer, fixOptions);

		if (isIterable(result)) {
			try {
				return [...result];
			} catch (error) {
				if (error instanceof FixAbortError) {
					return;
				}

				/* c8 ignore next */
				throw error;
			}
		}

		return result;
	};
}

function reportListenerProblems(listener, context) {
	// Listener arguments can be `codePath, node` or `node`
	return function (...listenerArguments) {
		let problems = listener(...listenerArguments);

		if (!problems) {
			return;
		}

		if (!isIterable(problems)) {
			problems = [problems];
		}

		for (const problem of problems) {
			if (problem.fix) {
				problem.fix = wrapFixFunction(problem.fix);
			}

			if (Array.isArray(problem.suggest)) {
				for (const suggest of problem.suggest) {
					if (suggest.fix) {
						suggest.fix = wrapFixFunction(suggest.fix);
					}

					suggest.data = {
						...problem.data,
						...suggest.data,
					};
				}
			}

			context.report(problem);
		}
	};
}

// `checkVueTemplate` function will wrap `create` function, there is no need to wrap twice
const wrappedFunctions = new Set();
function reportProblems(create) {
	if (wrappedFunctions.has(create)) {
		return create;
	}

	const wrapped = context => {
		const listeners = create(context);

		if (!listeners) {
			return {};
		}

		return Object.fromEntries(
			Object.entries(listeners)
				.map(([selector, listener]) => [selector, reportListenerProblems(listener, context)]),
		);
	};

	wrappedFunctions.add(wrapped);

	return wrapped;
}

function checkVueTemplate(create, options) {
	const {
		visitScriptBlock,
	} = {
		visitScriptBlock: true,
		...options,
	};

	create = reportProblems(create);

	const wrapped = context => {
		const listeners = create(context);

		// `vue-eslint-parser`
		if (context.parserServices?.defineTemplateBodyVisitor) {
			return visitScriptBlock
				? context.parserServices.defineTemplateBodyVisitor(listeners, listeners)
				: context.parserServices.defineTemplateBodyVisitor(listeners);
		}

		return listeners;
	};

	wrappedFunctions.add(wrapped);
	return wrapped;
}

/** @returns {import('eslint').Rule.RuleModule} */
function loadRule(ruleId) {
	const rule = require(`../${ruleId}`);

	return {
		meta: {
			// If there is are, options add `[]` so ESLint can validate that no data is passed to the rule.
			// https://github.com/not-an-aardvark/eslint-plugin-eslint-plugin/blob/master/docs/rules/require-meta-schema.md
			schema: [],
			...rule.meta,
			docs: {
				...rule.meta.docs,
				url: getDocumentationUrl(ruleId),
			},
		},
		create: reportProblems(rule.create),
	};
}

function loadRules() {
	return Object.fromEntries(
		fs.readdirSync(path.join(__dirname, '..'), {withFileTypes: true})
			.filter(file => file.isFile())
			.map(file => {
				const ruleId = path.basename(file.name, '.js');
				return [ruleId, loadRule(ruleId)];
			}),
	);
}

module.exports = {
	loadRule,
	loadRules,
	checkVueTemplate,
};
