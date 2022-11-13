import React from 'react';
import {useInput} from "./frontendlib/HookInput";
import {bookState} from "./book/store";
import axios from "axios";
import * as terms from "./terms.json"
import * as Sentry from "@sentry/react";
import {uuidv4} from "sync-message";
import Popup from "reactjs-popup";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faBug} from "@fortawesome/free-solid-svg-icons";
import _ from "lodash";

const SENTRY_DSN = process.env.REACT_APP_SENTRY_DSN;


const FeedbackModal = ({close}) => {
  const email = useInput(bookState.user.email || "", {
    placeholder: terms.feedback_email_placeholder,
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
      <h3>{terms.give_feedback}</h3>
      <div dangerouslySetInnerHTML={{__html: terms.give_feedback_instructions}}/>

      <div>{email.input}</div>
      <br/>
      <div>{description.input}</div>
      <br/>
      <div>
        <button
          className="btn btn-primary"
          disabled={!description.value}
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
                  Authorization: 'DSN ' + SENTRY_DSN,
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

const feedbackContentStyle = {
  maxHeight: "90vh",
  overflow: "auto",
  background: "white",
  border: "solid 1px lightgray",
}

export function FeedbackMenuButton() {
  if (!SENTRY_DSN) {
    return null;
  }
  return <p>
    <Popup
      trigger={
        <button className="btn btn-success">
          <FontAwesomeIcon icon={faBug}/> {terms.feedback}
        </button>
      }
      modal
      nested
      contentStyle={feedbackContentStyle}
    >
      {close => <FeedbackModal close={close}/>}
    </Popup>
  </p>;
}

export function InternalError({ranCode, canGiveFeedback}) {
  const start = _.template(terms.internal_error_start)({
    maybeErrorReported: SENTRY_DSN ? terms.error_has_been_reported : '',
  });
  const suggestions = [];
  if (ranCode) {
    suggestions.push(terms.try_running_code_again);
  }
  suggestions.push(terms.refresh_and_try_again, terms.try_using_different_browser);
  if (SENTRY_DSN && canGiveFeedback) {
    suggestions.push(terms.give_feedback_from_menu);
  }
  return <div>
    <p>{start}</p>
    <ul>
      {suggestions.map(suggestion => <li key={suggestion}>{suggestion}</li>)}
    </ul>
  </div>;
}

export function ErrorBoundary({children, canGiveFeedback}) {
  return <Sentry.ErrorBoundary fallback={
    ({error}) => <ErrorFallback {...{error, canGiveFeedback}}/>
  }>
    {children}
  </Sentry.ErrorBoundary>;
}

function ErrorFallback({error, canGiveFeedback}) {
  return <div style={{margin: "4em"}}>
    <div className="alert alert-danger" role="alert">
      <pre><code>{error.toString()}</code></pre>
    </div>
    <InternalError canGiveFeedback={canGiveFeedback}/>
  </div>;
}
