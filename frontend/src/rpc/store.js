import {redact} from "../frontendlib";

const initialState = {
  loading: [],
  error: null,
};

const {stateSet, statePush, reducer, makeAction} = redact('rpc', initialState);

export {stateSet, statePush, reducer as rpcReducer};

export const finishLoading = makeAction(
  'FINISH_LOADING',
  (state, {value}) => {
    const foundIndex = state.loading.indexOf(value);
    return {
      ...state,
      loading: state.loading.filter((x, currentIndex) => foundIndex !== currentIndex),
    };
  },
);
