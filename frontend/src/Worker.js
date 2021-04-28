import * as Comlink from 'comlink';

importScripts('https://cdn.jsdelivr.net/pyodide/v0.17.0/full/pyodide.js');

async function loadPyodideAndPackages() {
  await loadPyodide({indexURL: 'https://cdn.jsdelivr.net/pyodide/v0.17.0/full/'});
  await pyodide.runPythonAsync(`
import io
import zipfile
from js import fetch
import sys

package_path = "/tmp/package/"
url = "/static_backend/package.zip"

resp = await fetch(url)
if not resp.ok:
    raise OSError(
        f"Request for {url} failed with status {resp.status}: {resp.statusText}"
    )
buffer = await resp.arrayBuffer()
fd = io.BytesIO(buffer.to_py())
with zipfile.ZipFile(fd) as zf:
    zf.extractall(package_path)

sys.path.append(package_path)

from core.workers.worker import run_code_catch_errors  # noqa trigger imports
print("Python core ready!")
`)
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
    let resolver;
    const promise = new Promise(r => resolver = r);
    pyodide.globals.get("run_code_catch_errors")(entry, null, (result) => resolver(toObject(result.toJs())))
    return await promise;
  }
}

Comlink.expose(api);
