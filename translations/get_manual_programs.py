from collections import defaultdict

import polib
from pathlib import Path

from littleutils import json_to_file


def main():
    this_dir = Path(__file__).parent
    locales = this_dir / "locales"
    result = defaultdict(dict)

    for lang_dir in locales.iterdir():
        mofile = polib.mofile(str(lang_dir / "LC_MESSAGES/futurecoder.mo"))
        for entry in mofile:
            if entry.msgid.endswith(".program"):
                result[entry.msgid][lang_dir.name] = entry.msgstr.splitlines()

    json_to_file(result, this_dir / "manual_programs.json", indent=4, sort_keys=True)


main()
