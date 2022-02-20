import {applyMiddleware, combineReducers, compose, createStore} from "redux";
import thunk from "redux-thunk";
import logger from "redux-logger";
import {connect} from "react-redux";
import {dispatcher, redact, TextContainer} from "./frontendlib";
import {bookReducer, currentStep, navigate} from "./book/store";
import * as Sentry from "@sentry/react";
import _ from "lodash";

const sentryReduxEnhancer = Sentry.createReduxEnhancer({
  actionTransformer: action => {
    if (action.type === "LOAD_PAGES") {
      return null;
    }
    if (action.type === "RAN_CODE") {
      try {
        action = {
          ...action,
          messages: action.messages?.map(m => _.truncate(m, {length: 100})),
          output: _.truncate(action.output, {length: 100}),
        }
      } catch {
      }
    }
    return action;
  },
  stateTransformer: state => {
    state = _.omit(state, "book.pages");
    try {
      state = {...state, currentStep: currentStep(state)};
    } catch {
    }
    return state;
  },
});

const sentryDsn = process.env.REACT_APP_SENTRY_DSN;
if (sentryDsn) {
  console.log('Configuring sentry');
  Sentry.init({
    dsn: sentryDsn,
    normalizeDepth: 5,
    beforeBreadcrumb(breadcrumb, hint) {
      const {message} = breadcrumb;
      if (message.includes("prev state") || message.includes("next state")) {
        return null;
      }
      return breadcrumb;
    },
  });
}

const {delegateReducer} = redact("root");

TextContainer.connect = connect;

const reducer = delegateReducer(
  combineReducers({
    book: bookReducer,
  })
);

// noinspection JSUnresolvedVariable
const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;

export const store = createStore(
  reducer,
  composeEnhancers(
    applyMiddleware(
      thunk,
      logger,
    ),
    sentryReduxEnhancer,
  )
);

dispatcher.store = store;
redact.store = store;
window.reduxStore = store;

navigate();
