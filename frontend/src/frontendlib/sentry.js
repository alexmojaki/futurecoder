import * as Sentry from "@sentry/react";

export function wrapAsync(func) {
  return async function() {
    try {
      return await func(...arguments);
    } catch (e) {
      Sentry.setExtra(`${func.name || 'anon'}_arguments`, [...arguments]);
      throw e;
    }
  }
}
