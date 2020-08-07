import {ipush, iremove, iset, redact} from "../frontendlib";
import {rpc} from "../rpc";
import {animateScroll, scroller} from "react-scroll";
import _ from "lodash";

const initialState = {
  server: {
    pages_progress: {},
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
    developerMode: false,
  },
  processing: false,
  numHints: 0,
  editorContent: "",
  messages: [],
  pastMessages: [],
  requestingSolution: false,
  solution: {
    tokens: [],
    maskedIndices: [],
    mask: [],
  }
};


const {reducer, makeAction, setState, localState} = redact('book', initialState, {dispatched: true});

export {reducer as bookReducer, setState as bookSetState, localState as bookState};

export const stepIndex = (state = localState.server) => state.pages_progress[state.page_index];

const set_server_page = (index) => rpc(
  "set_page",
  {index},
  (data) => setState("server", data),
);

const loadData = (data) => {
  if (!data.user) {
    window.location = '/accounts/login/?next='
      + window.location.pathname
      + window.location.search;
  }
  const fresh = localState.pages.length === 1;
  setState("pages", data.pages);
  setState("server", data.state);
  setState("user", data.user);
  let pageIndex = new URLSearchParams(window.location.search).get('page');
  if (pageIndex != null && fresh) {
    pageIndex = parseInt(pageIndex);
    set_server_page(pageIndex);
    setState("server.page_index", pageIndex);
  } else {
    setState("server.page_index", data.state.page_index);
  }
}

rpc("load_data", {}, loadData);

export const moveStep = (delta) => {
  rpc("move_step", {delta}, loadData);
};

export const movePage = (delta) => {
  const newIndex = localState.server.page_index + delta;
  setState("server.page_index", newIndex);
  set_server_page(newIndex);
  scroller.scrollTo(`step-text-${stepIndex()}`, {delay: 0, duration: 0})
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
    const newStepIndex = stepIndex(value.state);
    if (stepIndex(state.server) < newStepIndex) {
      setTimeout(() =>
          scroller.scrollTo(`step-text-${newStepIndex}`, {
            duration: 1000,
            smooth: true,
          }),
        500,
      )

      state = {
        ...state,
        ..._.pick(initialState, (
          "numHints messages solution " +
          "requestingSolution").split(" ")),
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

export const setDeveloperMode = (value) => {
  rpc("set_developer_mode", {value});
  setState("user.developerMode", value);
}
