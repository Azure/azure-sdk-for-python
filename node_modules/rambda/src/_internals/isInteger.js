function _isInteger(n){
  return n << 0 === n
}

export const isInteger = Number.isInteger || _isInteger
