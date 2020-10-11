import React, {Component} from 'react'
import AnsiUp from "ansi_up";

import sourceStyles from './defs/styles/TerminalMessage'
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faInfoCircle} from "@fortawesome/free-solid-svg-icons";
import Popup from "reactjs-popup";

const ansi_up = new AnsiUp();

export default class TerminalMessage extends Component {

  render() {
    let {content} = this.props;

    if (content.isTraceback) {
      return <Tracebacks {...content}/>
    }

    let color = "white";
    if (typeof content === "object") {
      color = content.color;
      content = content.text;
    }

    const styles = {
      message: sourceStyles
    }

    return <span
      style={{...styles.message, color}}
      dangerouslySetInnerHTML={{__html: ansi_up.ansi_to_html(content)}}
    />
  }
}


const Tracebacks = ({tracebacks, codeSource}) => {
  const simple = (
    codeSource === "shell"
    && tracebacks.length === 1
    && tracebacks[0].frames.length === 1
  );
  return <div className="tracebacks-container">
    {!simple &&
      <div className="traceback-exception">
        <strong>Error traceback:</strong>
      </div>
    }
    {
      tracebacks.map((traceback, tracebackIndex) =>
        <div className="traceback" key={tracebackIndex}>
          {
            !simple && traceback.frames.map((frame, frameIndex) =>
              frame.type === "frame" ?
                <Frame frame={frame} key={frameIndex}/>
                :
                <RepeatedFrames data={frame.data} key={frameIndex}/>
            )
          }
          <div>
            <span className="traceback-exception">
              <strong>{traceback.exception.type}: </strong>{traceback.exception.message}
            </span>
            {" "}
            <Popup
              trigger={
                <span className="friendly-traceback-info">
                  <FontAwesomeIcon icon={faInfoCircle}/>
                </span>
              }
              position="top right"
              on={['hover', 'focus']}
              arrow={false}
              contentStyle={{
                width: "30em",
                border: "10px solid grey",
                zIndex: 5
              }}
            >
              <div className="markdown-body friendly-traceback-popup"
                   dangerouslySetInnerHTML={{__html: traceback.friendly}}/>
            </Popup>
          </div>
          {
            traceback.didyoumean.length > 0 &&
            <div className="traceback-didyoumean">
              <i>Did you mean...</i>
              <ul>
                {
                  traceback.didyoumean.map((suggestion, suggestionIndex) =>
                    <li key={suggestionIndex}>{suggestion}?</li>
                  )
                }
              </ul>
            </div>
          }
          {
            traceback.tail && <div className="traceback-tail">{traceback.tail}</div>
          }
        </div>
      )
    }
  </div>;
}

const Frame = ({frame}) =>
  <div className="traceback-frame">
    {frame.name !== "<module>" && <div className="traceback-frame-name">{frame.name}:</div>}
    <table className="traceback-lines-table">
      <tbody>
      {
        frame.lines.map(line =>
          <tr key={line.lineno}>
            <td className="traceback-lineno">{line.lineno}</td>
            <td className="traceback-line-content codehilite"
                dangerouslySetInnerHTML={{__html: line.content}}/>
          </tr>
        )
      }
      </tbody>
    </table>
    <table className="traceback-variables-table">
      <tbody>
      {
        frame.variables.map((variable, variableIndex) =>
          <tr key={variableIndex}>
            <td className="traceback-variable-name codehilite"
                dangerouslySetInnerHTML={{__html: variable.name}}/>
            <td className="traceback-variable-value codehilite"
                dangerouslySetInnerHTML={{__html: variable.value}}/>
          </tr>
        )
      }
      </tbody>
    </table>
  </div>


const RepeatedFrames = ({data}) =>
  <div className="traceback-repeated-frames">
    <div>Similar frames skipped:</div>
    <ul>
      {
        data.map((item, itemIndex) =>
        <li key={itemIndex}>
          {`${item.name} at line ${item.lineno} (${item.count} times)`}
        </li>)
      }
    </ul>
  </div>
