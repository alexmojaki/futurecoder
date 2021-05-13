import { ipush, iset } from "./mu-immutable";
import { merge } from "lodash";
import { dispatcher } from "./dispatcher";
import { assert } from "./utilities";


export const redact = (name, initialState = {}, { dispatched } = {}) => {
  const reducerCases = {};

  const addReducerCase = (type, reducer) => {
    reducer = reducer || (state => state);
    assert(!reducerCases[type], 'Type already exists');
    return reducerCases[type] = reducer;
  };

  const maybeDispatcher = dispatched ? dispatcher : x => x;

  const makeAction = (type, reducer, actionMaker = value => ({ value })) => {
    addReducerCase(type, reducer);
    return maybeDispatcher((...args) => {
      const action = actionMaker(...args);
      return {
        ...action,
        type,
      };
    });
  };

  const makeThunk = (type, reducer, actionMaker = value => ({ value })) => {
    addReducerCase(type, reducer);
    return maybeDispatcher((...args) => {
      const thunkFn = actionMaker(...args);
      // Return a function with a similar signature
      // except it replaces dispatch with a modified version
      // that automatically adds the type to its argument
      return (dispatch, ...args) => {
        const dispatchWithType = (dispatchedAction) => {
          if (typeof dispatchedAction === 'object') {
            return dispatch({ type, ...dispatchedAction });
          }
          return dispatch(dispatchedAction);
        };
        return thunkFn(dispatchWithType, ...args);
      };
    });
  };


  const stateSet = makeAction(
    name + "_SET_STATE",
    (state, { path, value }) => iset(state, path, value),
    (path, value) => ({ path, value })
  );
  const setState = stateSet;

  const mergeState = makeAction(
    name + '_MERGE_STATE',
    (state, { value }) => merge({}, state, value)
  );

  const statePush = makeAction(
    name + '_PUSH',
    (state, { path, value }) => ipush(state, path, value),
    (path, value) => ({ path, value }),
  );

  const reducer = (state = initialState, action) => {
    const reducerCase = reducerCases[action.type];
    if (!reducerCase) {
      return state;
    }
    return reducerCase(state, action);
  };

  const delegateReducer = (baseReducer) => (state, action) => baseReducer(reducer(state, action), action);

  const localState = new Proxy({}, {
    get: (_, prop) => redact.store?.getState()[name][prop]
  });

  return {
    reducerCases,
    makeAction,
    makeThunk,
    stateSet,
    setState,
    mergeState,
    statePush,
    reducer,
    delegateReducer,
    localState,
  };
};

export default redact;
