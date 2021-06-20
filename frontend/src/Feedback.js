import React from 'react';
import {useInput} from "./frontendlib/HookInput";
import {redact} from "./frontendlib/redact"
import Popup from "reactjs-popup";
import _ from "lodash";
import {bookSetState, bookState} from "./book/store";
import axios from "axios";


export const FeedbackModal = ({close, error}) => {
  let initialTitle, instructions, descriptionExtra;
  if (error) {
    initialTitle = error.title;
    descriptionExtra = "\n\n```" + error.details + "```";
    instructions = <>
      <h3>Report error</h3>
      <p>
        Oops, something went wrong!
        Please describe what you were just doing and what steps someone can take
        to reproduce the problem, then click Submit. Or click Cancel to not send a report.
      </p>
      <details>
        <summary>Click for error details</summary>
        <pre>{error.details}</pre>
      </details>

    </>
  } else {
    initialTitle = "";
    descriptionExtra = "";
    instructions = <>
      <h3>Give feedback</h3>
      <p>Tell us what you like or don't like! If you're reporting a bug, give a detailed description of the problem:</p>
      <ul>
        <li>What were you doing before and when the problem occurred?</li>
        <li>What steps can someone take to reproduce it?</li>
        <li>What do you observe happening, and what do you expect to happen instead?</li>
      </ul>
    </>
  }
  const email = useInput(bookState.user.email || "", {
    placeholder: 'Email (optional, publicly visible)',
    type: 'text',
    className: 'form-control',
    style: {
      width: "100%",
    },
  });
  const title = useInput(initialTitle, {
    placeholder: 'Title',
    type: 'text',
    className: 'form-control',
    style: {
      width: "100%",
    },
  });
  const description = useInput('', {
    placeholder: 'Description',
    className: 'form-control',
    style: {
      width: "100%",
      minHeight: "8em",
    }
  }, 'textarea')
  return (
    <div style={{margin: "1em"}}>
      {instructions}

      <div>{email.input}</div>
      <br/>
      <div>{title.input}</div>
      <br/>
      <div>{description.input}</div>
      <br/>
      <div>
        <button
          className="btn btn-primary"
          disabled={!(title.value && description.value)}
          onClick={() => {
            const state = _.omit(redact.store.getState(), "book.pages")
            const body = `
**User Issue**
Email: ${email.value || "(not given)"}
User Agent: ${navigator.userAgent}

${description.value + descriptionExtra}

<details>

<summary>Redux state</summary>

<p>

\`\`\`json
${JSON.stringify(state)}
\`\`\`

</p>
</details>`
            axios.post(
              'https://api.github.com/repos/alexmojaki/futurecoder/issues',
              {title: title.value, body, labels: ['user', 'bug']},
              {
                headers: {
                  Authorization: 'token ' + process.env.REACT_APP_FEEDBACK_GITHUB_TOKEN,
                  Accept : 'application/vnd.github.v3+json'
                }
              }
            );
            close();
          }}
        >
          Submit
        </button>

        <button
          className="btn btn-default"
          onClick={close}
        >
          Cancel
        </button>
      </div>
      <br/>
      <br/>
      <div>
        Alternatively, you can contact us directly:
        <ul>
          <li>
            <a href="mailto:hello@futurecoder.io">
              Email hello@futurecoder.io
            </a>
          </li>
          <li>
            <a href="https://github.com/alexmojaki/futurecoder/issues/new">
              Open an issue on GitHub
            </a>
          </li>
          <li>
            <a href="https://join.slack.com/t/futurecoder/shared_invite/zt-l0zxo9d3-mimh7iTSaDB07hnePMNGFw">
              Chat on Slack
            </a>
          </li>
        </ul>
      </div>
    </div>
  );
};


export const ErrorModal = ({error}) => {
  if (!error) {
    return null;
  }
  return (
    <Popup
      open={true}
      closeOnDocumentClick
      onClose={() => bookSetState("error", null)}
      contentStyle={feedbackContentStyle}
    >
      {close => <FeedbackModal close={close} error={error}/>}
    </Popup>
  )
};


export const feedbackContentStyle = {
  maxHeight: "90vh",
  overflow: "auto",
}
