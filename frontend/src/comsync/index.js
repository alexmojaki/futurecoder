import {readMessage, uuidv4, writeMessage} from "sync-message";
import * as Comlink from 'comlink';

export class InterruptError extends Error {
}

export class NoChannelError extends Error {
}

export class TaskClient {
  constructor(workerCreator, channel) {
    this.workerCreator = workerCreator;
    this.channel = channel;
    this.messageId = null;
    this.interrupter = null;
    this.state = "idle";
    this._start();
  }

  _start() {
    this.worker = this.workerCreator();
    this.workerProxy = Comlink.wrap(this.worker);
  }

  _terminate() {
    this.workerProxy[Comlink.releaseProxy]();
    this.worker.terminate();
  }

  async interrupt(force) {
    if (this.state === "idle") {
      return;
    }

    if (!force) {
      if (this.messageId) {
        await this._writeMessage({interrupted: true});
        return;
      }

      if (this.interrupter) {
        await this.interrupter();
        return;
      }
    }

    this.interruptRejector(new InterruptError("Worker terminated"));
    this._terminate();
    this._start();
  }

  async _writeMessage(message) {
    const {messageId} = this;
    if (!messageId) {
      throw new Error("No messageId set");
    }
    this.messageId = null;
    await writeMessage(this.channel, message, messageId);
  }

  async runTask(funcName, ...args) {
    if (this.state !== "idle") {
      throw new Error("Still running a task");
    }
    this.state = "running";

    const syncMessageCallback = (messageId, state) => {
      this.messageId = messageId;
      if (state) {
        this.state = state;
      }
    };

    this.interruptPromise = new Promise((resolve, reject) => this.interruptRejector = reject);

    try {
      return await Promise.race([
        this.workerProxy[funcName](
          this.channel,
          Comlink.proxy(syncMessageCallback),
          ...args,
        ),
        this.interruptPromise,
      ]);
    } finally {
      this.state = "idle";
    }
  }

  async writeMessage(message) {
    if (this.state !== "awaitingInput") {
      throw new Error("Not waiting for message");
    }
    this.state = "running";
    await this._writeMessage({message});
  }
}

export function exposeSync(func) {
  return function (channel, syncMessageCallback, ...args) {
    function fullSyncMessageCallback(state, readMessageOptions) {
      if (!channel) {
        throw new NoChannelError();
      }
      const messageId = uuidv4();
      syncMessageCallback(messageId, state);
      const {message, interrupted} = readMessage(channel, messageId, readMessageOptions);
      if (interrupted) {
        throw new InterruptError();
      }
      return message;
    }

    const extras = {
      channel,
      readMessage() {
        return fullSyncMessageCallback("awaitingInput");
      },
      syncSleep(ms) {
        fullSyncMessageCallback(null, {timeout: ms});
      },
    };
    return func(extras, ...args);
  }
}
