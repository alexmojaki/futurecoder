import {ipush, iremove, iset, redact} from "../frontendlib";
import {animateScroll, scroller} from "react-scroll";
import _ from "lodash";
import {terminalRef} from "../RunCode";
import firebase from "firebase/app";
import "firebase/auth";
import "firebase/analytics";
import pagesUrl from "./pages.json.load_by_url"
import axios from "axios";
import * as terms from "../terms.json"
import * as Sentry from "@sentry/react";
import {wrapAsync} from "../frontendlib/sentry";
import pRetry from 'p-retry';
import localforage from "localforage";
import {languageConfig} from "../languages";

export const disableFirebase = !!process.env.REACT_APP_DISABLE_FIREBASE;
export const disableLogin = disableFirebase || !!process.env.REACT_APP_DISABLE_LOGIN;

const {firebaseConfig} = languageConfig;
const firebaseApp = !disableFirebase && firebase.initializeApp(firebaseConfig);

let {databaseURL} = firebaseConfig;

if (!disableFirebase && process.env.REACT_APP_USE_FIREBASE_EMULATORS && window.location.hostname === "localhost") {
  // firebase.database().useEmulator("localhost", 9009);
  databaseURL = "http://localhost:9009";
  firebase.auth().useEmulator("http://localhost:9099");
}

let firebaseAnalytics;
export const isProduction = !disableFirebase && window.location.hostname.endsWith("futurecoder.io");
if (isProduction) {
  firebase.analytics.isSupported().then((isSupported) => {
    if (isSupported) {
      firebaseAnalytics = firebase.analytics(firebaseApp);
    }
  });
}

const initialState = {
  error: null,
  route: "main",
  previousRoute: "main",
  pages: {
    loading_placeholder: {
      title: terms.loading_wait,
      slug: "loading_placeholder",
      index: 0,
      steps: [
        {
          index: 0,
          text: "",
          hints: [],
          name: "loading_placeholder",
          solution: null,
          requirements: null,
        }
      ],
    },
  },
  pageSlugsList: ["loading_placeholder"],
  user: {
    uid: null,
    email: "",
    developerMode: false,
    pagesProgress: {
      loading_placeholder: {
        step_name: "loading_placeholder",
      }
    },
    pageSlug: "loading_placeholder",
  },
  processing: false,
  running: false,
  numHints: 0,
  editorContent: "",
  messageSections: [],
  specialMessages: [],
  pastSpecialMessages: [],
  requestingSolution: 0,
  prediction: {
    choices: null,
    answer: "",
    wrongAnswers: [],
    userChoice: "",
    state: "hidden",
    codeResult: {},
  },
  questionWizard: {
    messages: [],
    requestExpectedOutput: false,
    expectedOutput: "",
  }
};


const {reducer, makeAction, setState, localState, statePush} = redact('book', initialState, {dispatched: true});

export {reducer as bookReducer, setState as bookSetState, localState as bookState, statePush as bookStatePush};

const isLoaded = (state) => state.user.uid && state.pageSlugsList.length > 1

export const currentPage = (state = localState) => {
  if (!isLoaded(state)) {
    return initialState.pages.loading_placeholder;
  }
  return state.pages[state.user.pageSlug];
};

const pageProgress = (state = localState) => {
  if (!isLoaded(state)) {
    return initialState.user.pagesProgress.loading_placeholder;
  }
  return state.user.pagesProgress[state.user.pageSlug];
};

export const currentStepName = (state = localState) => pageProgress(state).step_name;
export const currentStep = (state = localState) =>
  _.find(currentPage(state).steps, {name: currentStepName(state)});

export const setPage = (page_slug) => {
  setState("user.pageSlug", page_slug);
  afterSetPage(page_slug);
};

const afterSetPage = (pageSlug, state = localState) => {
    setTimeout(() =>
      scroller.scrollTo(`step-text-${currentStep(state).index}`, {
        delay: 0,
        duration: 0,
        offset: -60,
      }),
    120,
  )
  updateDatabase({pageSlug});
  window.location.hash = pageSlug;
}

export const specialHash = (hash) => ["toc", "ide", "question"].includes(hash);

export const navigate = () => {
  const hash = window.location.hash.substring(1);
  setState("previousRoute", localState.route)
  if (specialHash(hash)) {
    setState("route", hash);
  } else if (_.includes(localState.pageSlugsList, hash)) {
    setState("route", "main");
    setPage(hash);
  }
};
window.addEventListener("hashchange", navigate);

export const setPageIndex = (pageIndex) => {
  setPage(localState.pageSlugsList[pageIndex]);
};

export const movePage = (delta) => {
  setPageIndex(currentPage().index + delta);
};

export const moveStep = (delta) => {
  const stepIndex = currentStep().index + delta;
  const step = currentPage().steps[stepIndex];
  if (!step) {
    return;
  }

  if (delta > 0) {
    animateStep(stepIndex);
  }
  setUserStateAndDatabase(["pagesProgress", localState.user.pageSlug, "step_name"], step.name);
};

