import React from 'react';
import {bookSetState, getSolution, revealSolutionToken, showHint} from "./book/store";
import hintIcon from "./img/hint.png";
import Popup from "reactjs-popup";

export const HintsPopup = ({hints, numHints, requestingSolution, solution}) => {
  if (!hints.length) {
    return null;
  }
  return (
    <div className="custom-popup"
         onCopy={(event) => {
           alert("Copying from the hints/solution area is not allowed!");
           event.preventDefault();
         }}
    >
      <Popup
        trigger={<img src={hintIcon} className="hint-icon" alt="Hint button"/>}
      >
        <div className="hints-popup">
          {
            numHints === 0 ?
              <button onClick={showHint} className="btn btn-primary">Get a hint</button>
              :
              <Hints
                hints={hints}
                numHints={numHints}
                requestingSolution={requestingSolution}
                solution={solution}
              />
          }
        </div>
      </Popup>
    </div>
  )
}


const Hints = ({hints, numHints, requestingSolution, solution}) =>
  <div className="markdown-body">
    {hints.slice(0, numHints).map((hint, index) =>
      <div>
        <div key={index} dangerouslySetInnerHTML={{__html: hint}}/>
        <hr/>
      </div>
    )}
    <div>
      {
        numHints < hints.length ?
          <button onClick={showHint} className="btn btn-primary">
            Get another hint
          </button>
          :
          <RequestSolution
            requestingSolution={requestingSolution}
            solution={solution}
          />
      }
    </div>
  </div>


const RequestSolution = ({requestingSolution, solution}) => {
  if (!requestingSolution) {
    return (
      <button onClick={() => bookSetState("requestingSolution", true)} className="btn btn-primary">
        Show solution
      </button>
    )
  } else if (solution.tokens.length === 0) {
    return <ConfirmSolution/>
  } else {
    return <Solution solution={solution}/>
  }
}


const ConfirmSolution = () => <>
  <p>Are you sure? You will learn much better if you can solve this yourself.</p>
  <p>
    <button onClick={getSolution} className="btn btn-primary">
      Yes
    </button>
    {" "}
    <button onClick={() => bookSetState("requestingSolution", false)}
            className="btn-default btn">
      No
    </button>
  </p>
</>


const Solution = ({solution}) =>
  <div>
    <pre>
      <code>
        {solution.tokens.map((token, tokenIndex) =>
          <span
            className={
              `solution-token-${solution.mask[tokenIndex]
                ? "hidden" : "visible"}`
            }
            key={tokenIndex}
          >
            {token}
          </span>
        )}
    </code>
    </pre>
    {solution.maskedIndices.length > 0 &&
    <p>
      <button onClick={revealSolutionToken} className="btn btn-primary">
        Reveal
      </button>
    </p>}
  </div>
