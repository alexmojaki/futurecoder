// import * as Sentry from "@sentry/react";  // FIXME(hangtwenty): Put back Sentry

export function wrapAsync(func, name) {
  return async function () {
    try {
      return await func(...arguments);
    } catch (e) {
      // FIXME(hangtwenty): Put back Sentry
      // Sentry.setExtra(`${name || func.name || 'anon'}_arguments`, [...arguments]);
      throw e;
    }
  }
}
