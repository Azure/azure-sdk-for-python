import { cloneList } from './_internals/cloneList.js'
import { isArray } from './_internals/isArray.js'
import { isInteger } from './_internals/isInteger.js'
import { assoc } from './assoc.js'
import { curry } from './curry.js'

function assocPathFn(
  path, newValue, input
){
  const pathArrValue =
    typeof path === 'string' ?
      path.split('.').map(x => isInteger(Number(x)) ? Number(x) : x) :
      path
  if (pathArrValue.length === 0){
    return newValue
  }

  const index = pathArrValue[ 0 ]
  if (pathArrValue.length > 1){
    const condition =
      typeof input !== 'object' ||
      input === null ||
      !input.hasOwnProperty(index)

    const nextInput = condition ?
      isInteger(pathArrValue[ 1 ]) ?
        [] :
        {} :
      input[ index ]

    newValue = assocPathFn(
      Array.prototype.slice.call(pathArrValue, 1),
      newValue,
      nextInput
    )
  }

  if (isInteger(index) && isArray(input)){
    const arr = cloneList(input)
    arr[ index ] = newValue

    return arr
  }

  return assoc(
    index, newValue, input
  )
}

export const assocPath = curry(assocPathFn)
