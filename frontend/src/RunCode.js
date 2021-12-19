// eslint-disable-next-line import/no-webpack-loader-syntax
import Worker from "worker-loader!./Worker.js";
import * as Comlink from 'comlink';
import {
  bookSetState,
  bookState,
  currentStep,
  currentStepName,
  databaseRequest,
  isProduction,
  logEvent,
  moveStep,
  ranCode
} from "./book/store";
import _ from "lodash";
import localforage from "localforage";
import {animateScroll} from "react-scroll";
import React from "react";
import * as Sentry from "@sentry/react";

const Runner = Comlink.wrap(new Worker());

let inputTextArray, inputMetaArray, interruptBuffer = null;
if (typeof SharedArrayBuffer == "undefined") {
  inputTextArray = null;
  inputMetaArray = null;
} else {
  inputTextArray = new Uint8Array(new SharedArrayBuffer(128 * 1024));
  inputMetaArray = new Int32Array(new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 2));
  interruptBuffer = new Int32Array(new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 1));
}

const encoder = new TextEncoder();

export const terminalRef = React.createRef();

let awaitingInput = false;
let pendingOutput = [];

localforage.config({name: "birdseye", storeName: "birdseye"});

const runCodeRemote = async (entry, onSuccess) => {
  interruptBuffer[0] = 2;
  interruptBuffer = new Int32Array(new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 1));
  const runner = await new Runner();
  const result = await runner.runCode(
    entry,
    inputTextArray,
    inputMetaArray,
    interruptBuffer,
    Comlink.proxy(outputCallback),
    Comlink.proxy(inputCallback),
  );
  onSuccess(result);
}


function outputCallback(output_parts) {
  if (currentStep().prediction.choices) {
    pendingOutput.push(...output_parts);
  } else {
    showOutputParts(output_parts);
  }
}

function inputCallback() {
  awaitingInput = true;
  bookSetState("processing", false);
}

export const runCode = ({code, source}) => {
  const shell = source === "shell";
  if (shell) {
    if (awaitingInput) {
      awaitingInput = false;
      writeInput(code);
      bookSetState("processing", true);
      return;
    }
  } else {
    terminalRef.current.clearStdout();
  }

  awaitingInput = false;
  pendingOutput = [];

  const {route, user, questionWizard, editorContent, numHints, requestingSolution} = bookState;
  if (!shell && !code) {
    code = editorContent;
  }
  bookSetState("processing", true);
  const entry = {
    input: code,
    source,
    page_slug: user.pageSlug,
    step_name: currentStepName(),
    question_wizard: route === "question",
    expected_output: questionWizard.expectedOutput,
  };

  const onSuccess = (data) => {
    const {error} = data;

    logEvent('run_code', {
      code_source: entry.source,
      page_slug: entry.page_slug,
      step_name: entry.step_name,
      entry_passed: data.passed,
      has_error: Boolean(error),
      num_messages: data.messages?.length,
      // user: user.uid,
      // developerMode: user.developerMode,
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

    bookSetState("processing", false);

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
                return localforage.setItem(fullKey, value);
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
    if (!bookState.prediction.choices) {
      showCodeResult(data);
      terminalRef.current.focusTerminal();
    }

    if (isProduction) {
      databaseRequest("POST", {
        entry,
        result: {
          ..._.omit(data, "output_parts"),
          messages: data.messages.map(m => _.truncate(m, {length: 1000})),
          output: _.truncate(data.output, {length: 1000}),
        },
        state: {
          developerMode: user.developerMode,
          page_route: route,
          num_hints: numHints,
          requesting_solution: requestingSolution,
        },
        timestamp: new Date().toISOString(),
      }, "code_entries");
    }
  }

  runCodeRemote(entry, onSuccess);
}

document.addEventListener('keydown', function (e) {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    runCode({source: "editor"});
  }
});

const writeInput = (string) => {
  const bytes = encoder.encode(string);
  if (bytes.length > inputTextArray.length) {
    throw "Input is too long";  // TODO
  }
  inputTextArray.set(bytes, 0);  // TODO ensure no race conditions
  Atomics.store(inputMetaArray, 0, bytes.length);
  Atomics.store(inputMetaArray, 1, 1);
  Atomics.notify(inputMetaArray, 1);
}

function showOutputParts(output_parts) {
  const terminal = terminalRef.current;
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
