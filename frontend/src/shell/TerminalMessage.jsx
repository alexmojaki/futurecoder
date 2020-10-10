import React, {Component} from 'react'
import AnsiUp from "ansi_up";

import sourceStyles from './defs/styles/TerminalMessage'

const ansi_up = new AnsiUp();

export default class TerminalMessage extends Component {

  render() {
    let {content} = this.props;

    if (content.isTraceback) {
      return <div className="tracebacks-container">
        {
          content.data.map((traceback, tracebackIndex) =>
          <div className="traceback" key={tracebackIndex}>
            {
              traceback.frames.map((frame, frameIndex) =>
                <div className="traceback-frame" key={frameIndex}>
                  <div className="traceback-frame-name">{frame.name}:</div>
                  <table>
                    <tbody>
                    {
                      frame.lines.map(line =>
                        <tr key={line.lineno}>
                          <td className="traceback-lineno">{line.lineno}</td>
                          <td className="traceback-line-content codehilite" dangerouslySetInnerHTML={{__html: line.content}}/>
                        </tr>
                      )
                    }
                    </tbody>
                  </table>
                </div>
              )
            }
            <div className="traceback-exception">
              <strong>{traceback.exception.type}: </strong>{traceback.exception.message}
            </div>
          </div>
          )
        }
      </div>
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
