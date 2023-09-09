'use strict';

/**
 * @fileoverview Limit the number of top-level suites in a single file
 * @author Alexander Afanasyev
 */

const { isNil } = require('rambda');
const createAstUtils = require('../util/ast');

const defaultSuiteLimit = 1;

function isTopLevelScope(scope) {
    return scope.type === 'module' || scope.upper === null;
}

module.exports = {
    meta: {
        type: 'suggestion',
        docs: {
            description: 'Limit the number of top-level suites in a single file',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/max-top-level-suites.md'
        },
        schema: [
            {
                type: 'object',
                properties: {
                    limit: {
                        type: 'integer'
                    }
                },
                additionalProperties: false
            }
        ]
    },
    create(context) {
        const astUtils = createAstUtils(context.settings);
        const topLevelDescribes = [];
        const options = context.options[0] || {};
        let suiteLimit;

        if (isNil(options.limit)) {
            suiteLimit = defaultSuiteLimit;
        } else {
            suiteLimit = options.limit;
        }

        return {
            CallExpression(node) {
                if (astUtils.isDescribe(node)) {
                    const scope = context.getScope();

                    if (isTopLevelScope(scope)) {
                        topLevelDescribes.push(node);
                    }
                }
            },

            'Program:exit'() {
                if (topLevelDescribes.length > suiteLimit) {
                    context.report({
                        node: topLevelDescribes[suiteLimit],
                        message: `The number of top-level suites is more than ${ suiteLimit }.`
                    });
                }
            }
        };
    }
};
