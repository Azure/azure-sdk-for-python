export function cond(conditions){
  return input => {
    let done = false
    let toReturn
    conditions.forEach(([ predicate, resultClosure ]) => {
      if (!done && predicate(input)){
        done = true
        toReturn = resultClosure(input)
      }
    })

    return toReturn
  }
}
