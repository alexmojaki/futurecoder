import PropTypes from 'prop-types'

const styleTypes = {
  style: PropTypes.object,
  contentStyle: PropTypes.object,
  inputAreaStyle: PropTypes.object,
  promptLabelStyle: PropTypes.object,
  inputStyle: PropTypes.object
}

const classNameTypes = {
  className: PropTypes.string,
  contentClassName: PropTypes.string,
  inputAreaClassName: PropTypes.string,
  promptLabelClassName: PropTypes.string,
  inputClassName: PropTypes.string
}

const optionTypes = {
  autoFocus: PropTypes.bool,
  dangerMode: PropTypes.bool,
  disableOnProcess: PropTypes.bool,
  noDefaults: PropTypes.bool,
  noAutomaticStdout: PropTypes.bool,
  noHistory: PropTypes.bool,
  noAutoScroll: PropTypes.bool
}

const labelTypes = {
  welcomeMessage: PropTypes.oneOfType([
    PropTypes.bool,
    PropTypes.array,
    PropTypes.string
  ]),
  promptLabel: PropTypes.string,
  errorText: PropTypes.string
}

const commandTypes = {
  onCommand: PropTypes.object.func,
  commandCallback: PropTypes.func
}

export default {
  ...styleTypes,
  ...classNameTypes,
  ...optionTypes,
  ...labelTypes,
  ...commandTypes
}
