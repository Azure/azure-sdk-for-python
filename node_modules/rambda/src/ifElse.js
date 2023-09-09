import { curry } from './curry.js'

function ifElseFn(
  condition, onTrue, onFalse
){
  return (...input) => {
    const conditionResult =
      typeof condition === 'boolean' ? condition : condition(...input)

    if (conditionResult === true){
      return onTrue(...input)
    }

    return onFalse(...input)
  }
}

export const ifElse = curry(ifElseFn)
