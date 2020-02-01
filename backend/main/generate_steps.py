from textwrap import indent

current_text = ""
current_program = ""

input_text = """
Fill this in with some markdown.
"""

for line in input_text.splitlines(keepends=True):
    if line.startswith(" " * 4):
        current_program += line
    else:
        if current_program:
            print(f'''\
    class step_name_here(VerbatimStep):
        """
{current_text.strip()}

__program_indented__
        """

        def program(self):
{indent(current_program, " " * 8).rstrip()}
''')
            current_text = ""
            current_program = ""
            program_lines = []
        current_text += line
print(f'''\
    final_text = """
{current_text.strip()}
    """
''')
