/* These very simple helper should hopefully make using redux easier without having 
 * to add dependencies any complex libraries like Immutable.js
 * 
 * It exports two functions to make updating nested structures much easier, pretty 
 * much all other tasks can be achieved with normal JS syntax. The main problem is 
 * that object literals are just shit, and we want to keep very light syntax.
 * 
 * This needs testing but it is very simple code.
 * */

/* Check if something is an Array */
export const isObject = thing => thing !== null && typeof thing === "object";

/* Check if something is an Object */
export const isArray = thing => Array.isArray(thing);

/* Given a nested data structure this will follow the path, and replace
 * the item at the end of the path with the result of calling the updateFn on it.
 * */
export const iupdate = (root, path, updateFn) => {
  if (!isArray(path)) {
    path = path.split('.');
  }

  if (path.length === 0) return updateFn(root);

  const [head, ...tail] = path;

  let newRoot;
  if (isArray(root)) {
    newRoot = [...root];
  } else if (isObject(root)) {
    newRoot = { ...root };
  } else {
    throw new Error(`${root} is not an Array or Object, check your path`);
  }

  if (tail.length === 0) {
    newRoot[head] = updateFn(root[head]);
  } else {
    newRoot[head] = iupdate(root[head], tail, updateFn);
  }

  return newRoot;
};

/* Given a nested data structure this will follow the path, and replace
 *  the item at the end of the path with the value.
 */
export const iset = (root, path, value) => iupdate(root, path, () => value);

/* Given a nested data structure this will follow the path, and add the 
 * given value to the end of the array at that path.
 */
export const ipush = (root, path, value) =>
  iupdate(root, path, list => list.concat([value]));

/* Given a nested data structure this will follow the path, and remove the 
 * given idex in the array at that path
 */
export const iremove = (root, path, index) =>
  iupdate(root, path, list => [
    ...list.slice(0, index),
    ...list.slice(index + 1)
  ]);
