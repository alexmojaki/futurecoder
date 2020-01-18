import React, {Component} from 'react'
import AnsiUp from "ansi_up";

import sourceStyles from './defs/styles/TerminalMessage'

const ansi_up = new AnsiUp();

export default class TerminalMessage extends Component {

  render() {
    let {content} = this.props;
    let color = "white";
    if (typeof content === "object") {
      color = content.color;
      content = content.text;
    }

    const styles = {
      message: sourceStyles
    }

    return <p
      style={{...styles.message, color}}
      dangerouslySetInnerHTML={{__html: ansi_up.ansi_to_html(content)}}
    />
  }
}
