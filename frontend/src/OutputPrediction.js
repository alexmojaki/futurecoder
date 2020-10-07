import React, {Component} from "react";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCheck, faCircle, faDotCircle, faTimes} from "@fortawesome/free-solid-svg-icons";
import {bookSetState, bookStatePush, scrollToNextStep} from "./book/store";
import {showCodeResult, terminalRef} from "./App";
import Confetti from "react-dom-confetti";
import {animateScroll} from "react-scroll";
import _ from "lodash";

const RadioButton = ({onChange, label, status}) => (
  <div className={"prediction-choice prediction-" + status}
       onClick={onChange}>
    <FontAwesomeIcon
      icon={{
        selected: faDotCircle,
        wrong: faTimes,
        correct: faCheck,
        "": faCircle,
      }[status]}
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
    wrongAnswers,
    submitted
  }) => (
  <div>
    {choices.map((label, i) => {
      let status = "";
      if (_.includes(wrongAnswers, label)) {
        status = "wrong";
      } else if (submitted && correctAnswer === label) {
        status = "correct";
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

export class OutputPrediction extends Component {
  componentDidMount() {
    setTimeout(() => {
      const element = document.getElementsByClassName("output-prediction")[0];
      bookSetState("prediction.height", element.scrollHeight + "px");
    }, 100);
  }

  render() {
    const {
      choices,
      codeResult,
      state,
      userChoice,
      answer,
      wrongAnswers,
      height
    } = this.props.prediction;
    const confettiActive = state === "showingResult" && answer === userChoice;
    let message;
    if (state === "waiting") {
      if (wrongAnswers.length === 0) {
        message = "What do you think the result will be?";
      } else {
        message = "Oops, that's not right. You can try one more time!";
      }
    } else if (userChoice === answer) {
      message = "Correct!";
    } else {
      message = "Sorry, wrong answer. Try again next time!";
    }

    return <div
      className="output-prediction"
      style={{
        height: height,
        opacity: state === "waiting" || state === "showingResult" ? 1 : 0,
      }}
    >
      <RadioGroup
        choices={choices}
        onChange={value =>
          state === "waiting" &&
          !_.includes(wrongAnswers, value) &&
          bookSetState("prediction.userChoice", value)
        }
        value={userChoice}
        correctAnswer={answer}
        wrongAnswers={wrongAnswers}
        submitted={state === "showingResult" || state === "fading"}
      />
      <div className="submit-prediction">
        <CorrectConfetti active={confettiActive}/>
        <div><strong>{message}</strong></div>
        <button
          style={{opacity: state === "waiting" ? 1 : 0}}
          className="btn btn-primary"
          disabled={!userChoice}
          onClick={() => {
            if (userChoice !== answer) {
              bookStatePush("prediction.wrongAnswers", userChoice);
              if (wrongAnswers.length === 0) {
                bookSetState("prediction.userChoice", null);
                return;
              }
            }
            bookSetState("server", codeResult.state);
            scrollToNextStep();
            bookSetState("prediction.state", "showingResult");
            setTimeout(() => animateScroll.scrollToBottom({
              duration: 30,
              container: terminalRef.current.terminalRoot.current
            }))
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
    </div>
  }
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
