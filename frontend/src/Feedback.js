import React from 'react';
import {useInput} from "./frontendlib/HookInput";
import Popup from "reactjs-popup";
import {bookSetState, bookState} from "./book/store";
import axios from "axios";
import * as terms from "./terms.json"
import * as Sentry from "@sentry/react";
import {uuidv4} from "sync-message";


export const FeedbackModal = ({close, error}) => {
  let initialTitle, instructions;
  if (error) {
    initialTitle = error.title;
    instructions = <>
      <h3>{terms.report_error}</h3>
      <p>{terms.report_error_instructions}</p>
      <details>
        <summary>{terms.click_for_error_details}</summary>
        <pre>{error.details}</pre>
      </details>

    </>
  } else {
    initialTitle = "";
    instructions = <>
      <h3>{terms.give_feedback}</h3>
      <div dangerouslySetInnerHTML={{__html: terms.give_feedback_instructions}}/>
    </>
  }
  const email = useInput(bookState.user.email || "", {
    placeholder: terms.feedback_email_placeholder,
    type: 'text',
    className: 'form-control',
    style: {
      width: "100%",
    },
  });
  const title = useInput(initialTitle, {
    placeholder: terms.title,
    type: 'text',
    className: 'form-control',
    style: {
      width: "100%",
    },
  });
  const description = useInput('', {
    placeholder: terms.description,
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
            // Get the last actual event (if any) before we override it now
            const lastEvent = Sentry.lastEventId();
            // Create an artificial event so that user feedback can be attached to it.
            // Set a unique fingerprint to prevent grouping so that an email notification is triggered.
            Sentry.withScope(scope => {
              scope.setFingerprint([uuidv4()]);
              Sentry.captureMessage(`User feedback`);
            });
            const comments = `${email.value ? `Email: ${email.value}\n` : ''}
${lastEvent ? `Last event: ${lastEvent}\n` : ''}
${title.value.trim()}

${description.value.trim()}`;
            axios.post(
              'https://sentry.io/api/0/projects/futurecoder/frontend/user-feedback/',
              {
                event_id: Sentry.lastEventId(),  // the captureMessage event just now
                name: "John Doe",  // name and email are required by Sentry
                email: "john@example.com",
                comments,
              },
              {
                headers: {
                  Authorization: 'DSN ' + process.env.REACT_APP_SENTRY_DSN,
                }
              }
            );
            close();
          }}
        >
          {terms.submit}
        </button>

        <button
          className="btn btn-default"
          onClick={close}
        >
          {terms.cancel}
        </button>
      </div>
      <br/>
      <br/>
      <div>
        {terms.contact_directly}
        <ul>
          <li>
            <a href="mailto:hello@futurecoder.io">
              {terms.send_email_to} hello@futurecoder.io
            </a>
          </li>
          <li>
            <a href="https://github.com/alexmojaki/futurecoder/issues/new">
              {terms.open_github_issue}
            </a>
          </li>
          <li>
            <a href="https://join.slack.com/t/futurecoder/shared_invite/zt-tp8cmwra-CbdEeX9u3k1VyoMLDupAeQ">
              {terms.chat_on_slack}
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
  background: "white",
  border: "solid 1px lightgray",
}
