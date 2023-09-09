'use strict';

const createAstUtils = require('../util/ast');

function newDescribeLayer(describeNode) {
    return {
        describeNode,
        before: false,
        after: false,
        beforeEach: false,
        afterEach: false
    };
}

module.exports = {
    meta: {
        type: 'suggestion',
        docs: {
            description: 'Disallow duplicate uses of a hook at the same level inside a describe',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/no-sibling-hooks.md'
        },
        schema: []
    },
    create(context) {
        const isUsed = [];
        const astUtils = createAstUtils(context.settings);

        return {
            Program(node) {
                isUsed.push(newDescribeLayer(node));
            },

            CallExpression(node) {
                const name = astUtils.getNodeName(node.callee);

                if (astUtils.isDescribe(node)) {
                    isUsed.push(newDescribeLayer(node));
                    return;
                }

                if (!astUtils.isHookIdentifier(node.callee)) {
                    return;
                }

                if (isUsed[isUsed.length - 1][name]) {
                    context.report({
                        node: node.callee,
                        message: `Unexpected use of duplicate Mocha \`${ name }\` hook`
                    });
                }

                isUsed[isUsed.length - 1][name] = true;
            },

            'CallExpression:exit'(node) {
                if (isUsed[isUsed.length - 1].describeNode === node) {
                    isUsed.pop();
                }
            }
        };
    }
};
