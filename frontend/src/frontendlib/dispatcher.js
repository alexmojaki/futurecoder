export const dispatcher = (actionMaker) => {
  const wrapper = (...args) => {
    const action = wrapper.raw(...args);
    const store = wrapper.store || dispatcher.store;
    store.dispatch(action);
  };
  wrapper.raw = actionMaker;
  return wrapper;
};

export default dispatcher;
