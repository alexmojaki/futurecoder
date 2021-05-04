/* eslint-disable */
// Otherwise webpack fails silently
// https://github.com/facebook/create-react-app/issues/8014

import * as Comlink from 'comlink';

async function getPackageBuffer() {
  const response = await fetch("/static_backend/package.zip");
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
import zipfile
import sys

package_path = "/tmp/package/"

def load_package_buffer(buffer):
    global run_code_catch_errors
    fd = io.BytesIO(buffer.to_py())
    with zipfile.ZipFile(fd) as zf:
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

const api = {
  async runCode(entry) {
    await pyodideReadyPromise;
    return await new Promise(resolver =>
      pyodide.globals.get("run_code_catch_errors")(entry, null, (result) => resolver(toObject(result.toJs())))
    );
  }
}

Comlink.expose(api);
