import { isArray } from './_internals/isArray.js'
import { keys } from './_internals/keys.js'

export function forEach(fn, list){
  if (arguments.length === 1) return _list => forEach(fn, _list)

  if (list === undefined){
    return
  }

  if (isArray(list)){
    let index = 0
    const len = list.length

    while (index < len){
      fn(list[ index ])
      index++
    }
  } else {
    let index = 0
    const listKeys = keys(list)
    const len = listKeys.length

    while (index < len){
      const key = listKeys[ index ]
      fn(
        list[ key ], key, list
      )
      index++
    }
  }

  return list
}
