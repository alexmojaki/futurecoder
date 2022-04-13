import React from 'react';
import ReactDOM from 'react-dom';
import {App} from './App';
import {Provider} from "react-redux";
import {store} from "./store";


import * as serviceWorkerRegistration from './serviceWorkerRegistration';


ReactDOM.render(
    <Provider store={store}>
      <App/>
    </Provider>,
  document.getElementById("root")
);

// Always run the service worker (even in dev) (but it only enables PWA-style precaching depending on an env variable)
serviceWorkerRegistration.register();
