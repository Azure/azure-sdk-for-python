function _curryN(
  n, cache, fn
){
  return function (){
    let ci = 0
    let ai = 0
    const cl = cache.length
    const al = arguments.length
    const args = new Array(cl + al)
    while (ci < cl){
      args[ ci ] = cache[ ci ]
      ci++
    }
    while (ai < al){
      args[ cl + ai ] = arguments[ ai ]
      ai++
    }
    const remaining = n - args.length

    return args.length >= n ?
      fn.apply(this, args) :
      _arity(remaining, _curryN(
        n, args, fn
      ))
  }
}

function _arity(n, fn){
  switch (n){
  case 0:
    return function (){
      return fn.apply(this, arguments)
    }
  case 1:
    return function (_1){
      return fn.apply(this, arguments)
    }
  case 2:
    return function (_1, _2){
      return fn.apply(this, arguments)
    }
  case 3:
    return function (
      _1, _2, _3
    ){
      return fn.apply(this, arguments)
    }
  case 4:
    return function (
      _1, _2, _3, _4
    ){
      return fn.apply(this, arguments)
    }
  case 5:
    return function (
      _1, _2, _3, _4, _5
    ){
      return fn.apply(this, arguments)
    }
  case 6:
    return function (
      _1, _2, _3, _4, _5, _6
    ){
      return fn.apply(this, arguments)
    }
  case 7:
    return function (
      _1, _2, _3, _4, _5, _6, _7
    ){
      return fn.apply(this, arguments)
    }
  case 8:
    return function (
      _1, _2, _3, _4, _5, _6, _7, _8
    ){
      return fn.apply(this, arguments)
    }
  case 9:
    return function (
      _1, _2, _3, _4, _5, _6, _7, _8, _9
    ){
      return fn.apply(this, arguments)
    }
  default:
    return function (
      _1, _2, _3, _4, _5, _6, _7, _8, _9, _10
    ){
      return fn.apply(this, arguments)
    }
  }
}

export function curryN(n, fn){
  if (arguments.length === 1) return _fn => curryN(n, _fn)

  if (n > 10){
    throw new Error('First argument to _arity must be a non-negative integer no greater than ten')
  }

  return _arity(n, _curryN(
    n, [], fn
  ))
}
