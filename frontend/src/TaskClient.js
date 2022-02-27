// noinspection ES6CheckImport
// eslint-disable-next-line import/no-webpack-loader-syntax
import Worker from "worker-loader!./Worker.js";
import {makeChannel} from "sync-message";
import {InterruptError, TaskClient} from "./comsync";

const channel = makeChannel({serviceWorker: {scope: "/course/"}});
if (channel?.type === "serviceWorker") {
  navigator.serviceWorker.register("./service-worker.js");
}

export const taskClient = new TaskClient(() => new Worker(), channel);

export async function runCodeTask(...args) {
  let interruptBuffer = null;
  if (typeof SharedArrayBuffer !== "undefined") {
    interruptBuffer = new Int32Array(new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 1));
    taskClient.interrupter = () => {
      interruptBuffer[0] = 2;
    }
  }

  try {
    return await taskClient.runTask("runCode", interruptBuffer, ...args);
  } catch (e) {
    if (e instanceof InterruptError) {
      return {
        interrupted: true,
        error: null,
        passed: false,
        messages: [],
      }
    }
    throw e;
  }
}
