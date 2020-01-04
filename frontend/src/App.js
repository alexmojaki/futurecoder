import React from 'react';
import Terminal from './shell/Terminal';
import {rpc} from "./rpc";
import "./css/main.scss"
import "./css/github-markdown.css"
import {connect} from "react-redux";
import {bookSetState, bookState, closeMessage, movePage, ranCode, showHint} from "./book/store";
import hintIcon from "./img/hint.png"
import Popup from "reactjs-popup";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/theme-monokai";
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {faPlay, faTimes} from '@fortawesome/free-solid-svg-icons'
import {animateScroll} from "react-scroll";

class AppComponent extends React.Component {
  constructor(props) {
    super(props)
    this.terminal = React.createRef()
  }

  ranCode(data) {
    ranCode(data);
    const terminal = this.terminal.current;
    data.result.forEach((line) => terminal.pushToStdout(line))
    animateScroll.scrollToBottom({duration: 30, container: terminal.terminalRoot.current});
  }

  render() {
    const {
      server,
      numHints,
      editorContent,
      messages,
      showingPageIndex,
      pages,
    } = this.props;
    let {
      step_index,
      hints,
      showEditor,
    } = server;
    const page = pages[showingPageIndex];
    if (showingPageIndex < server.page_index) {
      step_index = page.step_texts.length - 1;
    }
    return <div className="book-container">
      <div className="book-text markdown-body">
        <h1>{page.title}</h1>
        {page.step_texts.slice(0, step_index + 1).map((part, index) =>
          <div key={index}>
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
        {/*<div>*/}
        {/*  <button onClick={() => moveStep(-1)}>{"<-"}</button>*/}
        {/*  <button onClick={() => moveStep(+1)}>{"->"}</button>*/}
        {/*</div>*/}
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
              rpc(
                "run_program",
                {code: bookState.editorContent},
                (data) => {
                  this.terminal.current.clearStdout();
                  return this.ranCode(data);
                },
              );
            }}
          >
            <FontAwesomeIcon icon={faPlay}/> Run
          </button>
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
              promptLabel=">>> "
              onCommand={(cmd) => rpc("shell_line", {line: cmd}, (data) => this.ranCode(data))}
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
                  {
                    numHints < hints.length ?
                      <div>
                        <button onClick={showHint}>Get another hint</button>
                      </div>
                      : null
                  }
                </div>
            }

          </Popup>
          : null
      }

    </div>
  }
}

export const App = connect(
  state => state.book,
)(AppComponent);
