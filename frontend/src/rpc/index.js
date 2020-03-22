import axios from "axios";
import {stateSet} from "./store";
// import {finishLoading, statePush, stateSet} from "./store";

axios.defaults.xsrfCookieName = 'csrftoken';
axios.defaults.xsrfHeaderName = "X-CSRFTOKEN";

export const rpc = (method, data, onSuccess, onError) => {
  console.log('Calling RPC method', method);
  // dispatch(statePush('loading', method));

  return axios.post(
    `/api/${method}/`,
    data,
  ).then((response) => {
    console.log('Finished RPC method', method);
    if (response.data.error) {
      stateSet("error", {...response.data.error, method, data});
    } else if (onSuccess) {
      onSuccess(response.data);
    }
  }).catch((response) => {
    const message = `Error for RPC method ${method}`;
    console.error(message, response);
    if (onError) {
      onError(response);
    }
  }).then(() => {
    // dispatch(finishLoading(method));
  });
};
