import {ipush, iremove, iset, redact} from "../frontendlib";
import {rpc} from "../rpc";
import {scroller, animateScroll} from "react-scroll";
import _ from "lodash";

const initialState = {
  server: {
    step_index: 0,
    page_index: 0,
    hints: [],
    showEditor: false,
    showSnoop: false,
    showPythonTutor: false,
    showBirdseye: true,
  },
  pages: [
    {
      title: "Loading...",
      step_texts: [],
    }
  ],
  user: {
    email: "",
  },
  processing: false,
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


const {reducer, makeAction, setState, localState} = redact('book', initialState, {dispatched: true});

export {reducer as bookReducer, setState as bookSetState, localState as bookState};

const loadData = (data) => {
  if (!data.user) {
    window.location = "/accounts/login/?next=/course/"
  }
  setState("server", data.state);
  setState("pages", data.pages);
  setState("user", data.user);
  setState("showingPageIndex", data.state.page_index);
}

rpc("load_data", {}, loadData);

export const moveStep = (delta) => {
  rpc("move_step", {delta}, loadData);
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
      setTimeout(() =>
          scroller.scrollTo(`step-text-${value.state.step_index}`, {
            duration: 1000,
            smooth: true,
          }),
        500,
      )

      state = {
        ...state,
        ..._.pick(initialState, [(
          "numHints messages solution " +
          "requestingSolution").split(" ")]),
        server: value.state,
        processing: false,
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
