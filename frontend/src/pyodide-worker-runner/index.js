/* eslint-disable */
// Otherwise webpack fails silently
// https://github.com/facebook/create-react-app/issues/8014

import {ServiceWorkerError} from "sync-message";
import pRetry from 'p-retry';
import {exposeSync, InterruptError, NoChannelError, TaskClient} from "../comsync";
import {loadPyodide} from 'pyodide/pyodide.js';
import * as Comlink from 'comlink';
import pyodide_worker_runner_contents from "!!raw-loader!./pyodide_worker_runner.py"
import {taskClient} from "../TaskClient";

export async function loadPyodideAndPackage(packageOptions) {
  const {format, extract_dir, url} = packageOptions;

  // const indexURL = 'https://cdn.jsdelivr.net/pyodide/v0.19.0/full/';
  // importScripts(indexURL + 'pyodide.js');

  const [pyodide, packageBuffer] = (await Promise.all([
    loadPyodide({indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.19.0/full/'}),
    pRetry(() => getPackageBuffer(url), {retries: 3}),
  ]));

  pyodide.unpackArchive(packageBuffer, format, extract_dir);

  if (extract_dir) {
    const sys = pyodide.pyimport("sys");
    sys.path.append(extract_dir);
  }

  initPyodide(pyodide);

  return pyodide;
}

function initPyodide(pyodide) {
  pyodide.registerComlink(Comlink);

  const sys = pyodide.pyimport("sys");
  const pathlib = pyodide.pyimport("pathlib");

  const dirPath = "/tmp/pyodide_worker_runner/";
  sys.path.append(dirPath);
  pathlib.Path(dirPath + "pyodide_worker_runner.py").write_text(pyodide_worker_runner_contents);
  pyodide.pyimport("pyodide_worker_runner");
}

async function getPackageBuffer(url) {
  const response = await fetch(url);
  if (!response.ok) {
    throw `Request for package failed with status ${response.status}: ${response.statusText}`
  }
  return await response.arrayBuffer()
}

export function toObject(x) {
  if (x?.toJs) {
    x = x.toJs();
  }
  if (x instanceof Map) {
    return Object.fromEntries(Array.from(
      x.entries(),
      ([k, v]) => [k, toObject(v)]
    ))
  } else if (x instanceof Array) {
    return x.map(toObject);
  } else {
    return x;
  }
}

export function makeRunnerCallback(comsyncExtras, callbacks) {
  return function (data) {
    data = toObject(data);
    if (data.type === "input") {
      callbacks.input?.(data.prompt);
      try {
        return comsyncExtras.readMessage() + "\n";
      } catch (e) {
        if (e instanceof InterruptError) {
          return 1;  // raise KeyboardInterrupt
        } else if (e instanceof ServiceWorkerError) {
          return 2;  // suggesting closing all tabs and reopening
        } else if (e instanceof NoChannelError) {
          return 3;  // browser not supported
        }
        throw e;
      }
    } else if (data.type === "sleep") {
      try {
        comsyncExtras.syncSleep(data.seconds * 1000);
      } catch (e) {
        console.error(e);
      }
    } else {
      callbacks[data.type](data);
    }
  }
}

export function exposePyodide(pyodidePromise, func) {
  return exposeSync(async function (comsyncExtras, interruptBuffer, ...args) {
    const pyodide = await pyodidePromise;

    if (interruptBuffer) {
      pyodide.setInterruptBuffer(interruptBuffer);
    }

    return func(comsyncExtras, pyodide, ...args);
  });
}

export class PyodideTaskClient extends TaskClient {
  async runTask(funcName, ...args) {
    let interruptBuffer = null;
    if (typeof SharedArrayBuffer !== "undefined") {
      interruptBuffer = new Int32Array(new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 1));
      taskClient.interrupter = () => {
        interruptBuffer[0] = 2;
      }
    }

    return super.runTask(funcName, interruptBuffer, ...args);
  }
}
