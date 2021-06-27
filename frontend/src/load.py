import io
import tarfile
import sys

package_path = "/tmp/package/"
sys.path.append(package_path)
tarfile.TarFile.chown = lambda *_, **__: None


def load_package_buffer(buffer):
    global run_code_catch_internal_errors
    fd = io.BytesIO(buffer.to_py())
    with tarfile.TarFile(fileobj=fd) as zf:
        zf.extractall(package_path)

    from core.workers.worker import run_code_catch_internal_errors  # noqa trigger imports
    print("Python core ready!")
