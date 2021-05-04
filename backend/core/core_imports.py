import os
import sys

from littleutils import strip_required_prefix

from core.utils import site_packages
from core.text import pages

sys.modules["django"] = None

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


if __name__ == '__main__':
    print(" ".join(get_roots()))
