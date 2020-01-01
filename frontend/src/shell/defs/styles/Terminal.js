
export default {
  container: {
    minWidth: '500px',
    minHeight: '300px',
    maxWidth: '100%', // Fill parent before overflowing
    maxHeight: '100%', // Fill parent before overflowing
    borderRadius: '5px',
    overflow: 'auto',
    cursor: 'text',
    background: '#212121',
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
    width: '100%'
  },
  promptLabel: {
    // paddingTop: '3px',
    // color: '#EE9C34'
  },
  input: {
    border: '0',
    padding: '0 0 0 7px',
    margin: '0',
    flexGrow: '100',
    width: '100%',
    height: '22px',
    background: 'transparent',
    fontSize: '15px',
    color: '#FFFFFF',
    fontFamily: 'monospace',
    outline: 'none' // Fix for outline showing up on some browsers
  }
}
