import React from 'react';
import Terminal from './shell/Terminal';
import {rpc} from "./rpc";
import "./css/main.scss"
import "./css/github-markdown.css"
import {connect} from "react-redux";
import {bookSetState, bookState, ranCode, moveStep, showHint} from "./book/store";
import hintIcon from "./img/hint.png"
import Popup from "reactjs-popup";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/theme-monokai";
import {FontAwesomeIcon} from '@fortawesome/react-fontawesome'
import {faPlay} from '@fortawesome/free-solid-svg-icons'
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
      server: {
        parts,
        progress,
        hints,
        showEditor,
      },
      numHints,
      editorContent,
    } = this.props;
    return <div className="book-container">
      <div className="book-text markdown-body">
        {parts.slice(0, progress + 1).map((part, index) =>
          <div key={index}>
            <div dangerouslySetInnerHTML={{__html: part}}/>
            <hr/>
          </div>
        )}
        <div>
          <button onClick={() => moveStep(-1)}>{"<-"}</button>
          <button onClick={() => moveStep(+1)}>{"->"}</button>
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
            {/*<Terminal*/}
            {/*  color='white'*/}
            {/*  prompt='white'*/}
            {/*  commandPassThrough={(cmd, print) => {*/}
            {/*    rpc("shell_line", {line: cmd}, ranCode);*/}
            {/*  }}*/}
            {/*  hideTopBar*/}
            {/*  allowTabs={false}*/}
            {/*  promptSymbol=">>>"*/}
            {/*/>*/}
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