const animateStep = (stepIndex) => {
  const stepDiv = document.getElementById(`step-text-${stepIndex}`);
  if (stepDiv) {
    stepDiv.style.animation = 'next-step-transition 0.7s ease-out, next-step-flash 3s ease-out 0.7s';
  }
}

const loadPages = makeAction(
  "LOAD_PAGES",
  (state, {value: {pages, pageSlugsList}}) => {
    return loadUserAndPages({
      ...state,
      pages,
      pageSlugsList,
    });
  },
)

const debouncedSaveEditorContent = _.debounce(
  editorContent => updateDatabase({editorContent}),
  3000,
  {maxWait: 15000},
);

export function setEditorContent(editorContent) {
  setState("editorContent", editorContent);
  // noinspection JSValidateTypes
  debouncedSaveEditorContent(editorContent);
}

pRetry(() => wrapAsync(axios.get, "axios_get")(pagesUrl), {retries: 3})
  .then((response) => loadPages(response.data));

const loadUser = makeAction(
  "LOAD_USER",
  (state, {value: {editorContent, ...user}}) => {
    state = iset(state, "editorContent", state.editorContent || editorContent || "");
    return loadUserAndPages({...state, user}, state.user);
  },
);

// Reset state to clear out user data
export const signOut = makeAction(
  "SIGN_OUT",
  (state) => {
    return loadUserAndPages({
      ...state,
      editorContent: "",
      user: {
        ...initialState.user,
        // Avoid an empty user.uid so that this cleared state is saved to the local store,
        // so signing out has an effect even when offline.
        ...initialUser,
        // Stay on the current page, rather than the initial loading_placeholder which breaks.
        pageSlug: state.user.pageSlug,
      }
    }, {});
  },
);

if (!disableFirebase) {
  firebase.auth().onAuthStateChanged(async (user) => {
    if (user) {
      // TODO ideally we'd set a listener on the user instead of just getting it once
      //   to sync changes made on multiple devices
      await updateUserData(user);
    } else {
      await firebase.auth().signInAnonymously();
    }
  });
}

export const updateUserData = async (user) => {
  Sentry.setUser({id: user.uid});
  const userData = await databaseRequest("GET");
  // loadUser should be called on the local store data first
  // for proper merging with the firebase user data in loadUserAndPages
  await loadUserFromLocalStorePromise;
  loadUser({
    uid: user.uid,
    email: user.email,
    ...userData,
  });
}

export const initialUser = {uid: "__futurecoder_offline__"}

export const localStore = localforage.createInstance({name: "futurecoder"});

const loadUserFromLocalStorePromise = localStore.getItem("user").then(user => {
  loadUser(user || initialUser);
});

export const databaseRequest = wrapAsync(async function databaseRequest(method, data={}, endpoint="users") {
  if (disableFirebase) {
    return;
  }
  const currentUser = firebase.auth().currentUser;
  if (!currentUser) {
    return;
  }
  const auth = await currentUser.getIdToken();
  const response = await pRetry(() =>
      axios.request({
        url: `${databaseURL}/${endpoint}/${currentUser.uid}.json`,
        params: {auth},
        method,
        data,
      }),
    {retries: 3},
  )
  return response.data;
});

export const updateDatabase = (updates) => {
  return databaseRequest("PATCH", updates);
}

const setUserStateAndDatabase = (path, value) => {
  if (typeof path === "string") {
    path = [path];
  }
  setState(["user", ...path], value);
  updateDatabase({[path.join("/")]: value});
}

let loadedPromiseResolve;
export const loadedPromise = new Promise((resolve) => {loadedPromiseResolve = resolve});

const loadUserAndPages = (state, previousUser = {}) => {
  if (!isLoaded(state)) {
    return state;
  }
  let {
    user: {pagesProgress, pageSlug, developerMode},
    pages,
    pageSlugsList
  } = state;

  developerMode = developerMode || previousUser.developerMode || false;
  const updates = {developerMode};

  const hash = window.location.hash.substring(1);

  if (!pageSlug) {
    if (previousUser.uid && previousUser.pageSlug !== "loading_placeholder") {
      pageSlug = previousUser.pageSlug;
    } else if (_.includes(pageSlugsList, hash)) {
      pageSlug = hash;
    } else {
      // Check URL parameters for legacy URLs, otherwise default to first page
      pageSlug = new URLSearchParams(window.location.search).get('page') || pageSlugsList[0];
    }
  }

  pagesProgress = {...(pagesProgress || {})};
  pageSlugsList.forEach(slug => {
    const steps = pages[slug].steps;
    let step_name = pagesProgress[slug]?.step_name || steps[0].name;
    const progress = previousUser.pagesProgress?.[slug];
    if (progress) {
      const findStepIndex = (name) => _.find(steps, {name})?.index || 0
      const previousIndex = findStepIndex(progress.step_name);
      const currentIndex =  findStepIndex(step_name);
      if (previousIndex > currentIndex) {
        step_name = progress.step_name;
        updates[`pagesProgress/${slug}/step_name`] = step_name;
      }
    }
    pagesProgress[slug] = {step_name};
  });

  migrateUserState(pages, pagesProgress, updates);

  updateDatabase(updates);

  state = {...state, user: {...state.user, pagesProgress, pageSlug, developerMode}};
  if (!specialHash(hash)) {
    afterSetPage(pageSlug, state);
  }

  loadedPromiseResolve();

  return state;
}

