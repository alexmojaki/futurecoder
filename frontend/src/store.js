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
  ))
);

dispatcher.store = store;
redact.store = store;
