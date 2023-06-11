import React, {useState} from "react";

export const HookInput = (hook, options, element = "input") =>
  React.createElement(element,
    {
      value: hook[0],
      onChange: (e) => hook[1](e.target.value),
      ...options,
    })

export const useInput = (initialValue, options, element = "input") => {
  const hook = useState(initialValue);
  const input = HookInput(hook, options, element);
  return {input, value: hook[0], setHookValue: hook[1]};
}
