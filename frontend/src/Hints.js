import React from "react";
import {bookSetState, reorderSolutionLines, revealSolutionToken, showHint} from "./book/store";
import {DragDropContext, Draggable, Droppable} from "react-beautiful-dnd";
import * as terms from "./terms.json"
import _ from "lodash";

export const HintsAssistant = (assistant) => {
  if (!assistant.step.hints.length) {
    return null;
  }
  return (
    <div
         onCopy={(event) => {
           alert(terms.copying_solution_not_allowed);
           event.preventDefault();
         }}
    >
        <div className="hints-popup">
          {
            assistant.numHints === 0 ?
              <button onClick={showHint} className="btn btn-primary">{terms.get_hint}</button>
              :
              <Hints {...assistant}/>
          }
        </div>
    </div>
  )
}

const hintsProgress = _.template(terms.hints_progress);

const Hints = ({step: {hints, solution}, numHints, requestingSolution}) =>
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
            {terms.get_another_hint}
          </button>
          :
          <RequestSolution1
            requestingSolution={requestingSolution}
            solution={solution}
          />
      }
    </div>
    {
      numHints < hints.length &&
      <span className="small">{hintsProgress({numHints, totalHints: hints.length})}</span>
    }
  </div>


const RequestSolution1 = ({requestingSolution, solution}) => {
  if (requestingSolution === 0) {
    return (
      <button onClick={() => bookSetState("requestingSolution", solution.lines ? 1 : 3)} className="btn btn-primary">
        {solution.lines ?
          terms.show_shuffled_solution :
          terms.show_solution}
      </button>
    )
  } else if (requestingSolution === 1) {
    return <ConfirmSolution1/>
  } else {
    return <>
      {solution.lines && <>
        <Parsons lines={solution.lines}/>
        <p>{" "}</p>
        <p>{terms.parsons_solution_instructions}</p>
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
      {solution.lines ?
        terms.show_unscrambled_solution :
        terms.show_solution}
    </button>
  } else if (requestingSolution === 3) {
    return <ConfirmSolution2/>
  } else {
    return <Solution solution={solution}/>
  }

}


const ConfirmSolution1 = () => <>
  <p>{terms.are_you_sure}</p>
  <p>
    <button onClick={() => bookSetState("requestingSolution", 2)} className="btn btn-primary">
      {terms.yes}
    </button>
    {" "}
    <button onClick={() => bookSetState("requestingSolution", 0)}
            className="btn-default btn">
      {terms.no}
    </button>
  </p>
</>


const ConfirmSolution2 = () => <>
  <p>{terms.are_you_sure}</p>
  <p>
    <button onClick={() => bookSetState("requestingSolution", 4)} className="btn btn-primary">
      {terms.yes}
    </button>
    {" "}
    <button onClick={() => bookSetState("requestingSolution", 2)}
            className="btn-default btn">
      {terms.no}
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
      <p>{terms.hidden_solution_instructions}</p>
      <p>
        <button onClick={revealSolutionToken} className="btn btn-primary">
          {terms.reveal}
        </button>
      </p>
    </>}
  </div>
