
export default {
  container: {
    minWidth: '500px',
    minHeight: '300px',
    maxWidth: '100%', // Fill parent before overflowing
    maxHeight: '100%', // Fill parent before overflowing
    borderRadius: '5px',
    overflow: 'auto',
    cursor: 'text',
    background: 'rgb(39, 40, 34)',
    backgroundSize: 'cover'
  },
  content: {
    padding: '20px',
    height: '100%',
    fontSize: '15px',
    color: '#FFFFFF',
    fontFamily: 'monospace'
  },
  inputArea: {
    display: 'inline-flex',
    width: 'calc(100% - 2.5em)'
  },
  promptLabel: {
    // paddingTop: '3px',
    // color: '#EE9C34'
  },
  input: {
    border: '0',
    padding: '0',
    margin: '0',
    marginBottom: '2em',
    flexGrow: '100',
    width: '100%',
    background: 'transparent',
    fontSize: '15px',
    color: '#FFFFFF',
    fontFamily: 'monospace',
    outline: 'none' // Fix for outline showing up on some browsers
  }
}
