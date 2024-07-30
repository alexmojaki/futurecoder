import terms from "./terms.json";
import React from "react";
import _ from "lodash";

export const requirementText = (requirement, terms) => {
  let text;
  switch (requirement.type) {
    case "verbatim":
      text = terms.verbatim;
      break;
    case "exercise":
      text = terms.exercise_requirement;
      break;
    case "program_in_text":
      text = terms.program_in_text;
      break;
    case "function_exercise":
      text = _.template(terms.function_exercise)(requirement);
      break;
    case "function_exercise_goal":
      text = _.template(terms.function_exercise_goal)(requirement);
      break;
    case "exercise_stdin":
      text = terms.exercise_stdin;
      break;
    case "non_function_exercise":
      if (!requirement.inputs.trim()) {
        text = terms.no_input_variables;
      } else {
        text = _.template(terms.non_function_exercise)(requirement);
      }
      break;
    default:
      text = requirement.message;
      break;
  }
  return text;
}

export function Requirements({ requirements }) {
  return <>
    <p>
      {terms.requirements_description}
    </p>
    <ul>
      {requirements.map((requirement, index) =>
        <li key={index}>
          <Requirement requirement={requirement}/>
        </li>
      )}
    </ul>
  </>;
}

const Requirement = ({ requirement, }) => {
  return <div className="assistant-requirement"
              dangerouslySetInnerHTML={{ __html: requirementText(requirement, terms) }}/>
};
