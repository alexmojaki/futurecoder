import React from 'react';
import ReactDOM from 'react-dom';
import {App} from './App';
import {Provider} from "react-redux";
import {store} from "./store";

if (window.location.pathname === "/") {
  window.location = "/home";
}

ReactDOM.render(
  typeof SharedArrayBuffer == "undefined" ?
    <div className="container">
      <h1>Browser not supported</h1>
      <p>Sorry, futurecoder doesn't work yet on this browser. The following browsers should work:</p>
      <ul>
        <li>Chrome</li>
        <li>Firefox</li>
        <li>Edge</li>
        <li>Opera</li>
      </ul>
      <p>Mobile devices and Safari are currently not supported.</p>
    </div>
    :
    <Provider store={store}>
      <App/>
    </Provider>,
  document.getElementById("root")
);
