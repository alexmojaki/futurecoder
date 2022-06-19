import os

import python_runner
import snoop.tracer

from ..utils import internal_dir

snoop.tracer.internal_directories += (
    internal_dir,
    os.path.dirname(python_runner.__file__),
)
