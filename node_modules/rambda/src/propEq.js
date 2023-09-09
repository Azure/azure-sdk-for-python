import { curry } from './curry.js'
import { equals } from './equals.js'
import { prop } from './prop.js'

function propEqFn(
  propToFind, valueToMatch, obj
){
  if (!obj) return false

  return equals(valueToMatch, prop(propToFind, obj))
}

export const propEq = curry(propEqFn)
