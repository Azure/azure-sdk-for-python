export function createPath(path, delimiter = '.'){
  return typeof path === 'string' ? path.split(delimiter) : path
}
