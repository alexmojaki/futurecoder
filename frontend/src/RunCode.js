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
import {makeChannel, writeMessage} from "sync-message";

let worker, workerWrapper;

function initWorker() {
  worker = new Worker();
  workerWrapper = Comlink.wrap(worker);
}

initWorker();

const channel = makeChannel({serviceWorker: {scope: "/course/"}});
if (channel?.type === "serviceWorker") {
  navigator.serviceWorker.register("/course/service-worker.js", {scope: "/course/"});
}

let interruptBuffer = null;
if (typeof SharedArrayBuffer != "undefined") {
  interruptBuffer = new Int32Array(new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 1));
}

export const terminalRef = React.createRef();

let awaitingInput = false;
let pendingOutput = [];

localforage.config({name: "birdseye", storeName: "birdseye"});

function inputCallback(messageId) {
  awaitingInput = messageId;
  bookSetState("processing", false);
  terminalRef.current.focusTerminal();
}

export let interrupt = () => {
};

let finishedLastRun = Promise.resolve();
let finishedLastRunResolve = () => {};

export const runCode = async ({code, source}) => {
  const shell = source === "shell";
  if (shell) {
    if (awaitingInput) {
      const messageId = awaitingInput;
      awaitingInput = false;
      await writeMessage(channel, {text: code}, messageId);
      bookSetState("processing", true);
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

  awaitingInput = false;
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

  let interrupted = false;
  let interruptResolver;
  const interruptPromise = new Promise(r => interruptResolver = r);
  interrupt = async () => {
    if (awaitingInput) {
      const messageId = awaitingInput;
      awaitingInput = false;
      await writeMessage(channel, {interrupted: true}, messageId);
    } else {
      doInterrupt();
    }
    interrupted = true;
  }

  let doInterrupt;
  if (typeof SharedArrayBuffer === "undefined") {
    doInterrupt = () => {
      worker.terminate();
      initWorker();
      interruptResolver({
        interrupted: true,
        error: null,
        passed: false,
        messages: [],
      });
    }
  } else {
    interruptBuffer = new Int32Array(new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 1));
    doInterrupt = () => {
      interruptBuffer[0] = 2;
    }
  }

  const hasPrediction = currentStep().prediction.choices;

  function outputCallback(output_parts) {
    if (interrupted) {
      return;
    }
    for (const part of output_parts) {
      part.codeSource = source;
    }
    if (hasPrediction) {
      pendingOutput.push(...output_parts);
    } else {
      showOutputParts(output_parts);
    }
  }

  const data = await Promise.race([
    interruptPromise,
    workerWrapper.runCode(
      entry,
      channel,
      interruptBuffer,
      Comlink.proxy(outputCallback),
      Comlink.proxy(inputCallback),
    ),
  ]);

  awaitingInput = false;

  const {error} = data;

  logEvent('run_code', {
    code_source: entry.source,
    page_slug: entry.page_slug,
    step_name: entry.step_name,
    entry_passed: data.passed,
    has_error: Boolean(error),
    num_messages: data.messages?.length,
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
  if (!bookState.prediction.choices || !data.passed) {
    showCodeResult(data);
    terminalRef.current.focusTerminal();
  }

  finishedLastRunResolve();

  if (isProduction) {
    databaseRequest("POST", {
      entry,
      result: {
        messages: data.messages?.map(m => _.truncate(m, {length: 1000})),
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

document.addEventListener('keydown', function (e) {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
    runCode({source: "editor"});
  }
});

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
