import {redact} from "../frontendlib";
import {rpc} from "../rpc";
import {animateScroll} from "react-scroll";

const initialState = {
  server: {
    parts: [],
    progress: 0,
    hints: [],
    showEditor: false,
  },
  numHints: 0,
  editorContent: "",
};


const {reducer, makeAction, setState, localState} = redact('rpc', initialState, {dispatched: true});

export {reducer as bookReducer, setState as bookSetState, localState as bookState};

rpc("load_data", {}, (data) => {
  return setState("server", data);
});

export const moveStep = (delta) => {
  rpc("move_step", {delta});
  setState("server.progress", localState.server.progress + delta);
};

export const showHint = makeAction(
  'SHOW_HINT',
  (state) => {
    return {
      ...state,
      numHints: state.numHints + 1,
    };
  },
);

export const ranCode = makeAction(
  'RAN_CODE',
  (state, {value}) => {
    if (state.server.progress < value.progress) {
      animateScroll.scrollToBottom({duration: 1000, delay: 500});
      state = {
        ...state,
        numHints: 0,
        server: {
          ...state.server,
          progress: value.progress,
          hints: value.hints,
          showEditor: value.showEditor,
        }
      };
    }
    return state;
  },
);
