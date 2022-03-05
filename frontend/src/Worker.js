/* eslint-disable */
// Otherwise webpack fails silently
// https://github.com/facebook/create-react-app/issues/8014

import * as Comlink from 'comlink';
import pythonCoreUrl from "./python_core.tar.load_by_url"
import {exposePyodide, loadPyodideAndPackage, makeRunnerCallback, toObject} from "./pyodide-worker-runner";

async function load() {
  const pyodide = await loadPyodideAndPackage({url: pythonCoreUrl, format: "tar"});
  pyodide.pyimport("core.init_pyodide").init(process.env.REACT_APP_LANGUAGE);
  return pyodide;
}

const runCode = exposePyodide(
  load(),
  async function (comsyncExtras, pyodide, entry, outputCallback, inputCallback) {
    const pyodide_worker_runner = pyodide.pyimport("pyodide_worker_runner");

    try {
      await pyodide_worker_runner.install_imports(entry.input);
    } catch (e) {
      console.error(e);
    }

    let outputPromise;
    const callback = makeRunnerCallback(comsyncExtras, {
      input: inputCallback,
      output: (data) => {
        outputPromise = outputCallback(data.parts);
      },
    });

    const result = pyodide.pyimport("core.checker").check_entry(entry, callback);
    await outputPromise;
    return toObject(result);
  },
);

Comlink.expose({runCode});
