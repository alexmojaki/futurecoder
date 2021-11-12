import React from "react";
import {bookSetState, reorderSolutionLines, revealSolutionToken, showHint} from "./book/store";
import hintIcon from "./img/hint.png";
import Popup from "reactjs-popup";
import {DragDropContext, Draggable, Droppable} from "react-beautiful-dnd";

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
      <div className="hint-body" key={index}>
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
          <RequestSolution1
            requestingSolution={requestingSolution}
            solution={solution}
          />
      }
    </div>
    {
      numHints !== hints.length &&
      <span className="small">Shown {numHints} of {hints.length} hints.</span>
    }
  </div>


const RequestSolution1 = ({requestingSolution, solution}) => {
  if (requestingSolution === 0) {
    return (
      <button onClick={() => bookSetState("requestingSolution", solution.lines ? 1 : 3)} className="btn btn-primary">
        Show {solution.lines && "shuffled"} solution
      </button>
    )
  } else if (requestingSolution === 1) {
    return <ConfirmSolution1/>
  } else {
    return <>
      {solution.lines && <>
        <Parsons lines={solution.lines}/>
        <p>{" "}</p>
        <p>
          Above is an example solution with the lines out of order. You can drag them around to reorder them.
          Finding a correct order is up to you, and we won't will tell you if you get it right.
          Experimenting and running partial solutions in the editor may help you figure it out.
          You still need to type a correct solution into the editor and run it to continue.
        </p>
      </>}
      <RequestSolution2
        requestingSolution={requestingSolution}
        solution={solution}
      />
    </>
  }
}


const RequestSolution2 = ({requestingSolution, solution}) => {
  if (requestingSolution === 2) {
    return <button onClick={() => bookSetState("requestingSolution", 3)} className="btn btn-primary">
        Show {solution.lines && "unscrambled"} solution
    </button>
  } else if (requestingSolution === 3) {
    return <ConfirmSolution2/>
  } else {
    return <Solution solution={solution}/>
  }

}


const ConfirmSolution1 = () => <>
  <p>Are you sure?</p>
  <p>
    <button onClick={() => bookSetState("requestingSolution", 2)} className="btn btn-primary">
      Yes
    </button>
    {" "}
    <button onClick={() => bookSetState("requestingSolution", 0)}
            className="btn-default btn">
      No
    </button>
  </p>
</>


const ConfirmSolution2 = () => <>
  <p>Are you sure?</p>
  <p>
    <button onClick={() => bookSetState("requestingSolution", 4)} className="btn btn-primary">
      Yes
    </button>
    {" "}
    <button onClick={() => bookSetState("requestingSolution", 2)}
            className="btn-default btn">
      No
    </button>
  </p>
</>


const Parsons = ({lines}) =>
  <DragDropContext
    onDragEnd={(result) => {
      if (result.destination) {
        reorderSolutionLines(
          result.source.index,
          result.destination.index
        )
      }
    }}>
    <Droppable droppableId="droppable">
      {(provided) => (
        <div
          className="parsons-droppable"
          {...provided.droppableProps}
          ref={provided.innerRef}
        >
          {lines.map((line, index) => (
            <Draggable key={line.id} draggableId={line.id} index={index}>
              {(provided) => (
                <div
                  ref={provided.innerRef}
                  {...provided.draggableProps}
                  {...provided.dragHandleProps}
                  style={provided.draggableProps.style}
                >
                  <pre>
                    <code className="codehilite"
                          dangerouslySetInnerHTML={{__html: line.content}}/>
                  </pre>
                </div>
              )}
            </Draggable>
          ))}
          {provided.placeholder}
        </div>
      )}
    </Droppable>
  </DragDropContext>


const Solution = ({solution}) =>
  <div className="gradual-solution">
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
    <>
      <p>
        Above is an example solution, but it's hidden. Click the Reveal button repeatedly
        to reveal the solution bit by bit. Try to stop when you think you've revealed
        enough and can fill in the remaining gaps yourself. Then type a solution in the
        editor and run it. Your solution doesn't have to be the same as the one above.
      </p>
      <p>
        <button onClick={revealSolutionToken} className="btn btn-primary">
          Reveal
        </button>
      </p>
    </>}
  </div>
