// eslint-disable-next-line import/no-webpack-loader-syntax
import Worker from "worker-loader!./Worker.js";
import {makeChannel} from "sync-message";
import * as Comlink from 'comlink';
import {PyodideClient} from "pyodide-worker-runner";

const channel = makeChannel({serviceWorker: {scope: "/course/"}});
if (channel?.type === "serviceWorker") {
  navigator.serviceWorker.register("/course/service-worker.js");
}

export const taskClient = new PyodideClient(() => new Worker(), channel);

export async function runCodeTask(entry, outputCallback, inputCallback) {
  let running = true;

  function wrappedOutputCallback(...args) {
    if (running) {
      outputCallback(...args);
    }
  }

  try {
    return await taskClient.call(
      taskClient.workerProxy.runCode,
      entry,
      Comlink.proxy(wrappedOutputCallback),
      Comlink.proxy(inputCallback),
    );
  } catch (e) {
    if (e.type === "InterruptError") {
      return {
        interrupted: true,
        error: null,
        passed: false,
        messages: [],
      }
    }
    throw e;
  } finally {
    running = false;
  }
}
