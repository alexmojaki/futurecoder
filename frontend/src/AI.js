import ReactMarkdown from "react-markdown";
import {bookState, currentPage, currentStep, receiveAiMessage, sendAiMessage} from "./book/store";
import {requirementText} from "./Requirements";
import terms from "./terms.json";
import React from "react";
import {useInput} from "./frontendlib/HookInput";
import LoadingIndicator from "./components/LoadingIndicator";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faPaperPlane} from "@fortawesome/free-solid-svg-icons";

export function AI({ messages, running }) {
  const userMessage = useInput("", {
    placeholder: "Enter message...",  // TODO terms
    type: 'text',
    className: 'form-control',
    style: {
      width: "100%",
    },
  });
  return <div>
    {messages.map((message, index) =>
      <div key={index}>
        {message.role === "user" ?
          <>
            <strong>You:</strong> {message.content}
          </>
          :
          <ReactMarkdown>
            {"**Bot:** " + message.content}
          </ReactMarkdown>
        }
        <hr/>
      </div>
    )}
    <form onSubmit={async (e) => {
      e.preventDefault();
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
      sendAiMessage(userMessage.value);
      userMessage.setHookValue("");
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
      const response = await res.text();
      receiveAiMessage(response);
    }}>
      <div>
        {userMessage.input}
      </div>
      <br/>
      <button
        type="submit"
        className="btn btn-primary"
        disabled={running}
      >
        {running ?
          <LoadingIndicator/> :
          <>
            <FontAwesomeIcon icon={faPaperPlane}/> Send {/* TODO terms */}
          </>
        }
      </button>
    </form>
  </div>;
}
