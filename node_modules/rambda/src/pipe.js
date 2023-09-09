import { reduceFn } from './reduce.js'

export function _arity(n, fn){
  switch (n){
  case 0:
    return function (){
      return fn.apply(this, arguments)
    }
  case 1:
    return function (a0){
      return fn.apply(this, arguments)
    }
  case 2:
    return function (a0, a1){
      return fn.apply(this, arguments)
    }
  case 3:
    return function (
      a0, a1, a2
    ){
      return fn.apply(this, arguments)
    }
  case 4:
    return function (
      a0, a1, a2, a3
    ){
      return fn.apply(this, arguments)
    }
  case 5:
    return function (
      a0, a1, a2, a3, a4
    ){
      return fn.apply(this, arguments)
    }
  case 6:
    return function (
      a0, a1, a2, a3, a4, a5
    ){
      return fn.apply(this, arguments)
    }
  case 7:
    return function (
      a0, a1, a2, a3, a4, a5, a6
    ){
      return fn.apply(this, arguments)
    }
  case 8:
    return function (
      a0, a1, a2, a3, a4, a5, a6, a7
    ){
      return fn.apply(this, arguments)
    }
  case 9:
    return function (
      a0, a1, a2, a3, a4, a5, a6, a7, a8
    ){
      return fn.apply(this, arguments)
    }
  case 10:
    return function (
      a0, a1, a2, a3, a4, a5, a6, a7, a8, a9
    ){
      return fn.apply(this, arguments)
    }
  default:
    throw new Error('First argument to _arity must be a non-negative integer no greater than ten')
  }
}

export function _pipe(f, g){
  return function (){
    return g.call(this, f.apply(this, arguments))
  }
}

export function pipe(){
  if (arguments.length === 0){
    throw new Error('pipe requires at least one argument')
  }

  return _arity(arguments[ 0 ].length,
    reduceFn(
      _pipe,
      arguments[ 0 ],
      Array.prototype.slice.call(
        arguments, 1, Infinity
      )
    ))
}
