import os
import pathlib
import subprocess

import pytest

from .test_data import PATHS


def _make_test_path(path: pathlib.Path):
    if os.path.exists(path):
        raise ValueError(f"Abort: Path {path} already exists.")
    path.mkdir(parents=True)


def _make_test_file(filepath: pathlib.Path, size_bytes=0):
    if os.path.exists(filepath):
        raise ValueError(f"Abort: Path {filepath} already exists.")
    with open(filepath, "w") as f:
        for _ in range(size_bytes):
            f.write("a")


@pytest.fixture(scope="session")
def test_base_dir(tmpdir_factory):
    """
    Create the directory structure and files required for the various test cases,
    as specified in the PATHS dictionary in test_data.py.

    All files and directories are created in temporary locations, e.g.
    /tmp/pytest-of-elias/pytest-10/pyls_test_dir-0/empty


    :param tmpdir_factory: fixture to obtain the base directory, see https://docs.pytest.org/en/2.8.7/tmpdir.html
    :return:
    """
    base_path = pathlib.Path(tmpdir_factory.mktemp("pyls_test_dir-"))

    for test_case_name, dirs_files_dict in PATHS.items():
        test_path = base_path / test_case_name
        _make_test_path(test_path)
        for dir_path in dirs_files_dict["dirs"]:
            path = test_path / dir_path
            _make_test_path(path)
        for fname, size in dirs_files_dict["files"]:
            _make_test_file(test_path / fname, size_bytes=size)

    return base_path


@pytest.mark.parametrize(
    "test_path",
    ["empty"],
)
def test_compare_to_ls_ignoring_whitespace_no_args(test_path, test_base_dir):
    path = test_base_dir / test_path
    assert path.exists()
    command = ["ls", str(path)]
    ls_run = subprocess.run(command, capture_output=True)
    ls_sys_result = ls_run.stdout.decode('utf-8')
    assert list(ls_sys_result.split()) == []
