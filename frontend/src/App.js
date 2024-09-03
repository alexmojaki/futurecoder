import React from 'react';
import Terminal from './shell/Terminal';
import "./css/main.scss"
import "./css/pygments.css"
import "./css/github-markdown.css"
import {connect} from "react-redux";
import {
  addSpecialMessage,
  bookSetState,
  bookState,
  closeSpecialMessage,
  currentPage,
  currentStep,
  currentStepName,
  disableLogin,
  logEvent,
  movePage,
  moveStep,
  openAssessment,
  postCodeEntry,
  setDeveloperMode,
  setEditorContent,
  signOut,
  specialHash,
} from "./book/store";
import Popup from "reactjs-popup";
import AceEditor from "react-ace";
import Collapsible from 'react-collapsible';
import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/theme-monokai";
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {
  faBars,
  faBug,
  faCog,
  faCompress,
  faExpand,
  faLightbulb,
  faListCheck,
  faListOl,
  faPlay,
  faQuestionCircle,
  faRobot,
  faSignOutAlt,
  faStop,
  faUserGraduate
} from '@fortawesome/free-solid-svg-icons'
import {HintsAssistant} from "./Hints";
import Toggle from 'react-toggle'
import "react-toggle/style.css"
import {ErrorBoundary, FeedbackMenuButton} from "./Feedback";
import birdseyeIcon from "./img/birdseye_icon.png";
import languageIcon from "./img/language.png";
import {interrupt, runCode, terminalRef} from "./RunCode";
import firebase from "firebase/app";
import {TableOfContents} from "./TableOfContents";
import HeaderLoginInfo from "./components/HeaderLoginInfo";
import terms from "./terms.json"
import _ from "lodash";
import {otherVisibleLanguages} from "./languages";
import {Requirements} from "./Requirements";
import {AI} from "./AI";


