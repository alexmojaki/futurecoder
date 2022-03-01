/* eslint-disable */
// Otherwise webpack fails silently
// https://github.com/facebook/create-react-app/issues/8014

import * as Comlink from 'comlink';
import pythonCoreUrl from "./python_core.tar?url"
import loadPythonString from "./load.py?raw"
import {readMessage, ServiceWorkerError, uuidv4} from "./sync-message/lib";
import pRetry from 'p-retry';

async function getPackageBuffer() {
  // console.log("FIXME: how was .tar.load_by_url handled by webpack/etc before? Why do we have raw tar instead?
  const response = await fetch(pythonCoreUrl);
  if (!response.ok) {
    throw `Request for package failed with status ${response.status}: ${response.statusText}`
  }
  return await response.arrayBuffer()
}

let pyodide;
let loadPyodide;

async function importPyodide() {
  if (loadPyodide) return
  console.time("importScripts pyodide")
  const Imported = await import ('./vendor/pyodide.js?worker')
  console.timeEnd("importScripts pyodide")
  return Imported.loadPyodide
}

async function loadPyodideOnly() {
  // const indexURL = 'https://cdn.jsdelivr.net/pyodide/v0.19.0/full/';
  // importScripts(indexURL + 'pyodide.js');
  if (!loadPyodide) loadPyodide = await importPyodide()

  console.time("loadPyodide")
  pyodide = await loadPyodide({indexURL: "https://cdn.jsdelivr.net/pyodide/v0.19.1/full/"});
  console.timeEnd("loadPyodide")

  pyodide.runPython(loadPythonString)
  // pyodide.runPythonAsync  // TODO: should we use this? https://stackoverflow.com/questions/63958996/how-do-i-import-modules-in-a-project-using-pyodide-without-errors/64418958#64418958 ... https://github.com/inureyes/pyodide-console/blob/f128de6c5e2fda9115e396820eddb4897458c0cd/examples/webworker.js
}

let check_entry, install_imports;

async function loadPyodideAndPackages() {
  const buffer = (await Promise.all([
    pRetry(loadPyodideOnly, {retries: 3}),
    pRetry(getPackageBuffer, {retries: 3}),
  ]))[1];

  console.time("load_package_buffer(buffer)")
  const load_package_buffer = pyodide.globals.get("load_package_buffer")
  const result = load_package_buffer(buffer, process.env.REACT_APP_LANGUAGE);
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

async function runCode(entry, channel, interruptBuffer, outputCallback, inputCallback) {
  await pyodideReadyPromise;

  const fullInputCallback = (data) => {
    try {
      if (!channel) {
        return 3;  // browser not supported
      }
      const messageId = uuidv4();
      inputCallback(messageId, toObject(data));
      const result = readMessage(channel, messageId).text;
      if (result == null) {
        return 1;  // interrupt
      }
      return result + "\n";
    } catch (e) {
      if (e instanceof ServiceWorkerError) {
        return 2;  // suggesting closing all tabs and reopening
      } else {
        console.error(e);
        return 4;  // general error
      }
    }
  }

  if (interruptBuffer) {
    pyodide.setInterruptBuffer(interruptBuffer);
  }

  try {
    await install_imports(entry.input);
  } catch (e) {
    console.error(e);
  }

  let outputPromise;
  const fullOutputCallback = (data) => {
    outputPromise = outputCallback(toObject(data).parts);
  };

  function sleepCallback(data) {
    const timeout = toObject(data).seconds * 1000;
    if (!(timeout > 0 && channel)) {
      return;
    }
    const messageId = uuidv4();
    try {
      inputCallback(messageId, {sleeping: true});
      readMessage(channel, messageId, {timeout});
    } catch (e) {
      console.error(e);
    }
  }

  const result = check_entry(entry, fullInputCallback, fullOutputCallback, sleepCallback);
  await outputPromise;
  return toObject(result);
}

Comlink.expose({runCode});
