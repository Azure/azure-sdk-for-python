import { isArray } from './_internals/isArray.js'
import { type } from './type.js'

export function _lastIndexOf(valueToFind, list){
  if (!isArray(list)){
    throw new Error(`Cannot read property 'indexOf' of ${ list }`)
  }
  const typeOfValue = type(valueToFind)
  if (![ 'Object', 'Array', 'NaN', 'RegExp' ].includes(typeOfValue))
    return list.lastIndexOf(valueToFind)

  const { length } = list
  let index = length
  let foundIndex = -1

  while (--index > -1 && foundIndex === -1){
    if (equals(list[ index ], valueToFind)){
      foundIndex = index
    }
  }

  return foundIndex
}

export function _indexOf(valueToFind, list){
  if (!isArray(list)){
    throw new Error(`Cannot read property 'indexOf' of ${ list }`)
  }
  const typeOfValue = type(valueToFind)
  if (![ 'Object', 'Array', 'NaN', 'RegExp' ].includes(typeOfValue))
    return list.indexOf(valueToFind)

  let index = -1
  let foundIndex = -1
  const { length } = list

  while (++index < length && foundIndex === -1){
    if (equals(list[ index ], valueToFind)){
      foundIndex = index
    }
  }

  return foundIndex
}

function _arrayFromIterator(iter){
  const list = []
  let next
  while (!(next = iter.next()).done){
    list.push(next.value)
  }

  return list
}

function _equalsSets(a, b){
  if (a.size !== b.size){
    return false
  }
  const aList = _arrayFromIterator(a.values())
  const bList = _arrayFromIterator(b.values())

  const filtered = aList.filter(aInstance => _indexOf(aInstance, bList) === -1)

  return filtered.length === 0
}

function parseError(maybeError){
  const typeofError = maybeError.__proto__.toString()
  if (![ 'Error', 'TypeError' ].includes(typeofError)) return []

  return [ typeofError, maybeError.message ]
}

function parseDate(maybeDate){
  if (!maybeDate.toDateString) return [ false ]

  return [ true, maybeDate.getTime() ]
}

function parseRegex(maybeRegex){
  if (maybeRegex.constructor !== RegExp) return [ false ]

  return [ true, maybeRegex.toString() ]
}

export function equals(a, b){
  if (arguments.length === 1) return _b => equals(a, _b)

  const aType = type(a)

  if (aType !== type(b)) return false
  if (aType === 'Function'){
    return a.name === undefined ? false : a.name === b.name
  }

  if ([ 'NaN', 'Undefined', 'Null' ].includes(aType)) return true

  if (aType === 'Number'){
    if (Object.is(-0, a) !== Object.is(-0, b)) return false

    return a.toString() === b.toString()
  }

  if ([ 'String', 'Boolean' ].includes(aType)){
    return a.toString() === b.toString()
  }

  if (aType === 'Array'){
    const aClone = Array.from(a)
    const bClone = Array.from(b)

    if (aClone.toString() !== bClone.toString()){
      return false
    }

    let loopArrayFlag = true
    aClone.forEach((aCloneInstance, aCloneIndex) => {
      if (loopArrayFlag){
        if (
          aCloneInstance !== bClone[ aCloneIndex ] &&
          !equals(aCloneInstance, bClone[ aCloneIndex ])
        ){
          loopArrayFlag = false
        }
      }
    })

    return loopArrayFlag
  }

  const aRegex = parseRegex(a)
  const bRegex = parseRegex(b)

  if (aRegex[ 0 ]){
    return bRegex[ 0 ] ? aRegex[ 1 ] === bRegex[ 1 ] : false
  } else if (bRegex[ 0 ]) return false

  const aDate = parseDate(a)
  const bDate = parseDate(b)

  if (aDate[ 0 ]){
    return bDate[ 0 ] ? aDate[ 1 ] === bDate[ 1 ] : false
  } else if (bDate[ 0 ]) return false

  const aError = parseError(a)
  const bError = parseError(b)

  if (aError[ 0 ]){
    return bError[ 0 ] ?
      aError[ 0 ] === bError[ 0 ] && aError[ 1 ] === bError[ 1 ] :
      false
  }
  if (aType === 'Set'){
    return _equalsSets(a, b)
  }
  if (aType === 'Object'){
    const aKeys = Object.keys(a)

    if (aKeys.length !== Object.keys(b).length){
      return false
    }

    let loopObjectFlag = true
    aKeys.forEach(aKeyInstance => {
      if (loopObjectFlag){
        const aValue = a[ aKeyInstance ]
        const bValue = b[ aKeyInstance ]

        if (aValue !== bValue && !equals(aValue, bValue)){
          loopObjectFlag = false
        }
      }
    })

    return loopObjectFlag
  }

  return false
}
