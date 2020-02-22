import React from 'react';
import Terminal from './shell/Terminal';
import {rpc} from "./rpc";
import "./css/main.scss"
import "./css/github-markdown.css"
import {connect} from "react-redux";
import {
  bookSetState,
  bookState,
  closeMessage,
  getSolution,
  movePage,
  moveStep,
  ranCode,
  revealSolutionToken,
  showHint
} from "./book/store";
import hintIcon from "./img/hint.png"
import Popup from "reactjs-popup";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/theme-monokai";
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {faBug, faPlay, faTimes, faUserGraduate} from '@fortawesome/free-solid-svg-icons'
import {animateScroll} from "react-scroll";

class AppComponent extends React.Component {
  constructor(props) {
    super(props)
    this.terminal = React.createRef()
  }

  runCode({code, source}) {
    const shell = source === "shell";
    if (!shell && !code) {
      code = bookState.editorContent;
    }
    if (!code.trim()) {
      return;
    }
    bookSetState("processing", true);
    rpc(
      "run_code",
      {code, source},
      (data) => {
        if (!shell) {
          this.terminal.current.clearStdout();
        }
        bookSetState("processing", false);

        ranCode(data);
        const terminal = this.terminal.current;
        data.result.forEach((line) => terminal.pushToStdout(line))
        animateScroll.scrollToBottom({duration: 30, container: terminal.terminalRoot.current});
        terminal.focusTerminal();
      },
    );
  }

  render() {
    const {
      server,
      numHints,
      editorContent,
      messages,
      showingPageIndex,
      pages,
      solution,
      requestingSolution,
    } = this.props;
    let {
      step_index,
      hints,
      showEditor,
      showSnoop,
      showPythonTutor,
    } = server;
    const page = pages[showingPageIndex];
    if (showingPageIndex < server.page_index) {
      step_index = page.step_texts.length - 1;
    }
    return <div className="book-container">
      <div className="book-text markdown-body">
        <h1 dangerouslySetInnerHTML={{__html: page.title}}/>
        {page.step_texts.slice(0, step_index + 1).map((part, index) =>
          <div key={index} id={`step-text-${index}`}>
            <div dangerouslySetInnerHTML={{__html: part}}/>
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
          <button onClick={() => moveStep(-1)}>{"<-"}</button>
          <button onClick={() => moveStep(+1)}>{"->"}</button>
        </div>
        <div>
          {showingPageIndex > 0 &&
          <button className="btn btn-primary btn-sm" onClick={() => movePage(-1)}>Previous</button>}
          {" "}
          {showingPageIndex < pages.length - 1 && step_index === page.step_texts.length - 1 &&
          <button className="btn btn-success" onClick={() => movePage(+1)}>Next</button>}
        </div>
      </div>
      <div className="ide">
        <div className={"editor-buttons " + (showEditor ? "" : "invisible")}>
          <button
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
            className="btn btn-success"
            onClick={() => window.open(
              'https://pythontutor.com/iframe-embed.html#code=' + escape(bookState.editorContent) +
              '&codeDivHeight=600' +
              '&codeDivWidth=600' +
              '&cumulative=false' +
              '&curInstr=0' +
              '&heapPrimitives=false' +
              '&origin=opt-frontend.js' +
              '&py=3' +
              '&rawInputLstJSON=%5B%5D' +
              '&textReferences=false',
            )}
          >
            <FontAwesomeIcon icon={faUserGraduate}/> Python Tutor
          </button>}
        </div>
        <div className="editor-and-terminal">
          <div className={"editor " + (showEditor ? "" : "invisible")}>
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
            />
          </div>
          <div className="terminal">
            <Terminal
              onCommand={(cmd) => this.runCode({code: cmd, source: "shell"})}
              ref={this.terminal}
            />
          </div>
        </div>
      </div>

      {
        hints.length ?
          <Popup
            contentStyle={{
              position: "fixed",
              bottom: 50,
              right: 50,
            }}
            arrowStyle={{
              display: "none",
            }}
            trigger={<img src={hintIcon} className="hint-icon" alt="Hint button"/>}
          >
            {
              numHints === 0 ?
                <button onClick={showHint}>Get a hint</button>
                :
                <div className="markdown-body">
                  {hints.slice(0, numHints).map((hint, index) =>
                    <div>
                      <div key={index} dangerouslySetInnerHTML={{__html: hint}}/>
                      <hr/>
                    </div>
                  )}
                  <div>
                    {
                      numHints < hints.length ?
                        <button onClick={showHint}>
                          Get another hint
                        </button>
                        :
                        !requestingSolution ?
                          <button onClick={() => bookSetState("requestingSolution", true)}>
                            Show solution
                          </button>
                          : solution.tokens.length === 0 ?
                          <>
                            <p>Are you sure? You will learn much better if you can solve this yourself.</p>
                            <p>
                              <button onClick={getSolution} className="btn btn-primary">
                                Yes
                              </button>
                              {" "}
                              <button onClick={() => bookSetState("requestingSolution", false)}
                                      className="btn-default btn">
                                No
                              </button>
                            </p>
                          </>
                          :
                          <Solution solution={solution}/>

                    }
                  </div>
                </div>
            }

          </Popup>
          : null
      }

    </div>
  }
}

const Solution = ({solution}) => {
  return <div>
  <pre>
    {solution.tokens.map((token, tokenIndex) =>
      <span
        className={
          `solution-token-${solution.mask[tokenIndex]
            ? "hidden" : "visible"}`
        }
        key={tokenIndex}
      >
        {token}
      </span>
    )}
  </pre>
    {solution.maskedIndices.length > 0 &&
    <p>
      <button onClick={revealSolutionToken}>
        Reveal
      </button>
    </p>}
  </div>;
}

export const App = connect(
  state => state.book,
)(AppComponent);
