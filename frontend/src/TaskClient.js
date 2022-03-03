// eslint-disable-next-line import/no-webpack-loader-syntax
import Worker from "worker-loader!./Worker.js";
import {makeChannel} from "sync-message";
import {InterruptError, TaskClient} from "./comsync";
import * as Comlink from 'comlink';

const channel = makeChannel({serviceWorker: {scope: "/course/"}});
if (channel?.type === "serviceWorker") {
  navigator.serviceWorker.register("/course/service-worker.js");
}

export const taskClient = new TaskClient(() => new Worker(), channel);

export async function runCodeTask(entry, outputCallback, inputCallback) {
  let interruptBuffer = null;
  if (typeof SharedArrayBuffer !== "undefined") {
    interruptBuffer = new Int32Array(new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 1));
    taskClient.interrupter = () => {
      interruptBuffer[0] = 2;
    }
  }

  let running = true;

  function wrappedOutputCallback(...args) {
    if (running) {
      outputCallback(...args);
    }
  }

  try {
    return await taskClient.runTask(
      "runCode",
      interruptBuffer,
      entry,
      Comlink.proxy(wrappedOutputCallback),
      Comlink.proxy(inputCallback),
    );
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
  } finally {
    running = false;
  }
}
