import {ipush, iremove, iset, redact} from "../frontendlib";
import {rpc} from "../rpc";
import {animateScroll} from "react-scroll";
import _ from "lodash";

const initialState = {
  server: {
    step_index: 0,
    page_index: 0,
    hints: [],
    showEditor: false,
    showSnoop: false,
    showPythonTutor: false,
  },
  pages: [
    {
      title: "Loading...",
      step_texts: [],
    }
  ],
  numHints: 0,
  editorContent: "",
  messages: [],
  pastMessages: [],
  showingPageIndex: 0,
  requestingSolution: false,
  solution: {
    tokens: [],
    maskedIndices: [],
    mask: [],
  }
};


const {reducer, makeAction, setState, localState} = redact('rpc', initialState, {dispatched: true});

export {reducer as bookReducer, setState as bookSetState, localState as bookState};

rpc("load_data", {}, (data) => {
  setState("server", data.state);
  setState("pages", data.pages);
  setState("showingPageIndex", data.state.page_index);
});

export const moveStep = (delta) => {
  rpc("move_step", {delta});
  setState("server.step_index", localState.server.step_index + delta);
};

export const movePage = (delta) => {
  const newIndex = localState.showingPageIndex + delta;
  if (newIndex > localState.server.page_index) {
    setState("server.step_index", 0);
    setState("server.page_index", newIndex);
    rpc("next_page", {}, (data) => setState("server", data));
  }
  setState("showingPageIndex", newIndex);
  animateScroll.scrollToTop({delay: 0, duration: 0});
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
    if (state.server.step_index < value.state.step_index) {
      animateScroll.scrollToBottom({duration: 1000, delay: 500});
      state = {
        ...state,
        ..._.pick(initialState, [(
          "numHints messages solution " +
          "requestingSolution").split(" ")]),
        server: value.state,
      };
    }
    if (value.message && state.pastMessages.indexOf(value.message) === -1) {
      animateScroll.scrollToBottom({duration: 1000, delay: 500});
      state = ipush(state, "messages", value.message);
      state = ipush(state, "pastMessages", value.message);
    }
    return state;
  },
);

export const closeMessage = makeAction(
  'CLOSE_MESSAGE',
  (state, {value}) => iremove(state, "messages", value)
)

export const getSolution = () => {
  rpc("get_solution", {},
    (data) => {
      setState('solution', data)
    },
  );
}

export const revealSolutionToken = makeAction(
  "REVEAL_SOLUTION_TOKEN",
  (state) => {
    const indices = state.solution.maskedIndices;
    if (!indices.length) {
      return state;
    }
    state = iremove(state, "solution.maskedIndices", 0);
    state = iset(state, ["solution", "mask", indices[0]], false);
    return state;
  }
)
