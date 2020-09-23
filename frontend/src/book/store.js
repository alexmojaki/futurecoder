import {ipush, iremove, iset, redact} from "../frontendlib";
import {rpc} from "../rpc";
import {animateScroll, scroller} from "react-scroll";
import _ from "lodash";

const initialState = {
  server: {
    pages_progress: [0],
  },
  page_index: 0,
  pages: [
    {
      title: "Loading...",
      slug: "loading_placeholder",
      steps: [
        {
          text: "",
          hints: [],
          slug: "loading_placeholder",
          solution: null,
        }
      ],
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
  requestingSolution: 0,
};


const {reducer, makeAction, setState, localState} = redact('book', initialState, {dispatched: true});

export {reducer as bookReducer, setState as bookSetState, localState as bookState};

export const stepIndex = (state = localState) => state.server.pages_progress[state.page_index];

const set_page = (index) => {
  setState("page_index", index);
  rpc("set_page", {index});
};

const loadData = (data) => {
  if (!data.user) {
    window.location = '/accounts/login/?next='
      + window.location.pathname
      + window.location.search;
  }
  setState("pages", data.pages);
  setState("server", data.state);
  setState("user", data.user);
  const pageSlug = new URLSearchParams(window.location.search).get('page');
  let pageIndex;
  if (pageSlug != null) {
    // Allow either page index or page slug in URL
    pageIndex = parseInt(pageSlug) || parseInt(_.findIndex(data.pages, {slug: pageSlug}));
  } else {
    pageIndex = data.page_index;
  }
  set_page(pageIndex);
}

rpc("load_data", {}, loadData);

export const moveStep = (delta) => {
  rpc("move_step",
    {
      page_index: localState.page_index,
      step_index: stepIndex() + delta
    },
    (result) => setState("server", result),
  );
};

export const movePage = (delta) => {
  set_page(localState.page_index + delta);
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
    if (value.passed) {
      setTimeout(() =>
          scroller.scrollTo(`step-text-${stepIndex()}`, {
            duration: 1000,
            smooth: true,
          }),
        500,
      )

      state = {
        ...state,
        ..._.pick(initialState, (
          "numHints messages requestingSolution").split(" ")),
        server: value.state,
        processing: false,
      };
    }
    state = addMessageToState(state, value.message);
    return state;
  },
);

const addMessageToState = (state, message) => {
  if (message && state.pastMessages.indexOf(message) === -1) {
      animateScroll.scrollToBottom({duration: 1000, delay: 500});
      state = ipush(state, "messages", message);
      state = ipush(state, "pastMessages", message);
    }
  return state;
}

export const addMessage = makeAction(
  'ADD_MESSAGE',
  (state, {value}) => addMessageToState(state, value)
)

export const closeMessage = makeAction(
  'CLOSE_MESSAGE',
  (state, {value}) => iremove(state, "messages", value)
)

export const revealSolutionToken = makeAction(
  "REVEAL_SOLUTION_TOKEN",
  (state) => {
    const solution_path = ["pages", state.page_index, "steps", stepIndex(state), "solution"];
    const indices_path = [...solution_path, "maskedIndices"]
    const indices = _.get(state, indices_path);
    if (!indices.length) {
      return state;
    }
    state = iremove(state, indices_path, 0);
    state = iset(state, [...solution_path, "mask", indices[0]], false);
    return state;
  }
)

export const setDeveloperMode = (value) => {
  rpc("set_developer_mode", {value});
  setState("user.developerMode", value);
}

export const reorderSolutionLines = makeAction(
  "REORDER_SOLUTION_LINES",
  (state, {startIndex, endIndex}) => {
    const path = ["pages", state.page_index, "steps", stepIndex(state), "solution", "lines"];
    const result = Array.from(_.get(state, path));
    const [removed] = result.splice(startIndex, 1);
    result.splice(endIndex, 0, removed);
    return iset(state, path, result);
  },
  (startIndex, endIndex) => ({startIndex, endIndex})
)
