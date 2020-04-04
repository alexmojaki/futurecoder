import {createStore, applyMiddleware, compose, combineReducers} from "redux";
import thunk from "redux-thunk";
import logger from "redux-logger";
import {rpcReducer} from "./rpc/store";
import {connect} from "react-redux";
import {
  TextContainer,
  redact,
  dispatcher
} from "./frontendlib";
import {bookReducer} from "./book/store";

import createSentryMiddleware from "redux-sentry-middleware";
import * as Sentry from "@sentry/browser";

if (process.env.NODE_ENV !== 'development') {
  console.log('Configuring sentry');
  Sentry.init({dsn: 'https://8eeb5d4141a64fb38b6dac0c8bba9de3@sentry.io/5170673'});
}

const {delegateReducer, stateSet} = redact("root");

TextContainer.connect = connect;

const reducer = delegateReducer(
  combineReducers({
    rpc: rpcReducer,
    book: bookReducer,
  })
);

// noinspection JSUnresolvedVariable
const composeEnhancers = window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__ || compose;

export const store = createStore(
  reducer,
  composeEnhancers(applyMiddleware(
    thunk,
    logger,
    createSentryMiddleware(Sentry),
  ))
);

dispatcher.store = store;
redact.store = store;
