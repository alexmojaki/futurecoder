import {
  bookSetState,
  bookState,
  currentStep,
  currentStepName,
  loadedPromise,
  logEvent,
  moveStep,
  postCodeEntry,
  ranCode
} from "./book/store";
import _ from "lodash";
import localforage from "localforage";
import {animateScroll} from "react-scroll";
import React from "react";
import * as Sentry from "@sentry/react";
import {wrapAsync} from "./frontendlib/sentry";
import {runCodeTask, taskClient} from "./TaskClient";

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
    showInternalErrorOutput(`${e.name}: ${e.message}`);
    const {name, message, stack} = e;
    bookSetState("error", {name, message, stack});
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

  const {route, user, questionWizard, editorContent, assistant: {numHints, requestingSolution}} = bookState;
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
  } finally {
    bookSetState("processing", false);
    bookSetState("running", false);
  }

  const {error} = data;

  const event = {
    code_source: entry.source,
    page_slug: entry.page_slug,
    step_name: entry.step_name,
    entry_passed: data.passed,
    has_error: Boolean(error),
    page_route: route,
    num_hints: numHints,
    requesting_solution: requestingSolution,
  };
  for (const section of data.message_sections || []) {
    event[`num_messages_${section.type}`] = section.messages.length;
  }
  logEvent('run_code', event);

  if (error) {
    Sentry.captureEvent(error.sentry_event);
    delete error.sentry_event;
    bookSetState("error", {...error});
    showInternalErrorOutput(error.title);
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
      messageSections: data.message_sections?.map(section => ({
        type: section.type,
        messages: section.messages?.map(m => _.truncate(m, {length: 1000})),
      })),
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

function showInternalErrorOutput(message) {
  showOutputParts([
    {text: `\n${message.trim()}\n\n`, type: 'internal_error'},
    {text: '', type: 'internal_error_explanation'},
    {text: '>>> ', type: 'shell_prompt'},
  ]);
}
