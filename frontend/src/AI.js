import ReactMarkdown from "react-markdown";
import {bookSetState, bookState, currentPage, currentStep} from "./book/store";
import {requirementText} from "./Requirements";
import terms from "./terms.json";
import React from "react";
import {useInput} from "./frontendlib/HookInput";
import LoadingIndicator from "./components/LoadingIndicator";

export function AI({ response, running }) {
  const userMessage = useInput("", {
    placeholder: "Enter message...",  // TODO terms
    type: 'text',
    className: 'form-control',
    style: {
      width: "100%",
    },
  });
  return <div>
    <div>
      {userMessage.input}
    </div>
    <br/>
    <button
      className="btn btn-primary"
      disabled={running}
      onClick={async () => {
        const page = currentPage();
        const step = currentStep();
        const requirements = step.requirements.map((requirement) =>
          requirementText(
            { ...requirement, ...(requirement.unparsed || {}) },
            terms.unparsed,
          ));
        const { editorContent, assistant } = bookState;
        const data = {
          page,
          stepName: step.name,
          requirements,
          editorContent,
          assistant,
          terms: terms.unparsed,
          userMessage: userMessage.value,
        };
        bookSetState("assistant.ai.running", true)
        const res = await fetch(
          "http://127.0.0.1:5001/futurecoder-io/us-central1/chat",
          {
            method: "POST",
            body: JSON.stringify(data),
            headers: {
              "Content-Type": "application/json",
            },
          }
        );
        bookSetState("assistant.ai.running", false)
        bookSetState("assistant.ai.response", await res.text());
        userMessage.setHookValue("");
      }}>
      {running ? <LoadingIndicator/> : "Send"}
    </button>
    <br/>
    <ReactMarkdown>
      {response}
    </ReactMarkdown>
  </div>;
}
