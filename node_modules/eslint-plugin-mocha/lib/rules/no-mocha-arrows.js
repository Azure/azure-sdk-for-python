'use strict';

/**
 * @fileoverview Disallow arrow functions as arguments to Mocha globals
 * @author Paul Melnikow
 */

const createAstUtils = require('../util/ast');

function extractSourceTextByRange(sourceCode, start, end) {
    return sourceCode.text.slice(start, end).trim();
}

// eslint-disable-next-line max-statements
function formatFunctionHead(sourceCode, fn) {
    const arrow = sourceCode.getTokenBefore(fn.body);
    const beforeArrowToken = sourceCode.getTokenBefore(arrow);
    let firstToken = sourceCode.getFirstToken(fn);

    let functionKeyword = 'function';
    let params = extractSourceTextByRange(
        sourceCode,
        firstToken.range[0],
        beforeArrowToken.range[1]
    );
    if (fn.async) {
        // When 'async' specified strip the token from the params text
        // and prepend it to the function keyword
        params = params.slice(firstToken.range[1] - firstToken.range[0]).trim();
        functionKeyword = 'async function';

        // Advance firstToken pointer
        firstToken = sourceCode.getTokenAfter(firstToken);
    }

    const beforeArrowComment = extractSourceTextByRange(
        sourceCode,
        beforeArrowToken.range[1],
        arrow.range[0]
    );
    const afterArrowComment = extractSourceTextByRange(
        sourceCode,
        arrow.range[1],
        fn.body.range[0]
    );
    let paramsFullText;
    if (firstToken.type !== 'Punctuator') {
        paramsFullText = `(${params}${beforeArrowComment})${afterArrowComment}`;
    } else {
        paramsFullText = `${params}${beforeArrowComment}${afterArrowComment}`;
    }

    return `${functionKeyword}${paramsFullText} `;
}

function fixArrowFunction(fixer, sourceCode, fn) {
    if (fn.body.type === 'BlockStatement') {
        // When it((...) => { ... }),
        // simply replace '(...) => ' with 'function () '
        return fixer.replaceTextRange(
            [ fn.range[0], fn.body.range[0] ],
            formatFunctionHead(sourceCode, fn)
        );
    }

    const bodyText = sourceCode.getText(fn.body);
    return fixer.replaceTextRange(
        fn.range,
        `${formatFunctionHead(sourceCode, fn)}{ return ${bodyText}; }`
    );
}

module.exports = {
    meta: {
        type: 'suggestion',
        docs: {
            description:
                'Disallow arrow functions as arguments to mocha functions',
            url: 'https://github.com/lo1tuma/eslint-plugin-mocha/blob/master/docs/rules/no-mocha-arrows.md'
        },
        fixable: 'code',
        schema: []
    },
    create(context) {
        const astUtils = createAstUtils(context.settings);
        const sourceCode = context.getSourceCode();
        const isTestCase = astUtils.buildIsTestCaseAnswerer();
        const isDescribe = astUtils.buildIsDescribeAnswerer();
        const isMochaFunctionCall = astUtils.buildIsMochaFunctionCallAnswerer(
            isTestCase,
            isDescribe
        );

        return {
            CallExpression(node) {
                if (isMochaFunctionCall(node, context)) {
                    const amountOfArguments = node.arguments.length;

                    if (amountOfArguments > 0) {
                        const lastArgument =
                            node.arguments[amountOfArguments - 1];

                        if (lastArgument.type === 'ArrowFunctionExpression') {
                            const name = astUtils.getNodeName(node.callee);
                            context.report({
                                node,
                                message: `Do not pass arrow functions to ${name}()`,
                                fix(fixer) {
                                    return fixArrowFunction(
                                        fixer,
                                        sourceCode,
                                        lastArgument
                                    );
                                }
                            });
                        }
                    }
                }
            }
        };
    }
};
