import React from 'react';
import Terminal from './shell/Terminal';
import {rpc} from "./rpc";
import "./css/main.scss"
import "./css/pygments.css"
import "./css/github-markdown.css"
import {connect} from "react-redux";
import {
  addMessage,
  bookSetState,
  bookState,
  closeMessage, currentPage, currentStep, currentStepName,
  movePage,
  moveStep,
  ranCode,
  setDeveloperMode,
} from "./book/store";
import Popup from "reactjs-popup";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/theme-monokai";
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {
  faBars,
  faBug,
  faCog,
  faListOl,
  faPlay,
  faSignOutAlt,
  faTimes,
  faUser,
  faUserGraduate
} from '@fortawesome/free-solid-svg-icons'
import {animateScroll} from "react-scroll";
import {HintsPopup} from "./Hints";
import Toggle from 'react-toggle'
import "react-toggle/style.css"
import {ErrorModal, feedbackContentStyle, FeedbackModal} from "./Feedback";
import birdseyeIcon from "./img/birdseye_icon.png";
import _ from "lodash";
import localforage from "localforage";

// eslint-disable-next-line import/no-webpack-loader-syntax
import Worker from "worker-loader!./Worker.js";
import * as Comlink from 'comlink';
import {stateSet} from "./rpc/store";

const pyodideAPI = Comlink.wrap(new Worker());

export const terminalRef = React.createRef();

localforage.config({name: "birdseye", storeName: "birdseye"});

class AppComponent extends React.Component {
  runCode({code, source}) {
    const shell = source === "shell";
    if (!shell && !code) {
      code = bookState.editorContent;
    }
    if (!code.trim()) {
      return;
    }
    bookSetState("processing", true);
    const entry = {input: code, source, page_slug: bookState.user.pageSlug, step_name: currentStepName()};

    const onSuccess = (data) => {
      if (data.error) {
        stateSet("error", {...data.error, data, method: "run_code"});
        return;
      }
      if (!shell) {
        terminalRef.current.clearStdout();
      }
      bookSetState("processing", false);

      if (source === "birdseye") {
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
          const url = "/static_backend/birdseye/index.html?call_id=" + call_id;
          if (bookState.prediction.state === "hidden") {
            window.open(url);
          } else {
            bookSetState("prediction.codeResult.birdseyeUrl", url);
          }
        });
      }

