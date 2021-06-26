import {createStore, applyMiddleware, compose, combineReducers} from "redux";
import thunk from "redux-thunk";
import logger from "redux-logger";
import {connect} from "react-redux";
import {
  TextContainer,
  redact,
  dispatcher
} from "./frontendlib";
import {bookReducer, navigate} from "./book/store";

import * as Sentry from "@sentry/react";

const sentryDsn = process.env.REACT_APP_SENTRY_DSN;
if (sentryDsn) {
  console.log('Configuring sentry');
  Sentry.init({dsn: sentryDsn, normalizeDepth: 5});
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

const sentryReduxEnhancer = Sentry.createReduxEnhancer({});

export const store = createStore(
  reducer,
  composeEnhancers(
    applyMiddleware(
      thunk,
      logger,
    ),
    sentryReduxEnhancer)
);

dispatcher.store = store;
redact.store = store;
window.reduxStore = store;

navigate();
