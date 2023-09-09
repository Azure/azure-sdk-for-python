import { type } from './type.js'

export function isPromise(x){
  return 'Promise' === type(x)
}