      ranCode(data);
      if (!data.prediction.choices) {
        showCodeResult(data);
        terminalRef.current.focusTerminal();
      }
    }

    if (process.env.NODE_ENV !== 'development') {
      pyodideAPI.runCode(entry).then(onSuccess);
    } else {
      rpc("run_code", {entry}, onSuccess);
    }
  }

  render() {
    const {
      numHints,
      editorContent,
      messages,
      pages,
      requestingSolution,
      user,
      rpcError,
      prediction,
    } = this.props;
    const page = currentPage();
    const step = currentStep();
    const step_index = step.index;
    let showEditor, showSnoop, showPythonTutor, showBirdseye;
    if (step.text.length) {
      showEditor = page.index >= pages.WritingPrograms.index;
      const snoopPageIndex = pages.UnderstandingProgramsWithSnoop.index;
      showSnoop = page.index > snoopPageIndex ||
        (page.index === snoopPageIndex && step_index >= 1);
      showPythonTutor = page.index >= pages.UnderstandingProgramsWithPythonTutor.index;
      showBirdseye = page.index >= pages.IntroducingBirdseye.index;
    }

    const cantUseEditor = prediction.state === "waiting" || prediction.state === "showingResult";
    return <div className="book-container">
      <div className="book-text markdown-body"
           onCopy={checkCopy}>
        <h1 dangerouslySetInnerHTML={{__html: page.title}}/>
        {page.steps.slice(0, step_index + 1).map((part, index) =>
          <div key={index} id={`step-text-${index}`}>
            <div dangerouslySetInnerHTML={{__html: part.text}}
                 onClick={(event) => {
                   // https://stackoverflow.com/questions/54109790/how-to-add-onclick-event-to-a-string-rendered-by-dangerouslysetinnerhtml-in-reac
                   const button = event.target.closest("button");
                   if (button && event.currentTarget.contains(button) && button.textContent === "Copy") {
                     const codeElement = button.closest("code");
                     let codeText = codeElement.textContent;
                     codeText = codeText.substring(0, codeText.length - "\nCopy".length);
                     bookSetState("editorContent", codeText);
                   }
                 }}
            />
            <hr/>
          </div>
        )}
        {
          messages.map((message, index) =>
            <div key={index} className="card book-message">
              <div
                className="card-header"
                onClick={() => closeMessage(index)}>
                <FontAwesomeIcon icon={faTimes}/>
              </div>
              <div className="card-body" 
                   dangerouslySetInnerHTML={{__html: message}}/>
            </div>
          )
        }
        <div>
          {page.index > 0 &&
          <button className="btn btn-primary btn-sm previous-button"
                  onClick={() => movePage(-1)}>
            Previous
          </button>}
          {" "}
          {page.index < Object.keys(pages).length - 1 && step_index === page.steps.length - 1 &&
          <button className="btn btn-success next-button"
                  onClick={() => movePage(+1)}>
            Next
          </button>}
        </div>
        <br/>
        {
          user.developerMode && <StepButtons/>
        }
      </div>
      <div className="ide">
        <div className={"editor-buttons " + (showEditor ? "" : "invisible")}>
          <button
            disabled={cantUseEditor}
            className="btn btn-primary"
            onClick={() => {
              this.runCode({source: "editor"});
            }}
          >
            <FontAwesomeIcon icon={faPlay}/> Run
          </button>

          {" "}

          {showSnoop &&
          <button
            disabled={cantUseEditor}
            className="btn btn-success"
            onClick={() => {
              this.runCode({source: "snoop"})
            }}
          >
            <FontAwesomeIcon icon={faBug}/> Snoop
          </button>}

          {" "}

          {showPythonTutor &&
          <button
            disabled={cantUseEditor}
            className="btn btn-success"
            onClick={() => {
              this.runCode({source: "pythontutor"});
              window.open(
                'https://pythontutor.com/iframe-embed.html#code=' +
                encodeURIComponent(bookState.editorContent) +
                '&codeDivHeight=600' +
                '&codeDivWidth=600' +
                '&cumulative=false' +
                '&curInstr=0' +
                '&heapPrimitives=false' +
                '&origin=opt-frontend.js' +
                '&py=3' +
                '&rawInputLstJSON=%5B%5D' +
                '&textReferences=false',
              );
            }}
          >
            <FontAwesomeIcon icon={faUserGraduate}/> Python Tutor
          </button>}

          {" "}

          {showBirdseye &&
          <button
            disabled={cantUseEditor}
            className="btn btn-success"
            onClick={() => {
              this.runCode({source: "birdseye"})
            }}
          >
            <img
              src={birdseyeIcon}
              width={20}
              height={20}
              alt="birdseye logo"
              style={{position: "relative", top: "-2px"}}
            />
            Bird's Eye
          </button>}

        </div>
        <div className="editor-and-terminal">
          {showEditor && <div className="editor">
            <AceEditor
              mode="python"
              theme="monokai"
              onChange={(value) => {
                bookSetState("editorContent", value);
              }}
              value={editorContent}
              name="editor"
              height="100%"
              width="100%"
              onLoad={(editor) => {
                editor.renderer.setScrollMargin(10);
                editor.renderer.setPadding(10);
              }}
              fontSize="15px"
              setOptions={{
                fontFamily: "monospace",
                showPrintMargin: false,
              }}
              readOnly={cantUseEditor}
            />
          </div>}
          <div className="terminal" style={{height: showEditor ? "49%" : "100%"}}>
            <Terminal
              onCommand={(cmd) => this.runCode({code: cmd, source: "shell"})}
              ref={terminalRef}
            />
          </div>
        </div>
      </div>

      <HintsPopup
        hints={step.hints}
        numHints={numHints}
        requestingSolution={requestingSolution}
        solution={step.solution}
      />

      <MenuPopup
        user={user}
      />

      <ErrorModal error={rpcError}/>
    </div>
  }
}

