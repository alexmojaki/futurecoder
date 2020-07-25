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
    execute(traced_file.code)
    with eye.db.session_scope() as session:
        objects = session.query(eye.db.Call, eye.db.Function).all()
        calls, functions = [rows_to_dicts(set(column)) for column in zip(*objects)]
    return dict(calls=calls, functions=functions)