const EditorButtons = (
  {
    disabled,
    showBirdseye,
    showEditor,
    showPythonTutor,
    showSnoop,
    showQuestionButton,
    running,
  }) =>
  <div className={"editor-buttons " + (showEditor ? "" : "invisible")}>
    {
      running ?
        <button
          className="btn btn-danger"
          onClick={() => interrupt()}
        >
          <FontAwesomeIcon icon={faStop}/> {terms.stop}
        </button>
        :
        <button
          disabled={disabled}
          className="btn btn-primary"
          onClick={() => runCode({source: "editor"})}
        >
          <FontAwesomeIcon icon={faPlay}/> {terms.run}
        </button>
    }

    {" "}

    {showSnoop &&
      <button
        disabled={disabled || running}
        className="btn btn-success"
        onClick={() => runCode({source: "snoop"})}
      >
        <FontAwesomeIcon icon={faBug}/> <span style={{fontFamily: "monospace"}}>snoop</span>
      </button>}

    {" "}

    {showPythonTutor &&
      <button
        disabled={disabled || running}
        className="btn btn-success"
        onClick={() => {
          runCode({source: "pythontutor"});
          let code = bookState.editorContent;
          if (code.includes("assert_equal") && !code.includes("def assert_equal(")) {
            code = 'def assert_equal(actual, expected):\n' +
              '    if actual == expected:\n' +
              '        print("OK")\n' +
              '    else:\n' +
              '        print(f"Error! {repr(actual)} != {repr(expected)}")\n\n\n' + code;
          }
          window.open(
            'https://pythontutor.com/iframe-embed.html#code=' +
            encodeURIComponent(code) +
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
        disabled={disabled || running}
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
        <span style={{fontFamily: "monospace"}}> birdseye</span>
      </button>}

    {" "}

    {showQuestionButton && !disabled &&
      <a className="btn btn-success"
         href={"#question"}>
        <FontAwesomeIcon icon={faQuestionCircle}/> {terms.ask_for_help}
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
    messageSections,
  }) => {
  const nonEmptySections = messageSections.filter(section => section?.messages?.length);
  if (!nonEmptySections.length) {
    return <p dangerouslySetInnerHTML={{__html: terms.assessment_description}}/>;
  }
  return nonEmptySections.map((section) => {
    if (section.type === "passed_tests") {
      return <div key={section.type} className="card alert alert-success" style={{padding: 0}}>
        <div className="card-body">
          <details>
            <summary>
              {_.template(terms.assessment_passed_tests)({ num: section.messages.length })}
            </summary>
            <br/>
            <SectionMessages section={section}/>
          </details>
        </div>
      </div>
    } else if (section.type === "messages") {
      return <div key={section.type}>
        <SectionMessages section={section}/>
      </div>;
    } else {
      return <div key={section.type}>
        <div className="alert alert-warning" role="alert">
          {terms.assessment_lint}
        </div>
        <SectionMessages section={section}/>
      </div>
    }
  });
}

const SectionMessages = ({section}) => {
  return section.messages.map((message, index) =>
    <div key={index}>
      <div dangerouslySetInnerHTML={{__html: message}} className={`assistant-${section.type}-message`}/>
      {index !== section.messages.length - 1 && <hr/>}
    </div>
  )
}

const Assistant = (assistant) => {
  const {messageSections, step, lastSeenMessageSections} = assistant;
  if (!step.requirements) {
    return null;
  }
  const newMessages = messageSections.some((section) => {
    if (section.type === "passed_tests" || !section.messages.length) {
      return false;
    }
    const lastSeenSection = lastSeenMessageSections.find(s => s.type === section.type);
    return section.messages.some((message) => !lastSeenSection?.messages.includes(message));
  });
  return <div className="assistant accordion">
    <Collapsible classParentString="assistant-requirements card"
                 contentInnerClassName="assistant-content card-body"
                 trigger={<div className="card-header">
                   <FontAwesomeIcon icon={faQuestionCircle}/> {terms.requirements}
                 </div>}
    >
      <Requirements requirements={step.requirements}/>
    </Collapsible>
    <Collapsible onOpening={openAssessment}
                 onClosing={() => bookSetState("assessmentOpen", false)}
                 classParentString="assistant-assessment card"
                 contentInnerClassName="assistant-content card-body"
                 trigger={<div className="card-header">
                   <FontAwesomeIcon icon={faListCheck}/> {terms.assessment} &nbsp;
                   {newMessages && <span className="badge badge-pill badge-danger">{terms.new}</span>}
                 </div>}
    >
      <Messages {...{ messageSections }}/>
    </Collapsible>
    <Collapsible classParentString="assistant-hints card"
                 contentInnerClassName="assistant-content card-body"
                 trigger={<div className="card-header">
                   <FontAwesomeIcon icon={faLightbulb}/> {terms.hints_and_solution}
                 </div>}
    >
      <HintsAssistant {...assistant}/>
    </Collapsible>
    <Collapsible classParentString="assistant-ai card"
                 contentInnerClassName="assistant-content card-body"
                 trigger={<div className="card-header">
                   <FontAwesomeIcon icon={faRobot}/> AI {/*terms.hints_and_solution TODO */}
                 </div>}
    >
      <AI {...assistant.ai}/>
    </Collapsible>
  </div>
}

const QuestionWizard = (
  {
    messages,
    requestExpectedOutput,
    expectedOutput,
  }) =>
  <>
    <h1>{terms.question_wizard}</h1>
    <div dangerouslySetInnerHTML={{ __html: terms.question_wizard_intro }}/>
    <hr/>
    {requestExpectedOutput && <>
      <div dangerouslySetInnerHTML={{__html: terms.question_wizard_expected_output}}/>
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
         if (button && event.currentTarget.contains(button) && button.classList.contains("copy-button")) {
           const codeElement = button.closest("code");
           let codeText = codeElement.textContent;
           codeText = codeText.substring(0, codeText.length - 1 - button.textContent.length);
           copyFunc(codeText);
         }
       }}
  />

const CourseText = (
  {
    user,
    step,
    page,
    pages,
    assistant,
  }) =>
    <>
    <h1 dangerouslySetInnerHTML={{__html: page.title}}/>
    {page.steps.map((part, index) =>
      <div
        key={index}
        id={`step-text-${index}`}
        className={index > 0 ? 'pt-3' : ''}
        style={index > step.index ? {display: 'none'} : {}}
      >
        <Markdown html={part.text} copyFunc={text => bookSetState("editorContent", text)}/>
        <hr style={{ margin: '0' }}/>
      </div>
    )}
      <Assistant {...assistant} step={step}/>
    {/* pt-3 is Bootstrap's helper class. Shorthand for padding-top: 1rem. Available classes are pt-{1-5} */}
    <div className='pt-3'>
      {page.index > 0 &&
      <button className="btn btn-primary previous-button"
              onClick={() => movePage(-1)}>
        {terms.previous}
      </button>}
      {" "}
      {page.index < Object.keys(pages).length - 1 && step.index === page.steps.length - 1 &&
      <button className="btn btn-success next-button"
              onClick={() => movePage(+1)}>
        {terms.next}
      </button>}
    </div>
    <br/>
    {
      user.developerMode && <StepButtons/>
    }
  </>

class AppComponent extends React.Component {
  render() {
    if (this.props.route === "toc") {
      return <TableOfContents/>
    }

    return <div className="book-container">
      <NavBar user={this.props.user}/>
      <ErrorBoundary canGiveFeedback>
        <AppMain {...this.props}/>
      </ErrorBoundary>
    </div>
  }
}

function NavBar({user}) {
  return <nav className="navbar navbar-expand-lg navbar-light bg-light">
        <span className="nav-item custom-popup">
          <MenuPopup user={user}/>
        </span>
    <span className="nav-item navbar-text">
          <HeaderLoginInfo email={user.email}/>
        </span>
    <a className="nav-item nav-link" href="#toc">
      <FontAwesomeIcon icon={faListOl}/> {terms.table_of_contents}
    </a>
  </nav>;
}

function AppMain(
  {
    editorContent,
    assistant,
    specialMessages,
    questionWizard,
    pages,
    user,
    prediction,
    route,
    previousRoute,
    running,
  }) {
  const isQuestionWizard = route === "question";
  const fullIde = route === "ide";

  const page = currentPage();
  const step = currentStep();

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
      (page.index === snoopPageIndex && step.index >= 1);
    showPythonTutor = page.index >= pages.UnderstandingProgramsWithPythonTutor.index;
    showBirdseye = page.index >= pages.IntroducingBirdseye.index;
    showQuestionButton = page.index > pages.IntroducingBirdseye.index;
  }

  const cantUseEditor = prediction.state === "waiting" || prediction.state === "showingResult";

  return <>
    {!fullIde &&
      <div className="book-text markdown-body">
        {isQuestionWizard ?
          <QuestionWizard {...questionWizard}/>
          :
          <div onCopy={checkCopy}>
            <CourseText
              {...{
                assistant,
                user,
                step,
                page,
                pages,
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
      running,
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

    {specialMessages.map((message, index) =>
      <Popup
        key={index}
        open={true}
        onClose={() => closeSpecialMessage(index)}
      >
        <SpecialMessageModal message={message}/>
      </Popup>
    )}
  </>;
}

const StepButton = ({delta, label}) =>
  <button className={`btn btn-danger btn-sm button-${label.replace(" ", "-").toLowerCase()}`}
          onClick={() => {
            const entry = {skip_step: delta, page_slug: bookState.user.pageSlug, step_name: currentStepName()};
            postCodeEntry(entry);
            logEvent('skip_step', entry);
            moveStep(delta);
          }}>
    {label}
  </button>

const StepButtons = () =>
  <div style={{position: "fixed", bottom: 0}}>
    <StepButton delta={-1} label={terms.reverse_step}/>
    {" "}
    <StepButton delta={+1} label={terms.skip_step}/>
  </div>


const MenuPopup = ({user}) =>
    <Popup
      nested
      trigger={
        <button className="btn btn-sm btn-outline-secondary">
          <FontAwesomeIcon icon={faBars} size="lg"/>
        </button>}
    >
      {close => <div className="menu-popup">
        {!disableLogin &&
          <p>
            <button
              className="btn btn-danger"
              onClick={() => {
                close();
                signOut();
                firebase.auth().signOut();
              }}
            >
              <FontAwesomeIcon icon={faSignOutAlt}/> {terms.sign_out}
            </button>
          </p>
        }
        <p>
          <Popup
            trigger={
              <button className="btn btn-primary">
                <FontAwesomeIcon icon={faCog}/> {terms.settings}
              </button>
              }
            modal
            nested
          >
            <SettingsModal user={user}/>
          </Popup>
        </p>
        <FeedbackMenuButton/>
        {
          otherVisibleLanguages.map(lang =>
            <p key={lang.code}>
              <a href={lang.url + "course/"} className="btn btn-link"
                 style={{borderColor: "grey"}}>
                <img
                  alt="language icon"
                  src={languageIcon}
                  width={24}
                  height={24}
                  style={{
                    display: "inline",
                    position: "relative",
                    top: "-2px",
                    left: "-2px",
                  }}
                /> {lang.name}
              </a>
            </p>
          )
        }
      </div>}
    </Popup>


const SettingsModal = ({user}) => (
  <div className="settings-modal">
    <h1>{terms.settings}</h1>
    <br/>
    <label>
      <Toggle
        defaultChecked={user.developerMode}
        onChange={(e) => setDeveloperMode(e.target.checked)}
      />
      <b>{terms.developer_mode}</b>
    </label>

    <p>{terms.developer_mode_description}</p>
  </div>
)

const SpecialMessageModal = ({message}) => (
  <div className="special-message-modal">
    <div dangerouslySetInnerHTML={{__html: message}}/>
  </div>
);

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
    addSpecialMessage(terms.copy_warning);
  }
}


export const App = connect(
  state => ({
    ...state.book,
  }),
)(AppComponent);

