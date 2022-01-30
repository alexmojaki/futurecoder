"""
Run this file to generate files under frontend/src:

- chapters.json
- python_core.tar.load_by_url
- book/pages.json.load_by_url

When developing, you generally want this to run any time you make a change to the code.
You probably want a file watcher utility to do this for you automatically.
For example, you could use watchdog (https://github.com/gorakhargosh/watchdog):

    pip install 'watchdog[watchmedo]'
    watchmedo shell-command core \
        --recursive \
        --ignore-directories \
        --ignore-pattern '*~' \
        --drop \
        --command "python -m core.generate_static_files"
"""

import os
import shutil
import sys
import tarfile
from pathlib import Path

import birdseye
from littleutils import strip_required_prefix, json_to_file, file_to_json
from markdown import markdown

from core import translation as t
from core.checker import check_entry
from core.runner.utils import site_packages
from core.text import get_pages, step_test_entries, load_chapters
from core.utils import unwrapped_markdown, new_tab_links

str("import sentry_sdk after core.utils for stubs")
import sentry_sdk  # noqa imported lazily

this_dir = Path(__file__).parent
frontend = this_dir / "../frontend"
frontend_src = frontend / "src"


def run_steps():
    for *_, entry in step_test_entries():
        check_entry(entry, input_callback=None, output_callback=lambda _: 0)


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


def frontend_terms():
    for key, value in file_to_json(frontend_src / "english_terms.json").items():
        translation = t.get(f"frontend.{key}", value)

        if "\n" in translation:
            value = markdown(translation)
        else:
            value = unwrapped_markdown(translation)

        result = new_tab_links(value)
        if value != result:
            assert key.startswith("question_wizard_")

        yield key, result


def main():
    print("Generating files...")
    t.set_language(os.environ.get("FUTURECODER_LANGUAGE", "en"))

    json_to_file(list(load_chapters()), frontend_src / "chapters.json")
    json_to_file(get_pages(), frontend_src / "book/pages.json.load_by_url")
    json_to_file(dict(frontend_terms()), frontend_src / "terms.json", indent=4)

    birdseye_dest = frontend / "public/birdseye"
    shutil.rmtree(birdseye_dest, ignore_errors=True)
    shutil.copytree(Path(birdseye.__file__).parent / "static", birdseye_dest, dirs_exist_ok=True)

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

    with tarfile.open(frontend_src / "python_core.tar.load_by_url", "w") as tar:
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
