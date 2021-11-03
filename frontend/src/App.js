import React from 'react';
import Terminal from './shell/Terminal';
import "./css/main.scss"
import "./css/pygments.css"
import "./css/github-markdown.css"
import {connect} from "react-redux";
import {
  addMessage,
  bookSetState,
  bookState,
  closeMessage,
  currentPage,
  currentStep,
  movePage,
  moveStep,
  updateDatabase,
  setDeveloperMode,
  setEditorContent,
  specialHash,
  userMoveDirection,
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
  faCompress,
  faExpand,
  faListOl,
  faPlay,
  faQuestionCircle,
  faSignOutAlt,
  faTimes,
  faUser,
  faUserGraduate
} from '@fortawesome/free-solid-svg-icons'
import {HintsPopup} from "./Hints";
import Toggle from 'react-toggle'
import "react-toggle/style.css"
import {ErrorModal, feedbackContentStyle, FeedbackModal} from "./Feedback";
import birdseyeIcon from "./img/birdseye_icon.png";
import {runCode, terminalRef} from "./RunCode";
import firebase from "firebase/app";
import StyledFirebaseAuth from "react-firebaseui/StyledFirebaseAuth";
import {TableOfContents} from "./TableOfContents";


const EditorButtons = (
  {
    disabled,
    showBirdseye,
    showEditor,
    showPythonTutor,
    showSnoop,
    showQuestionButton,
  }) =>
  <div className={"editor-buttons " + (showEditor ? "" : "invisible")}>
    <button
      disabled={disabled}
      className="btn btn-primary"
      onClick={() => runCode({source: "editor"})}
    >
      <FontAwesomeIcon icon={faPlay}/> Run
    </button>

    {" "}

    {showSnoop &&
    <button
      disabled={disabled}
      className="btn btn-success"
      onClick={() => runCode({source: "snoop"})}
    >
      <FontAwesomeIcon icon={faBug}/> Snoop
    </button>}

    {" "}

    {showPythonTutor &&
    <button
      disabled={disabled}
      className="btn btn-success"
      onClick={() => {
        runCode({source: "pythontutor"});
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
      disabled={disabled}
      className="btn btn-success"
      onClick={() => runCode({source: "birdseye"})}
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

    {" "}

    {showQuestionButton && !disabled &&
    <a className="btn btn-success"
       href={"#question"}>
      <FontAwesomeIcon icon={faQuestionCircle}/> Ask for help
    </a>}
  </div>;

const Editor = ({readOnly, value}) =>
  <div className="editor">
    <AceEditor
      mode="python"
      theme="monokai"
      onChange={setEditorContent}
      onLoad={(editor) => {
        editor.renderer.setScrollMargin(10);
        editor.renderer.setPadding(10);
      }}
      value={value}
      name="editor"
      height="100%"
      width="100%"
      fontSize="15px"
      setOptions={{
        fontFamily: "monospace",
        showPrintMargin: false,
      }}
      readOnly={readOnly}
    />
  </div>;

const Shell = () =>
  <Terminal
    onCommand={(cmd) => runCode({code: cmd, source: "shell"})}
    ref={terminalRef}
  />

const Messages = (
  {
    messages,
  }) =>
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

const QuestionWizard = (
  {
    messages,
    requestExpectedOutput,
    expectedOutput,
  }) =>
  <>
    <h1>Question Wizard</h1>
    <p>
      If you need help, there are many sites like
      {" "} <a target="_blank" rel="noreferrer" href="https://stackoverflow.com/">Stack Overflow</a> {" "}
      and <a target="_blank" rel="noreferrer" href="https://www.reddit.com/r/learnpython/">reddit</a> where
      you can ask questions.
      This is a tool to help you write a good quality question that is likely to get answers.
    </p>
    <p>
      Enter and run your code on the right. If you don't have any code because you don't know where to get started,
      I'm afraid this tool can't help you. You can still ask for help, but it might be good to first
      read <a target="_blank" rel="noreferrer"
              href="https://stackoverflow.com/help/dont-ask">What types of questions should I avoid asking?</a>
    </p>
    <p>
      If your question is about servers (e.g. Django or Flask), web requests, databases, or a package that can't be
      imported here, then this tool won't work. However, just because your current code <em>involves</em> those things,
      that doesn't mean that's what your question is <em>about</em>. If you're having a general
      Python/programming/logic problem, then extract that problem from the other stuff.
      Python with Django is still Python. If you can't do that, then
      read <a target="_blank" rel="noreferrer"
              href="https://stackoverflow.com/help/minimal-reproducible-example">
      How to create a Minimal, Reproducible Example</a> before
      asking your question.
    </p>
    <hr/>
    {requestExpectedOutput && <>
      <p>
        Good, now enter the output you expect/want from your program below.
        What would it show if it worked correctly?
        If it's not supposed to output anything, then add some <code>print()</code> calls to your
        code so that it would output something useful.
      </p>
      <p>
        When you're done, click 'Run' again to generate your question.
      </p>
      <AceEditor
        onChange={value => bookSetState("questionWizard.expectedOutput", value)}
        theme={"monokai"}
        onLoad={(editor) => {
          editor.renderer.setScrollMargin(10);
          editor.renderer.setPadding(10);
        }}
        width="100%"
        height="15em"
        value={expectedOutput}
        name="expectedOutput"
        fontSize="15px"
        setOptions={{
          fontFamily: "monospace",
          showPrintMargin: false,
        }}
      />
      <hr/>
    </>
    }
    {messages.map((message, index) =>
      <div key={index}>
        <Markdown html={message} copyFunc={text => navigator.clipboard.writeText(text)}/>
        <hr/>
      </div>
    )}
  </>

const Markdown = (
  {
    html,
    copyFunc,
  }) =>
  <div dangerouslySetInnerHTML={{__html: html}}
       onClick={(event) => {
         // https://stackoverflow.com/questions/54109790/how-to-add-onclick-event-to-a-string-rendered-by-dangerouslysetinnerhtml-in-reac
         const button = event.target.closest("button");
         if (button && event.currentTarget.contains(button) && button.textContent === "Copy") {
           const codeElement = button.closest("code");
           let codeText = codeElement.textContent;
           codeText = codeText.substring(0, codeText.length - "\nCopy".length);
           copyFunc(codeText);
         }
       }}
  />

const CourseText = (
  {
    user,
    step_index,
    page,
    pages,
    messages
  }) => {
    const isNextButtonVisible = page.index < Object.keys(pages).length - 1 && step_index === page.steps.length - 1;
    const animateEntry = index => {
      if (userMoveDirection() < 0 || index === 0) {
        return {};
      }
      // animation shorthand: name | duration | easing-function | delay
      const animation = 'next-step-transition 0.7s ease-out, next-step-flash 3s ease-out 0.7s';

      // Animate only the last element if the 'Next' button is visible
      if (isNextButtonVisible) {
        if (index === step_index) {
          return { animation };
        }

        return {};
      }

      return { animation };
    }

    return <>
      <h1 dangerouslySetInnerHTML={{__html: page.title}}/>
      {page.steps.slice(0, step_index + 1).map((part, index) =>
        <div
          key={index}
          id={`step-text-${index}`}
          className={index > 0 ? 'pt-3' : ''}
          style={animateEntry(index)}
        >
          <Markdown html={part.text} copyFunc={text => bookSetState("editorContent", text)}/>
          <hr style={{ margin: '0' }}/>
        </div>
      )}
      <Messages {...{messages}}/>
      {/* pt-3 is Bootstrap's helper class. Shorthand for padding-top: 1rem. Avialable classes are pt-{1-5} */}
      <div className='pt-3'>
        {page.index > 0 &&
        <button className="btn btn-primary previous-button"
                onClick={() => movePage(-1)}>
          Previous
        </button>}
        {" "}
        {isNextButtonVisible &&
        <button className="btn btn-success next-button"
                onClick={() => movePage(+1)}>
          Next
        </button>}
      </div>
      <br/>
      {
        user.developerMode && <StepButtons/>
      }
    </>;
  }

class AppComponent extends React.Component {
  render() {
    const {
      numHints,
      editorContent,
      messages,
      questionWizard,
      pages,
      requestingSolution,
      user,
      error,
      prediction,
      route,
      previousRoute,
    } = this.props;
    if (route === "toc") {
      return <TableOfContents/>
    }
    const isQuestionWizard = route === "question";
    const fullIde = route === "ide";

    const page = currentPage();
    const step = currentStep();
    const step_index = step.index;

    let showEditor, showSnoop, showPythonTutor, showBirdseye, showQuestionButton;
    if (fullIde || isQuestionWizard) {
      showEditor = true;
      showSnoop = true;
      showPythonTutor = true;
      showBirdseye = true;
      showQuestionButton = !(isQuestionWizard || previousRoute === "question");
    } else if (step.text.length) {
      showEditor = page.index >= pages.WritingPrograms.index;
      const snoopPageIndex = pages.UnderstandingProgramsWithSnoop.index;
      showSnoop = page.index > snoopPageIndex ||
        (page.index === snoopPageIndex && step_index >= 1);
      showPythonTutor = page.index >= pages.UnderstandingProgramsWithPythonTutor.index;
      showBirdseye = page.index >= pages.IntroducingBirdseye.index;
      showQuestionButton = page.index > pages.IntroducingBirdseye.index;
    }

    const cantUseEditor = prediction.state === "waiting" || prediction.state === "showingResult";
    return <div className="book-container">
      <nav className="navbar navbar-expand-lg navbar-light bg-light">
        <span className="nav-item custom-popup">
          <MenuPopup user={user}/>
        </span>
        <span className="nav-item navbar-text">
          {
            user.email ?
              <><FontAwesomeIcon icon={faUser}/> {user.email}</>
              :
              <Popup
                trigger={
                  <button className="btn btn-primary">
                    <FontAwesomeIcon icon={faUser}/> Login / Sign up
                  </button>
                }
                modal
                closeOnDocumentClick
              >
                <StyledFirebaseAuth
                  uiConfig={{
                    signInOptions: [
                      {
                        provider: firebase.auth.EmailAuthProvider.PROVIDER_ID,
                        requireDisplayName: false,
                      },
                      // TODO not working because of cross origin isolation
                      // firebase.auth.GoogleAuthProvider.PROVIDER_ID,
                      // firebase.auth.FacebookAuthProvider.PROVIDER_ID,
                      // firebase.auth.GithubAuthProvider.PROVIDER_ID,
                    ],
                    autoUpgradeAnonymousUsers: true,
                    callbacks: {
                      // Avoid redirects after sign-in.
                      signInSuccessWithAuthResult: () => false,

                      // Ignore merge conflicts when upgrading anonymous users and continue signing in
                      // The store will merge the user data
                      signInFailure: (error) => {
                        if (error.code === 'firebaseui/anonymous-upgrade-merge-conflict') {

                          // Note the upgrade in the old anonymous account
                          updateDatabase({upgradedFromAnonymous: true});

                          firebase.auth().signInWithCredential(error.credential);
                        }
                      }
                    }
                  }}
                  firebaseAuth={firebase.auth()}
                />
              </Popup>
          }
        </span>
        <a className="nav-item nav-link" href="#toc">
          <FontAwesomeIcon icon={faListOl}/> Table of Contents
        </a>
      </nav>

      {!fullIde &&
      <div className="book-text markdown-body">
        {isQuestionWizard ?
          <QuestionWizard {...questionWizard}/>
          :
          <div onCopy={checkCopy}>
            <CourseText {...{
              user,
              step_index,
              page,
              pages,
              messages
            }}/>
          </div>
        }
      </div>

      }

      <EditorButtons {...{
        showBirdseye,
        showEditor,
        showSnoop,
        showPythonTutor,
        showQuestionButton,
        disabled: cantUseEditor,
      }}/>

      <div className={`ide ide-${fullIde ? 'full' : 'half'}`}>
        <div className="editor-and-terminal">
          {showEditor &&
           <Editor value={editorContent} readOnly={cantUseEditor}/>
          }
          <div className="terminal" style={{height: showEditor ? undefined : "100%"}}>
            <Shell/>
          </div>
        </div>
      </div>

      <a className="btn btn-primary full-ide-button"
         href={"#" + (!fullIde ? "ide" : (specialHash(previousRoute) ? previousRoute : page.slug))}>
        <FontAwesomeIcon icon={fullIde ? faCompress : faExpand}/>
      </a>

      {!(fullIde || isQuestionWizard) &&
      <HintsPopup
        hints={step.hints}
        numHints={numHints}
        requestingSolution={requestingSolution}
        solution={step.solution}
      />
      }

      <ErrorModal error={error}/>
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
    <Popup
      trigger={
        <button className="btn btn-sm btn-outline-secondary">
          <FontAwesomeIcon icon={faBars} size="lg"/>
        </button>}
    >
      {close => <div className="menu-popup">
        <p><button
          className="btn btn-danger"
          onClick={() => {
            close();
            bookSetState("user.uid", null)
            firebase.auth().signOut();
          }}
        >
          <FontAwesomeIcon icon={faSignOutAlt}/> Sign out
        </button></p>
        <p>
          <Popup
            trigger={
              <button className="btn btn-primary">
                <FontAwesomeIcon icon={faCog}/> Settings
              </button>
              }
            modal
            closeOnDocumentClick
          >
            <SettingsModal user={user}/>
          </Popup>
        </p>
        <p>
          <Popup
            trigger={
              <button className="btn btn-success">
                <FontAwesomeIcon icon={faBug}/> Feedback
              </button>
            }
            modal
            closeOnDocumentClick
            contentStyle={feedbackContentStyle}
          >
            {close => <FeedbackModal close={close}/>}
          </Popup>
        </p>
      </div>}
    </Popup>


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
  }),
)(AppComponent);

