import React, {Component} from 'react'
import html from 'react-inner-html'

import sourceStyles from './defs/styles/TerminalMessage'

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

    return <p style={{...styles.message, color}}>{content}</p>
  }
}
