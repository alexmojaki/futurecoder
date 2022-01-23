const BASE_URL_SUFFIX = "/__SyncWebWorkerServiceWorkerInput__";

export function serviceWorkerFetchListener() {
  const earlyMessages = {};
  const resolvers = {};

  return (e) => {
    const {url} = e.request;
    if (!url.includes(BASE_URL_SUFFIX)) {
      return false;
    }

    async function respond() {
      if (url.endsWith("/read")) {
        const {messageId} = await e.request.json();
        const data = earlyMessages[messageId];
        if (data) {
          delete earlyMessages[messageId];
          return new Response(data, {status: 200});
        } else {
          return await new Promise(r => resolvers[messageId] = r);
        }
      } else if (url.endsWith("/write")) {
        const {data, messageId} = await e.request.json();
        const resolver = resolvers[messageId];
        if (resolver) {
          resolver(new Response(data, {status: 200}));
          delete resolvers[messageId];
        } else {
          earlyMessages[messageId] = data;
        }
        return new Response(data, {status: 200});
      } else if (url.endsWith("/version")) {
        return new Response("v1", {status: 200});
      }
    }

    e.respondWith(respond());
    return true;
  };
}

export function asyncSleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

export function makeAtomicsChannel(options = {}) {
  const data = new Uint8Array(new SharedArrayBuffer(options.bufferSize || 128 * 1024));
  const meta = new Int32Array(new SharedArrayBuffer(Int32Array.BYTES_PER_ELEMENT * 2));
  const encoder = new TextEncoder();

  return {
    channel: {type: 'atomics', data, meta},
    writeInput: function (string) {
      const bytes = encoder.encode(string);
      if (bytes.length > data.length) {
        throw "Input is too long";
      }
      data.set(bytes, 0);
      Atomics.store(meta, 0, bytes.length);
      Atomics.store(meta, 1, 1);
      Atomics.notify(meta, 1);
    },
  }
}

export async function makeServiceWorkerChannel(options = {}) {
  const registration = await navigator.serviceWorker.ready;
  const baseUrl = registration.scope + BASE_URL_SUFFIX;

  const timeout = options.timeout || 5000;
  const startTime = new Date();
  while (true) {
    const response = await fetch(baseUrl + "/version");
    if (response.status === 200 && await response.text() === "v1") {
      break;
    }
    if (new Date() - startTime < timeout) {
      await asyncSleep(100);
    } else {
      return null;
    }
  }

  return {
    channel: {type: 'serviceWorker', baseUrl},
    writeInput: function (data, messageId) {
      fetch(baseUrl + "/write", {method: "POST", body: JSON.stringify({data, messageId})});
    },
  }
}

export function readChannel(channel, messageId, options = {}) {
  const {checkInterrupt} = options;
  if (channel.type === 'atomics') {
    const {data, meta} = channel;
    while (Atomics.wait(meta, 1, 0, 100) === "timed-out") {
      if (checkInterrupt?.()) {
        return null;
      }
    }
    const size = Atomics.exchange(meta, 0, 0);
    const bytes = data.slice(0, size);
    Atomics.store(meta, 1, 0);

    const decoder = new TextDecoder();
    return decoder.decode(bytes);
  } else {
    while (true) {
      const request = new XMLHttpRequest();
      // `false` makes the request synchronous
      request.open('POST', channel.baseUrl + "/read", false);
      request.timeout = 100;
      try {
        request.send(JSON.stringify({messageId}));
        return request.responseText;
      } catch {
        if (checkInterrupt?.()) {
          return null;
        }
      }
    }
  }
}
