export function prop(propToFind, obj){
  if (arguments.length === 1) return _obj => prop(propToFind, _obj)

  if (!obj) return undefined

  return obj[ propToFind ]
}
