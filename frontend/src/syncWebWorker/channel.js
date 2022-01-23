import {makeAtomicsChannel, makeServiceWorkerChannel} from "./index";

export async function makeChannel() {
  if (typeof SharedArrayBuffer !== "undefined") {
    return makeAtomicsChannel();
  } else {
    await navigator.serviceWorker.register("./service-worker.js");
    const result = await makeServiceWorkerChannel({timeout: 1000});
    if (!result) {
      // TODO what if this doesn't work?
      window.location.reload();
    }
    return result;
  }
}