function migrateUserState(pages, pagesProgress, updates) {
  const oldSlug = "GettingElementsAtPosition";
  const newSlug = "GettingElementsAtPositionExercises";
  const {step_name} = pagesProgress[oldSlug];
  if (!pages[oldSlug].step_names.includes(step_name)) {
    pagesProgress[oldSlug] = {step_name: "final_text"};
    pagesProgress[newSlug] = {step_name};
    updates[`pagesProgress/${oldSlug}/step_name`] = "final_text";
    updates[`pagesProgress/${newSlug}/step_name`] = step_name;
  }
}

export const showHint = makeAction(
  'SHOW_HINT',
  (state) => {
    return {
      ...state,
      numHints: state.numHints + 1,
    };
  },
);

export const scrollToNextStep = () => {
  setTimeout(() =>
      scroller.scrollTo(`step-text-${currentStep().index}`, {
        duration: 1000,
        smooth: true,
        offset: -60,
      }),
    500,
  )
};

export const ranCode = makeAction(
  'RAN_CODE',
  (state, {value}) => {
    const prediction = currentStep(state).prediction;

    if (value.passed) {
      scrollToNextStep();

      state = {
        ...state,
        ..._.pick(initialState,
          "numHints messageSections requestingSolution".split(" ")),
        prediction: {
          ...prediction,
          userChoice: "",
          wrongAnswers: [],
          state: prediction.choices ? "waiting" : "hidden",
          codeResult: value,
        },
      };

      if (prediction.choices) {
        const scrollInterval = setInterval(() => {
          animateScroll.scrollToBottom({duration: 30, container: terminalRef.current.terminalRoot.current});
        }, 30);
        setTimeout(() => clearInterval(scrollInterval), 1300);
      }
    }

    if (state.route === "question") {
      if (value.question_wizard_status === "expected_output") {
        state = iset(state, "questionWizard.requestExpectedOutput", true);
        state = iset(state, "questionWizard.messages", []);
      } else if (value.question_wizard_status === "messages") {
        state = iset(state, "questionWizard.messages", value.messages);
      }
    } else {
      state = iset(state, "messageSections", value.message_sections);
    }

    return state;
  },
);

// 'Special messages' currently only means the "don't copy" popup.
// It used to be all kinds of messages, but those coming from the Python checker
// (just called 'messages') have been moved into the assistant.
const addSpecialMessageToState = (state, message) => {
  if (message && state.pastSpecialMessages.indexOf(message) === -1) {
      animateScroll.scrollToBottom({duration: 1000, delay: 500});
      state = ipush(state, "specialMessages", message);
      state = ipush(state, "pastSpecialMessages", message);
    }
  return state;
}

export const addSpecialMessage = makeAction(
  'ADD_SPECIAL_MESSAGE',
  (state, {value}) => addSpecialMessageToState(state, value)
)

export const closeSpecialMessage = makeAction(
  'CLOSE_SPECIAL_MESSAGE',
  (state, {value}) => iremove(state, "specialMessages", value)
)

export const revealSolutionToken = makeAction(
  "REVEAL_SOLUTION_TOKEN",
  (state) => {
    const solution_path = ["pages", state.user.pageSlug, "steps", currentStep(state).index, "solution"];
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
  setUserStateAndDatabase("developerMode", value);
}

export const reorderSolutionLines = makeAction(
  "REORDER_SOLUTION_LINES",
  (state, {startIndex, endIndex}) => {
    const path = ["pages", state.user.pageSlug, "steps", currentStep(state).index, "solution", "lines"];
    const result = Array.from(_.get(state, path));
    const [removed] = result.splice(startIndex, 1);
    result.splice(endIndex, 0, removed);
    return iset(state, path, result);
  },
  (startIndex, endIndex) => ({startIndex, endIndex})
)

export function logEvent(name, data = {}) {
  firebaseAnalytics?.logEvent(name, data);
}

export function postCodeEntry(codeEntry) {
  if (isProduction) {
    const {user: {developerMode}, route, numHints, requestingSolution} = localState;
    codeEntry = {
      ...codeEntry,
      state: {
        developerMode,
        page_route: route,
        num_hints: numHints,
        requesting_solution: requestingSolution,
      },
      timestamp: new Date().toISOString(),
    };
    databaseRequest("POST", codeEntry, "code_entries").catch(e => console.error(e));
  }
}
