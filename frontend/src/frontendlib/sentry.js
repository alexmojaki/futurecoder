import * as Sentry from "@sentry/react";

export function wrapAsync(func, name) {
  return async function() {
    try {
      return await func(...arguments);
    } catch (e) {
      Sentry.setExtra(`${name || func.name || 'anon'}_arguments`, [...arguments]);
      throw e;
    }
  }
}
