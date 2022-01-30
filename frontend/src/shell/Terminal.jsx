import React, {Component} from 'react'
import defaults from 'defaults'
import isEqual from 'react-fast-compare'
// Components
import TerminalMessage from './TerminalMessage'
// Handlers
import validateCommands from './handlers/validateCommands'
import scrollHistory from './handlers/scrollHistory'
// Definitions
import sourceStyles from './defs/styles/Terminal'
import types from './defs/types/Terminal'
import {bookState} from "../book/store";
import {OutputPrediction} from "../OutputPrediction";

export default class Terminal extends Component {
  constructor(props) {
    super(props);
    this.state = {
      commands: {},
      stdout: [],
      history: [],
      historyPosition: null,
      previousHistoryPosition: null,
      processing: false
    };

    this.terminalRoot = React.createRef();
    this.terminalInput = React.createRef();

    this.focusTerminal = this.focusTerminal.bind(this);
    this.validateCommands = this.validateCommands.bind(this);
    this.showWelcomeMessage = this.showWelcomeMessage.bind(this);
    this.showHelp = this.showHelp.bind(this);
    this.pushToStdout = this.pushToStdout.bind(this);
    this.getStdout = this.getStdout.bind(this);
    this.clearStdout = this.clearStdout.bind(this);
    this.processCommand = this.processCommand.bind(this);
    this.handleInput = this.handleInput.bind(this)
  }

  static propTypes = types;

  /* istanbul ignore next: Covered by interactivity tests */
  focusTerminal() {
    // Only focus the terminal if text isn't being copied
    const isTextSelected = window.getSelection().type === 'Range';
    const input = this.terminalInput.current;
    if (!isTextSelected && input) input.focus()
  }

  /* istanbul ignore next: Covered by interactivity tests */
  scrollToBottom() {
    const rootNode = this.terminalRoot.current;

    // This may look ridiculous, but it is necessary to decouple execution for just a millisecond in order to scroll all the way
    [1, 10, 50, 100, 200, 300, 400, 500, 600, 700, 800, 900].forEach(timeout =>
      setTimeout(() => {
        rootNode.scrollTop = rootNode.scrollHeight
      }, timeout)
    )
  }

  validateCommands() {
    const validCommands = validateCommands(
      this.props.commands,
      this.showHelp,
      this.clearStdout,
      this.props.noDefaults
    );

    this.setState({commands: validCommands})
  }

  showWelcomeMessage() {
    const msg = this.props.welcomeMessage;

    if (typeof msg === 'boolean') this.pushToStdout('Welcome to the React terminal! Type \'help\' to get a list of commands.');
    else if (Array.isArray(msg)) msg.map(item => this.pushToStdout(item));
    else this.pushToStdout(msg)
  }

  /* istanbul ignore next: Covered by interactivity tests */
  showHelp() {
    const {commands} = this.state;

    for (const c in commands) {
      const cmdObj = commands[c];
      const usage = cmdObj.usage ? ` - ${cmdObj.usage}` : '';

      this.pushToStdout(`${c} - ${cmdObj.description}${usage}`)
    }
  }

  pushToStdout(message, rawInput) {
    const {stdout, history} = this.state;

    if (message instanceof Array) {
      stdout.push(...message);
    } else {
      stdout.push(message);
    }

    /* istanbul ignore if: Covered by interactivity tests */
    if (rawInput) { // Only supplied if history is enabled
      history.push(rawInput);
      this.setState({stdout: stdout, history: history, historyPosition: null})
    } else {
      this.setState({stdout: stdout})
    }
  }

  getStdout() {
    return this.state.stdout.map((line, i) => <TerminalMessage key={i} content={line}/>)
  }

  /* istanbul ignore next: Covered by interactivity tests */
  clearStdout() {
    this.setState({stdout: []})
  }

  /* istanbul ignore next: Covered by interactivity tests */
  clearInput() {
    this.setState({historyPosition: null});
    this.terminalInput.current.value = ''
  }

