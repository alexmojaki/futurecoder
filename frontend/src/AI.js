import ReactMarkdown from "react-markdown";
import {bookSetState, bookState, currentPage, currentStep} from "./book/store";
import {requirementText} from "./Requirements";
import terms from "./terms.json";
import React from "react";

export function AI({ chat }) {
  return <div>
    <ReactMarkdown>
      {chat}
    </ReactMarkdown>
    <button
      className="btn btn-primary"
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
        };
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
        bookSetState("assistant.chat", await res.text());
      }}>
      Send
    </button>
  </div>;
}
