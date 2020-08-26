import ast
import inspect
from datetime import datetime

import birdseye.bird
from birdseye.bird import BirdsEye

from main.utils import rows_to_dicts

from .worker import console, execute

birdseye.bird.get_unfrozen_datetime = datetime.now

# Import necessary files before limit is set
str(BirdsEye("sqlite://").db)


def exec_birdseye(filename, code):
    # Create database in memory
    eye = BirdsEye("sqlite://")
    traced_file = eye.compile(code, filename)
    eye._trace('<module>', filename, traced_file, traced_file.code, 'module', code)
    console.locals = eye._trace_methods_dict(traced_file)

    nodes_by_lineno = {
        node.lineno: node
        for node in traced_file.nodes
        if isinstance(node, ast.FunctionDef)
    }

    def find_code(root_code):
        """
        Trace all functions recursively, like trace_module_deep.
        """
        for code_obj in root_code.co_consts:
            if not inspect.iscode(code_obj) or code_obj.co_name.startswith('<'):
                continue

            find_code(code_obj)

            lineno = code_obj.co_firstlineno
            node = nodes_by_lineno.get(lineno)
            if not node:
                continue

            eye._trace(
                code_obj.co_name, filename, traced_file, code_obj,
                typ='function',
                source=code,
                start_lineno=lineno,
                end_lineno=node.last_token.end[0] + 1,
            )

    find_code(traced_file.code)

    execute(traced_file.code)
    with eye.db.session_scope() as session:
        objects = session.query(eye.db.Call, eye.db.Function).all()
        calls, functions = [rows_to_dicts(set(column)) for column in zip(*objects)]
    return dict(calls=calls, functions=functions)
