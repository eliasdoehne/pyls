import os
import pathlib
import subprocess

import pytest

from pyls import pyls  # TODO fix this
from .test_data import PATHS


def _make_test_path(path: pathlib.Path):
    if os.path.exists(path):
        raise ValueError(f"Abort: Path {path} already exists.")
    path.mkdir(parents=True)


def _make_test_file(filepath: pathlib.Path, size_bytes=0):
    if os.path.exists(filepath):
        raise ValueError(f"Abort: File {filepath} already exists.")
    filepath.write_bytes(b"a" * size_bytes)


@pytest.fixture(scope="session", name="test_base_dir")
def setup_test_dirs(tmp_path_factory) -> pathlib.Path:
    """
    Create the directory structure and files required for the various test cases,
    as specified in the PATHS dictionary in test_data.py.

    All files and directories are created in temporary locations, e.g.
    /tmp/pytest-of-elias/pytest-10/pyls_test_dir-0/empty


    :param tmp_path_factory: used to make a temporary base directory, see https://docs.pytest.org/en/latest/tmpdir.html
    :return:
    """
    base_path = tmp_path_factory.mktemp("pyls_test_dir_")
    for test_case_name, dirs_files_dict in PATHS.items():
        test_path = base_path / test_case_name
        _make_test_path(test_path)
        for dir_path in dirs_files_dict.get("dirs", []):
            _make_test_path(test_path / dir_path)
        for fname, size in dirs_files_dict.get("files", []):
            _make_test_file(test_path / fname, size_bytes=size)
    return base_path


@pytest.mark.parametrize("test_path", list(PATHS.keys()))
@pytest.mark.parametrize("show_all", [False, True])
def test_compare_to_system_ls(test_path: str,
                              test_base_dir: pathlib.Path,
                              show_all: bool):
    path = test_base_dir / test_path
    assert path.exists()

    subprocess_args = ["ls"]
    if show_all:
        subprocess_args.append("-a")
    subprocess_args.append(path)

    ls_run = subprocess.run(subprocess_args, capture_output=True)
    sys_ls_result = ls_run.stdout.decode('utf-8')

    pyls.CONFIG.paths = [path]
    pyls.CONFIG.show_all = show_all

    assert sys_ls_result == pyls.ls_string()
