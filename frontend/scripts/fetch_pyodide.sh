export HERE="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null && pwd )"  # bashism for getting dir the script is stored in


wget https://cdn.jsdelivr.net/pyodide/v0.19.0/full/pyodide.js -O "$HERE/../src/vendor/pyodide.js"
