export function partial(fn, ...args){
  const len = fn.length

  return (...rest) => {
    if (args.length + rest.length >= len){
      return fn(...args, ...rest)
    }

    return partial(fn, ...[ ...args, ...rest ])
  }
}
