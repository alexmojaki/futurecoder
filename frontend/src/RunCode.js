import {
  bookSetState,
  bookState,
  currentStep,
  currentStepName,
  postCodeEntry,
  loadedPromise,
  logEvent,
  moveStep,
  ranCode
} from "./book/store";
import _ from "lodash";
import localforage from "localforage";
import {animateScroll} from "react-scroll";
import React from "react";
import * as Sentry from "@sentry/react";
import {wrapAsync} from "./frontendlib/sentry";
import {taskClient, runCodeTask} from "./TaskClient";

export const terminalRef = React.createRef();

let pendingOutput = [];

const birdseyeLocalStore = localforage.createInstance({name: "birdseye", storeName: "birdseye"});

function inputCallback() {
  bookSetState("processing", false);
  terminalRef.current?.focusTerminal();
}

export function interrupt() {
  taskClient.interrupt();
}

let finishedLastRun = Promise.resolve();
let finishedLastRunResolve = () => {};

export async function runCode(entry) {
  try {
    await _runCode(entry)
  } catch (e) {
    bookSetState("error", {
      details: e.message,
      title: "JS Error while running code: " + e.name,
    });
    Sentry.captureException(e);
  }
}

export const _runCode = wrapAsync(async function runCode({code, source}) {
  const shell = source === "shell";
  if (shell) {
    if (taskClient.state === "awaitingMessage") {
      bookSetState("processing", true);
      try {
        await taskClient.writeMessage(code);
      } catch (e) {
        console.warn(e);
      }
      return;
    }
  } else {
    if (bookState.running) {
      interrupt();
      await finishedLastRun;
    }
    finishedLastRun = new Promise(r => finishedLastRunResolve = r);

    terminalRef.current.clearStdout();
  }

  pendingOutput = [];

  bookSetState("processing", true);
  bookSetState("running", true);

  await loadedPromise;

  const {route, user, questionWizard, editorContent, numHints, requestingSolution} = bookState;
  if (!shell && !code) {
    code = editorContent;
  }

  const entry = {
    input: code,
    source,
    page_slug: user.pageSlug,
    step_name: currentStepName(),
    question_wizard: route === "question",
    expected_output: questionWizard.expectedOutput,
  };

  const hasPrediction = currentStep().prediction?.choices;

  function outputCallback(output_parts) {
    for (const part of output_parts) {
      part.codeSource = source;
    }
    if (hasPrediction || !terminalRef.current) {
      pendingOutput.push(...output_parts);
    } else {
      showOutputParts(output_parts);
    }
  }

  let data;
  try {
    data = await runCodeTask(
      entry,
      outputCallback,
      inputCallback,
    );
  } catch (e) {
    showOutputParts({text: '>>> ', type: 'shell_prompt'});
    throw e;
  } finally {
    bookSetState("processing", false);
    bookSetState("running", false);
  }

  const {error} = data;

  logEvent('run_code', {
    code_source: entry.source,
    page_slug: entry.page_slug,
    step_name: entry.step_name,
    entry_passed: data.passed,
    has_error: Boolean(error),
    // num_messages: data.messages?.length,  // XXX
    page_route: route,
    num_hints: numHints,
    requesting_solution: requestingSolution,
  });

  if (error) {
    Sentry.captureEvent(error.sentry_event);
    delete error.sentry_event;
    bookSetState("error", {...error});
    return;
  }

  if (data.birdseye_objects) {
    const {store, call_id} = data.birdseye_objects;
    delete data.birdseye_objects;
    Promise.all(
      _.flatMapDeep(
        _.entries(store),
        ([rootKey, blob]) =>
          _.entries(blob)
            .map(([key, value]) => {
              const fullKey = rootKey + "/" + key;
              return birdseyeLocalStore.setItem(fullKey, value);
            })
      )
    ).then(() => {
      const url = "/course/birdseye/?call_id=" + call_id;
      if (bookState.prediction.state === "hidden") {
        window.open(url);
      } else {
        bookSetState("prediction.codeResult.birdseyeUrl", url);
      }
    });
  }

  ranCode(data);
  if (!bookState.prediction.choices || !data.passed) {
    showCodeResult(data);
    terminalRef.current?.focusTerminal();
  }

  finishedLastRunResolve();

  postCodeEntry({
    entry,
    result: {
      passed: data.passed,
      // messages: data.messages?.map(m => _.truncate(m, {length: 1000})),  // XXX
      output: _.truncate(data.output, {length: 1000}),
    },
  });
});

document.addEventListener('keydown', function (e) {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    runCode({source: "editor"});
  }
});

function showOutputParts(output_parts) {
  const terminal = terminalRef.current;
  if (!terminal) {
    setTimeout(() => showOutputParts(output_parts), 500);
    return;
  }
  terminal.pushToStdout(output_parts);
  animateScroll.scrollToBottom({duration: 0, container: terminal.terminalRoot.current});
}

export const showCodeResult = ({birdseyeUrl, passed}) => {
  pendingOutput.push({text: '>>> ', type: 'shell_prompt'});
  showOutputParts(pendingOutput);
  pendingOutput = [];

  if (passed) {
    moveStep(1);
  }

  if (birdseyeUrl) {
    window.open(birdseyeUrl);
  }
}
