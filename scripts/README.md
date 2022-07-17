This folder contains various scripts, especially for building futurecoder. I run them on Ubuntu, although hopefully they should work on any Linux/OSX system. In general you should run them from the root folder, e.g. `./scripts/build.sh` rather than `./build.sh`.

The most important scripts for most people to know about are:

- `install_deps.sh` installs Python (poetry) and JS (npm) dependencies. You should only need to run it once, unless dependencies change.
- `generate.sh` runs a few important Python scripts to generate several files, some of which are tracked by git. You should run it regularly when making changes during development. In particular it runs `generate_static_files.py` which 'builds' the Python code in `core` to be served by the frontend, so after making Python code changes you need to run it before refreshing the page in the browser. Running `generate_static_files` directly may be faster but not always be enough - in particular you often need to run `translations/generate_po_file.py` first.
- `build.sh` does a full build ready for production deployment, including the `frontend` folder which is deployed at the `/course/` path and the `homepage` folder.

Environment variables used by futurecoder:

- `FUTURECODER_LANGUAGE` is required for `build.sh` and specifies which translation to use. It should be the name of a folder in `translations/locales`, e.g. `en` or `fr`. Related variables:
  - `FUTURECODER_LANGUAGES` (with an `S` at the end) is used by `generate.sh` to update files for multiple languages at once, with space-separated language codes.
  - `REACT_APP_LANGUAGE` has the same meaning but is used when building the frontend JS code with `npm run build`, since create-react-app only accepts environment variables starting with `REACT_APP_`.
- `FIX_TESTS=1` when running `tests/test_steps.py` updates the files `tests/golden_files/$FUTURECODER_LANGUAGE/test_transcript.json`. So if the test there fails, you probably need to run it again with this environment variable first.
- `FIX_CORE_IMPORTS=1` updates `core_imports.txt` when running `generate_static_files.py`. Without this, the script will fail if a different set of Python dependencies is detected. This ensures that the correct dependencies are packaged into `python_core.tar.load_by_url`. If you haven't changed any dependencies and are told to set this environment variable to fix an error, you probably have some problem with your poetry virtual environment.
- `REACT_APP_PRECACHE=1` indicates that the JS service worker should enable caching to allow using futurecoder offline. This is good for production deployment but not local development, unless you're specifically working on service worker caching.
- `REACT_APP_SENTRY_DSN` is used to submit error reports to https://sentry.io/. Not required for development.
- `REACT_APP_DISABLE_LOGIN` hides the Login/Signup button in the top bar of the course, if you want a deployment with only anonymous user accounts.
- `REACT_APP_DISABLE_FIREBASE` disables firebase entirely, so in addition to no Login/Signup button there'll be no data stored online at all, not even in anonymous accounts. User data such as progress will still be saved locally.
- `REACT_APP_USE_FIREBASE_EMULATORS` configures firebase to connect to local emulators instead of the real database online. Ensure you're running the emulators with a command such as `firebase emulators:start --only auth,database`.

Less important scripts here:

- `ci_test.sh` is used by GitHub Actions in `.github/workflows/workflow.yml` to run tests.
- `generate_steps.py` is a very different kind of script occasionally used to help with writing course content.
