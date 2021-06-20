"""
Run this file to generate files under frontend/src:

- chapters.json
- python_core.tar
- book/pages.json.load_by_url

When developing, you generally want this to run any time you make a change to the code.
You probably want a file watcher utility to do this for you automatically.
For example, you could use watchdog (https://github.com/gorakhargosh/watchdog):

    pip install 'watchdog[watchmedo]'
    PYTHONPATH=. watchmedo shell-command core \
        --recursive \
        --ignore-directories \
        --ignore-pattern '*~' \
        --drop \
        --command "python core/generate_static_files.py"
"""


import os
import sys
import tarfile
from pathlib import Path

from littleutils import strip_required_prefix, json_to_file

from core.text import pages, get_pages, chapters
from core.utils import site_packages
from core.workers.worker import run_code


def run_steps():
    for page_index, page in enumerate(pages.values()):
        for step_index, step_name in enumerate(page.step_names[:-1]):
            step = page.get_step(step_name)

            for substep in [*step.messages, step]:
                program = substep.program

                if "\n" in program:
                    code_source = step.expected_code_source or "editor"
                else:
                    code_source = "shell"

                entry = dict(
                    input=program,
                    source=code_source,
                    page_slug=page.slug,
                    step_name=step_name,
                )

                run_code(entry, input_callback=None, result_callback=lambda _: 0)


def get_roots():
    run_steps()
    roots = set()
    mod_names = []
    for module in list(sys.modules.values()):
        try:
            f = module.__file__ or ""
        except AttributeError:
            continue

        if not f.startswith(site_packages):
            continue

        relative = strip_required_prefix(f, site_packages)
        root = relative.split(os.path.sep)[0]
        roots.add(root)

        mod_names.append(module.__name__)

    return sorted(roots)


def tarfile_filter(tar_info):
    name = tar_info.name
    if any(
        x in name
        for x in [
            "__pycache__",
            "friendly/locales",
            "birdseye/static",
            "pygments/lexers",
        ]
    ) or name.endswith(".pyc"):
        return None
    return tar_info


def main():
    print("Generating files...")
    this_dir = Path(__file__).parent
    frontend_src = this_dir / "../frontend/src"

    json_to_file(get_pages(), frontend_src / "book/pages.json.load_by_url")
    json_to_file(chapters, frontend_src / "chapters.json")

    roots = get_roots()
    core_imports = "\n".join(roots)
    core_imports_path = this_dir / "core_imports.txt"
    if os.environ.get("FIX_CORE_IMPORTS"):
        core_imports_path.write_text(core_imports)
    elif core_imports_path.read_text() != core_imports:
        raise ValueError(
            f"core_imports.txt is out of date, run with FIX_CORE_IMPORTS=1.\n"
            f"{core_imports}\n!=\n{core_imports_path.read_text()}"
        )

    with tarfile.open(frontend_src / "python_core.tar", "w") as tar:
        tar.add(this_dir, arcname=this_dir.stem, recursive=True, filter=tarfile_filter)
        for root in roots:
            tar.add(
                Path(site_packages) / root,
                arcname=root,
                recursive=True,
                filter=tarfile_filter,
            )
        for filename in ("__init__.py", "_mapping.py", "python.py"):
            arcname = str("pygments/lexers/" + filename)
            tar.add(Path(site_packages) / arcname, arcname=arcname)

    print("Done.")


if __name__ == "__main__":
    main()
