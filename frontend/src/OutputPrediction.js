import React from "react";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCircle, faDotCircle} from "@fortawesome/free-solid-svg-icons";
import {bookSetState} from "./book/store";
import {showCodeResult, terminalRef} from "./App";
import Confetti from "react-dom-confetti";
import {animateScroll} from "react-scroll";

const RadioButton = ({onChange, label, status}) => (
  <div className={"prediction-choice prediction-" + status}
       onClick={onChange}>
    <FontAwesomeIcon
      icon={status === "selected" ? faDotCircle : faCircle}
    />
    <div className="prediction-label" style={{color: label === "Error" ? "red" : "white"}}>
      {label}
    </div>
  </div>
);

const RadioGroup = (
  {
    choices,
    onChange,
    value,
    correctAnswer,
    submitted
  }) => (
  <div>
    {choices.map((label, i) => {
      let status = "";
      if (submitted) {
        if (correctAnswer === label) {
          status = "correct";
        } else if (value === label) {
          status = "wrong";
        }
      } else if (value === label) {
        status = "selected";
      }
      return (
        <RadioButton
          key={i}
          label={label}
          onChange={() => onChange(label)}
          status={status}
        />
      );
    })}
  </div>
);

export const OutputPrediction = (
  {
    prediction:
      {
        choices,
        codeResult,
        state,
        userChoice,
        answer,
        height
      }
  }
) => {
  if (state === "hidden") return null;

  const confettiActive = state === "showingResult" && answer === userChoice;
  return <div
    className="output-prediction"
    style={{
      height: height,
      opacity: state === "waiting" || state === "showingResult" ? 1 : 0,
    }}
  >
    <div>
      <strong>
        {
          state === "waiting" ?
            "What do you think the result will be?"
            :
            (
              userChoice === answer ?
                "Correct!"
                :
                "Sorry, wrong answer. Try again next time!"
            )
        }
      </strong>
      <CorrectConfetti active={confettiActive}/>
    </div>
    <RadioGroup
      choices={choices}
      onChange={value => state === "waiting" && bookSetState("prediction.userChoice", value)}
      value={userChoice}
      correctAnswer={answer}
      submitted={state === "showingResult" || state === "fading"}
    />
    <div style={{opacity: state === "waiting" ? 1 : 0}}>
      <button
        className="btn btn-primary"
        disabled={!userChoice}
        onClick={() => {
          bookSetState("server", codeResult.state);
          bookSetState("prediction.state", "showingResult");
          setTimeout(() => animateScroll.scrollToBottom({duration: 30, container: terminalRef.current.terminalRoot.current}))
          setTimeout(() => {
            bookSetState("prediction.state", "fading");
            bookSetState("prediction.height", 0);
            showCodeResult(codeResult);
          }, 3000);
          setTimeout(() => bookSetState("prediction.state", "hidden"), 4000);
        }}
      >
        Submit
      </button>
    </div>
    <CorrectConfetti active={confettiActive}/>
  </div>
}

const CorrectConfetti = ({active}) =>
  <Confetti
    active={active}
    config={{
      angle: "360",
      spread: 360,
      startVelocity: "32",
      elementCount: "117",
      dragFriction: "0.13",
      duration: "2500",
      stagger: "5",
      width: "17px",
      height: "18px",
      perspective: "0px",
      colors: [
        "#a864fd",
        "#29cdff",
        "#78ff44",
        "#ff718d",
        "#fdff6a",
      ]
    }}
  />
