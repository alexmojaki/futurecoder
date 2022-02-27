import React from "react";
import _ from "lodash";
import {assert} from "./utilities";

// To set up, import connect from react-redux and set
// TextContainer.connect = connect

export const TextContainer = stateFn => {
  const TextComponent = ({text}) => (
    <span>{text}</span>
  );
  return TextContainer.connect(
    state => ({text: stateFn(state)}),
  )(TextComponent);
};

export const PathTextContainer = _.memoize(path => {
  assert(typeof path === 'string', "path must be a string");
  return TextContainer(state => _.get(state, path));
});

export const QuickText = path => {
  const QuickTextContainer = PathTextContainer(path);
  return <QuickTextContainer/>
};
