import React from 'react';
import {useInput} from "./frontendlib/HookInput";
import {rpc} from "./rpc";
import {redact} from "./frontendlib/redact"


export const FeedbackModal = ({close}) => {
  const title = useInput('', {
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
      <h3>Give feedback</h3>
      <p>Tell us what you like or don't like! If you're reporting a bug, give a detailed description of the problem:</p>
      <ul>
        <li>What were you doing before and when the problem occurred?</li>
        <li>What steps can someone take to reproduce it?</li>
        <li>What do you observe happening, and what do you expect to happen instead?</li>
      </ul>

      <div>{title.input}</div>
      <br/>
      <div>{description.input}</div>
      <br/>
      <div>
        <button
          className="btn btn-primary"
          disabled={!(title.value && description.value)}
          onClick={() => {
            rpc("submit_feedback",
              {
                title: title.value,
                description: description.value,
                state: redact.store.getState(),
              });
            close();
          }}
        >
          Submit
        </button>
      </div>
    </div>
  );
};

