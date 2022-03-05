import importlib
import sys

import pyodide  # noqa
import pyodide_js  # noqa

sys.setrecursionlimit(500)


def non_str_input(self):
    # TODO do this in python_runner, then return early
    line = self.line
    self.line = ""

    if line == 1:
        raise KeyboardInterrupt
    elif line == 2:
        raise RuntimeError(
            "The service worker for reading input isn't working. "
            "Try closing all this site's tabs, then reopening. "
            "If that doesn't work, try using a different browser."
        )
    elif line == 3:
        raise RuntimeError(
            "This browser doesn't support reading input. "
            "Try upgrading to the most recent version or switching to a different browser, "
            "e.g. Chrome or Firefox. "
        )
    else:
        PatchedStdinRunner.non_str_input(self)


try:
    from python_runner import PatchedStdinRunner
except Exception:
    pass
else:
    PatchedStdinRunner.non_str_input = non_str_input


def find_imports_to_install(imports):
    to_install = []
    for module in imports:
        try:
            importlib.import_module(module)
        except ModuleNotFoundError:
            to_install.append(module)
    return to_install


async def install_imports(source_code):
    try:
        imports = pyodide.find_imports(source_code)
    except SyntaxError:
        return

    to_install = find_imports_to_install(imports)
    if to_install:
        try:
            import micropip  # noqa
        except ModuleNotFoundError:
            await pyodide_js.loadPackage("micropip")
            import micropip  # noqa

        to_package_name = pyodide_js._module._import_name_to_package_name.to_py()
        packages_names = [to_package_name.get(mod, mod) for mod in to_install]
        await micropip.install(packages_names)
