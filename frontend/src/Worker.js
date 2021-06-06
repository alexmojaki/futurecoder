/* eslint-disable */
// Otherwise webpack fails silently
// https://github.com/facebook/create-react-app/issues/8014

import * as Comlink from 'comlink';
import pythonCoreUrl from "./python_core.tar"

async function getPackageBuffer() {
  const response = await fetch(pythonCoreUrl);
  if (!response.ok) {
    throw `Request for package failed with status ${response.status}: ${response.statusText}`
  }
  return await response.arrayBuffer()
}

async function loadPyodideOnly() {
  console.time("importScripts pyodide")
  importScripts('https://cdn.jsdelivr.net/pyodide/v0.17.0/full/pyodide.js');
  console.timeEnd("importScripts pyodide")

  console.time("loadPyodide")
  await loadPyodide({indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.17.0/full/'});
  console.timeEnd("loadPyodide")

  pyodide.runPython(`
import io
import tarfile
import sys

package_path = "/tmp/package/"
tarfile.TarFile.chown = lambda *_, **__: None

def load_package_buffer(buffer):
    global run_code_catch_errors
    fd = io.BytesIO(buffer.to_py())
    with tarfile.TarFile(fileobj=fd) as zf:
        zf.extractall(package_path)
    
    sys.path.append(package_path)
    
    from core.workers.worker import run_code_catch_errors  # noqa trigger imports
    print("Python core ready!")
`)
}


async function loadPyodideAndPackages() {
  const buffer = (await Promise.all([
    loadPyodideOnly(),
    getPackageBuffer(),
  ]))[1];

  console.time("load_package_buffer(buffer)")
  pyodide.globals.get("load_package_buffer")(buffer);
  console.timeEnd("load_package_buffer(buffer)")
}

let pyodideReadyPromise = loadPyodideAndPackages();

const toObject = (x) => {
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

const decoder = new TextDecoder();

class Runner {
  constructor(resultCallback) {
    this.resultCallback = resultCallback;
  }
  async runCode(entry, inputTextArray, inputMetaArray, interruptBuffer) {
    await pyodideReadyPromise;

    const inputCallback = () => {
      while (true) {
        if (Atomics.wait(inputMetaArray, 1, 0, 50) === "timed-out") {
          if (interruptBuffer[0] === 2) {
            return null;
          }
        } else {
          break
        }
      }
      Atomics.store(inputMetaArray, 1, 0);
      const size = Atomics.exchange(inputMetaArray, 0, 0);
      const bytes = inputTextArray.slice(0, size);
      return decoder.decode(bytes) + "\n";
    }

    pyodide.setInterruptBuffer(interruptBuffer);
    const runCodeCatchErrors = pyodide.globals.get("run_code_catch_errors");
    const resultCallbackToObject = (result) => this.resultCallback(toObject(result.toJs()));
    runCodeCatchErrors(entry, inputCallback, resultCallbackToObject)
  }
}

Comlink.expose(Runner);