  /* istanbul ignore next: Covered by interactivity tests */
  processCommand() {
    this.setState({processing: true}, () => {
      // Initialise command result object
      const commandResult = {command: null, args: [], rawInput: null, result: null};
      const rawInput = this.terminalInput.current.value;

      if (!this.props.noAutomaticStdout) {

        const message = rawInput + '\n';
        if (!this.props.noHistory) this.pushToStdout(message, rawInput);
        else this.pushToStdout(message)
      }

      commandResult.rawInput = rawInput;
      commandResult.result = this.props.onCommand(rawInput, this.pushToStdout);

      this.setState({processing: false}, () => {
        this.clearInput();
        if (!this.props.noAutoScroll) this.scrollToBottom();
        if (this.props.commandCallback) this.props.commandCallback(commandResult)
      })
    })
  }

  /* istanbul ignore next: Covered by interactivity tests */
  scrollHistory(direction) {
    const toUpdate = scrollHistory(
      direction,
      this.state.history,
      this.state.historyPosition,
      this.state.previousHistoryPosition,
      this.terminalInput,
      this.props.noAutomaticStdout
    );

    this.setState(toUpdate);
    const input = this.terminalInput.current;
    setTimeout(() => {
      // Move cursor to end
      input.selectionStart = input.selectionEnd = 10000;
    }, 30);
  }

  /* istanbul ignore next: Covered by interactivity tests */
  handleInput(event) {
    switch (event.key) {
      case 'Enter':
        if (!(event.ctrlKey || event.metaKey)) {
          this.processCommand();
        }
        break;
      case 'ArrowUp':
        this.scrollHistory('up');
        break;
      case 'ArrowDown':
        this.scrollHistory('down');
        break
    }
  }

  componentDidUpdate(prevProps) {
    // If there was a change in commands, re-validate
    if (!isEqual(prevProps.commands, this.props.commands)) this.validateCommands()
  }

  componentDidMount() {
    this.validateCommands();
    if (this.props.welcomeMessage) this.showWelcomeMessage();
    /* istanbul ignore next: Covered by interactivity tests */
    if (this.props.autoFocus) this.focusTerminal()
    this.pushToStdout(">>> ");
  }

  render() {
    const styles = {
      container: defaults(this.props.style, sourceStyles.container),
      content: defaults(this.props.contentStyle, sourceStyles.content),
      inputArea: defaults(this.props.inputAreaStyle, sourceStyles.inputArea),
      promptLabel: defaults(this.props.promptLabelStyle, sourceStyles.promptLabel),
      input: defaults(this.props.inputStyle, sourceStyles.input)
    };

    return (
      <div
        ref={this.terminalRoot}
        name={'react-console-emulator'}
        className={this.props.className}
        style={styles.container}
        onClick={this.focusTerminal}
      >
        {/* Content */}
        <div
          name={'react-console-emulator__content'}
          className={this.props.contentClassName}
          style={styles.content}
        >
          {/* Stdout */}
          {this.getStdout()}
          {/* Input area */}
          <div
            name={'react-console-emulator__inputArea'}
            className={this.props.inputAreaClassName}
            style={styles.inputArea}
          >
            {/* Input */}
            {bookState.processing &&
            <div className="lds-ellipsis">
              <div/>
              <div/>
              <div/>
              <div/>
            </div>}

            {bookState.prediction.state !== "waiting" && bookState.prediction.state !== "showingResult" &&
            <input
              ref={this.terminalInput}
              name={'react-console-emulator__input'}
              className={this.props.inputClassName}
              style={styles.input}
              onKeyDown={this.handleInput}
              type={'text'}
              autoComplete={'off'}
              disabled={bookState.processing}
            />
            }
          </div>

          {
            bookState.prediction.state !== "hidden" &&
            <OutputPrediction prediction={bookState.prediction}/>

          }
        </div>
      </div>
    )
  }
}
