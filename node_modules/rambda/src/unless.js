export function unless(predicate, whenFalse){
  if (arguments.length === 1){
    return _whenFalse => unless(predicate, _whenFalse)
  }

  return input => predicate(input) ? input : whenFalse(input)
}
