/* eslint-disable */
// Otherwise webpack fails silently
// https://github.com/facebook/create-react-app/issues/8014

import * as Comlink from 'comlink';
import pythonCoreUrl from "./python_core.tar.load_by_url"
import loadPythonString from "!!raw-loader!./load.py"

async function getPackageBuffer() {
  const response = await fetch(pythonCoreUrl);
  if (!response.ok) {
    throw `Request for package failed with status ${response.status}: ${response.statusText}`
  }
  return await response.arrayBuffer()
}

let pyodide;

async function loadPyodideOnly() {
  console.time("importScripts pyodide")
  const indexURL = 'https://cdn.jsdelivr.net/pyodide/v0.18.0/full/';
  importScripts(indexURL + 'pyodide.js');
  console.timeEnd("importScripts pyodide")

  console.time("loadPyodide")
  pyodide = await loadPyodide({indexURL});
  console.timeEnd("loadPyodide")

  pyodide.runPython(loadPythonString)
}

let check_entry, install_imports;

async function loadPyodideAndPackages() {
  const buffer = (await Promise.all([
    loadPyodideOnly(),
    getPackageBuffer(),
  ]))[1];

  console.time("load_package_buffer(buffer)")
  const load_package_buffer = pyodide.globals.get("load_package_buffer")
  const result = load_package_buffer(buffer);
  ({check_entry, install_imports} = toObject(result));
  console.timeEnd("load_package_buffer(buffer)")
}

let pyodideReadyPromise = loadPyodideAndPackages();

const toObject = (x) => {
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

const decoder = new TextDecoder();

async function runCode(entry, inputTextArray, inputMetaArray, interruptBuffer, outputCallback, inputCallback) {
  await pyodideReadyPromise;

  const fullInputCallback = (data) => {
    inputCallback(toObject(data));
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

  pyodide._module.setInterruptBuffer(interruptBuffer);

  try {
    await install_imports(entry.input);
  } catch (e) {
    console.error(e);
  }

  let outputPromise;
  const fullOutputCallback = (data) => {
    outputPromise = outputCallback(toObject(data).parts);
  };
  const result = check_entry(entry, fullInputCallback, fullOutputCallback);
  await outputPromise;
  return toObject(result);
}

Comlink.expose({runCode});
