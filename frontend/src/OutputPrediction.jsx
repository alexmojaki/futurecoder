import React, {Component} from "react";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import {faCheck, faCircle, faDotCircle, faTimes} from "@fortawesome/free-solid-svg-icons";
import {bookSetState, bookStatePush, scrollToNextStep} from "./book/store";
import {showCodeResult, terminalRef} from "./RunCode";
import Confetti from "react-dom-confetti";
import {animateScroll} from "react-scroll";
import _ from "lodash";
import * as terms from "./terms.json"

const RadioButton = ({onChange, label, status, isError}) => (
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
    <div className="prediction-label" style={{color: isError ? "red" : "white"}}>
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
          isError={i === choices.length - 1}
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
        message = terms.output_prediction_question;
      } else {
        message = terms.output_prediction_wrong_once;
      }
    } else if (userChoice === answer) {
      message = terms.output_prediction_correct;
    } else {
      message = terms.output_prediction_wrong_twice;
    }

    const userFailed = wrongAnswers.length === 2;
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
          style={{
            opacity:
              state === "waiting" ||
              (state === "showingResult" && userFailed)
                ? 1 : 0
          }}
          className="btn btn-primary"
          disabled={!userChoice && !userFailed}
          onClick={() => {
            if (userChoice !== answer && !userFailed) {
              bookStatePush("prediction.wrongAnswers", userChoice);
              bookSetState("prediction.userChoice", null);
              if (wrongAnswers.length === 1) {
                bookSetState("prediction.state", "showingResult");
              }
              return;
            }
            scrollToNextStep();
            bookSetState("prediction.state", "showingResult");
            setTimeout(() => animateScroll.scrollToBottom({
              duration: 30,
              container: terminalRef.current.terminalRoot.current
            }));
            const timeToFade = userFailed ? 0 : 3000;
            setTimeout(() => {
              bookSetState("prediction.state", "fading");
              bookSetState("prediction.height", 0);
              showCodeResult(codeResult);
            }, timeToFade);
            setTimeout(() => bookSetState("prediction.state", "hidden"), timeToFade + 1000);
          }}
        >
          {userFailed ? terms.ok : terms.submit}
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
      colors: [
        "#a864fd",
        "#29cdff",
        "#78ff44",
        "#ff718d",
        "#fdff6a",
      ]
    }}
  />
