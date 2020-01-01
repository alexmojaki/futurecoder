/* Helper to determine type */
export const isNumber = value => typeof value === "number";
export const isString = value => typeof value === "string";
export const isFunction = value => typeof value === "function";

/* Basic assert statement */
export const assert = (condition, message) => {
  if (!condition) {
    throw new Error(message || "Assertion failed");
  }
};

/* Checks an array has only one element and returns it */
export const only = arr => {
  assert(arr.length === 1, `Expected 1 element, found ${arr.length}`);
  return arr[0];
};

/* converts a slug into text */
export const unslug = text => text.replace(/_/g, " ");
