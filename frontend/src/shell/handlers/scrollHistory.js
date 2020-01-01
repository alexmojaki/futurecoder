import cleanArray from '../utils/cleanArray'

export default function scrollHistory (direction, commandHistory, historyPosition, previousHistoryPosition, terminalInput, noAutomaticStdout) {
  const history = cleanArray(commandHistory).reverse() // Clean empty items and reverse order to ease position tracking
  const position = historyPosition
  const previousPosition = previousHistoryPosition
  const termNode = terminalInput.current

  if (!noAutomaticStdout && history.length > 0) { // Only run if history is non-empty and in use
    switch (direction) {
      case 'up':
        if (position === null) {
          // If at no position, get most recent entry
          termNode.value = history[0]
          return { historyPosition: 0, previousHistoryPosition: null }
        } else if (position + 1 === history.length) {
          // If the first entry will be reached on this press, get it and decrement position by 1 to avoid confusing downscroll
          termNode.value = history[history.length - 1]
          return { historyPosition: history.length - 1, previousHistoryPosition: history.length - 2 }
        } else {
          // Normal increment by one
          termNode.value = history[position + 1]
          return { historyPosition: position + 1, previousHistoryPosition: position }
        }
      case 'down':
        if (position === null || !history[position]) {
          // If at initial or out of range, clear (Unix-like behaviour)
          termNode.value = ''
          return { historyPosition: null, previousHistoryPosition: null }
        } else if (position - 1 === -1) {
          // Clear because user pressed up once and is now pressing down again => clear or is reaching bottom
          if (previousPosition === null || (position === 0 && previousPosition === 1)) termNode.value = ''
          else termNode.value = history[0]

          return { historyPosition: null, previousHistoryPosition: null }
        } else {
          // Normal decrement by one
          termNode.value = history[position - 1]
          return { historyPosition: position - 1, previousHistoryPosition: position }
        }
    }
  }
}
