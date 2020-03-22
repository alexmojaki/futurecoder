import React from 'react';
import {useInput} from "./frontendlib/HookInput";
import {rpc} from "./rpc";
import {redact} from "./frontendlib/redact"
import {stateSet as rpcStateSet} from "./rpc/store";
import Popup from "reactjs-popup";


export const FeedbackModal = ({close, error}) => {
  let initialTitle, instructions, descriptionExtra;
  if (error) {
    initialTitle = `Error in RPC method ${error.method}`;
    const details = `
Method: ${error.method}
Request data: ${JSON.stringify(error.data, null, 4)}

${error.traceback}
`;
    descriptionExtra = "\n\n```" + details + "```";
    instructions = <>
      <h3>Report error</h3>
      <p>
        There was an error processing your request on the server!
        Please describe what you were just doing and what steps someone can take
        to reproduce the problem, then click Submit. Or click Cancel to not send a report.
      </p>
      <details>
        <summary>Click for error details</summary>
        <pre>{details}</pre>
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
                description: description.value + descriptionExtra,
                state: redact.store.getState(),
              });
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
      onClose={() => rpcStateSet("error", null)}
    >
      {close => <FeedbackModal close={close} error={error}/>}
    </Popup>
  )
};