const StepButton = ({delta, label}) =>
  <button className={`btn btn-danger btn-sm button-${label.replace(" ", "-").toLowerCase()}`}
          onClick={() => moveStep(delta)}>
    {label}
  </button>

const StepButtons = () =>
  <div style={{position: "fixed", bottom: 0}}>
    <StepButton delta={-1} label="Reverse step"/>
    {" "}
    <StepButton delta={+1} label="Skip step"/>
  </div>


const MenuPopup = ({user}) =>
  <div className="custom-popup">
    <Popup
      trigger={
        <button className="btn menu-icon">
          <FontAwesomeIcon icon={faBars} size="lg"/>
        </button>}
    >
      <div className="menu-popup">
        <p><FontAwesomeIcon icon={faUser}/> {user.email}</p>
        <p><a href="/accounts/logout/"> <FontAwesomeIcon icon={faSignOutAlt}/> Sign out</a></p>
        <p>
          <Popup
            trigger={<a href="#"><FontAwesomeIcon icon={faCog}/> Settings </a>}
            modal
            closeOnDocumentClick
          >
            <SettingsModal user={user}/>
          </Popup>
        </p>
        <p>
          <Popup
            trigger={<a href="#"><FontAwesomeIcon icon={faBug}/> Feedback </a>}
            modal
            closeOnDocumentClick
            contentStyle={feedbackContentStyle}
          >
            {close => <FeedbackModal close={close}/>}
          </Popup>
        </p>
        <p><a href="/toc/"> <FontAwesomeIcon icon={faListOl}/> Table of Contents</a></p>
      </div>
    </Popup>
  </div>


const SettingsModal = ({user}) => (
  <div className="settings-modal">
    <h1>Settings</h1>
    <br/>
    <label>
      <Toggle
        defaultChecked={user.developerMode}
        onChange={(e) => setDeveloperMode(e.target.checked)}
      />
      <b>Developer mode</b>
    </label>

    <p>Enables the "Reverse step" and "Skip step" buttons.</p>
  </div>
)

const checkCopy = () => {
  const selection = document.getSelection();
  const codeElement = (node) => node.parentElement.closest("code");
  if (
    [...document.querySelectorAll(".book-text code")]
      .filter(node => selection.containsNode(node))
      .concat([
        codeElement(selection.anchorNode),
        codeElement(selection.focusNode),
      ])
      .some((node) => node && !node.classList.contains("copyable"))
  ) {
    addMessage(`
      <div>
        <p><strong>STOP!</strong></p>
        <p>
        Try to avoid copy pasting code. You will learn, absorb, and remember better if you
        type in the code yourself.
        </p>
        <p>
        When copying is appropriate, there will be a button to click to make it easy.
        If there's no button, try typing.
        </p>
        <p>
        Having said that, we're not going to force you. Copy if you really want to.
        </p>
      </div>
   `);
  }
}


export const App = connect(
  state => ({
    ...state.book,
    rpcError: state.rpc.error,
  }),
)(AppComponent);


export const showCodeResult = ({birdseyeUrl, output_parts, passed}) => {
  const terminal = terminalRef.current;
  terminal.pushToStdout(output_parts);
  animateScroll.scrollToBottom({duration: 30, container: terminal.terminalRoot.current});

  if (passed) {
    moveStep(1);
  }

  if (birdseyeUrl) {
    window.open(birdseyeUrl);
  }
}
