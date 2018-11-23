import contextlib
import os
import pathlib
import subprocess

import pytest

import pyls
from .test_data import PATHS


@contextlib.contextmanager
def ch_dir_context(target: pathlib.Path):
    """ This context manager allows executing the tests from a different directory. """
    cwd = pathlib.Path.cwd()
    os.chdir(target)
    yield
    os.chdir(cwd)


@pytest.fixture(scope="session", name="test_base_dir")
def setup_test_dirs(tmp_path_factory) -> pathlib.Path:
    """
    Create the directory structure and files required for the various test cases, as specified in the PATHS dictionary
    in test_data.py. All files and directories are created in temporary locations, e.g.
    /tmp/pytest-of-elias/pytest-10/pyls_test_dir-0/empty

    :param tmp_path_factory: used to make a temporary base directory, see https://docs.pytest.org/en/latest/tmpdir.html
    """
    base_path = tmp_path_factory.mktemp("pyls_test_dir_")

    for test_case_name, dirs_files_dict in PATHS.items():
        test_path = base_path / test_case_name
        _make_test_directory(test_path)
        for dir_path in dirs_files_dict.get("dirs", []):
            _make_test_directory(test_path / dir_path)
        for fname, size in dirs_files_dict.get("files", []):
            _make_test_file(test_path / fname, size_bytes=size)
        for name, target in dirs_files_dict.get("symlinks", []):
            _make_test_symlink(test_path / name, test_path / target)

    return base_path


def _make_test_directory(path: pathlib.Path):
    """ Make an empty directory at the specified location. """
    if os.path.exists(path):
        raise ValueError(f"Abort: Path {path} already exists.")
    path.mkdir(parents=True)


def _make_test_file(filepath: pathlib.Path, size_bytes=0):
    """ Make a new file at the specified location containing size_bytes many bytes of text. """
    if os.path.exists(filepath):
        raise ValueError(f"Abort: File {filepath} already exists.")
    filepath.write_bytes(b"a" * size_bytes)


def _make_test_symlink(path: pathlib.Path, target_path: pathlib.Path):
    """ Make a new symlink at the location given by path, pointing to the target_path. """
    if os.path.exists(path):
        raise ValueError(f"Abort: {path} already exists.")
    path.symlink_to(target=target_path)


def run_system_ls(path, list_format=False, recursive=False, show_all=False, sort_by_size=False) -> str:
    """ Executes the system ls command with the given arguments and returns the stdout output. """
    subprocess_args = []
    if show_all:
        subprocess_args.append("-a")
    if recursive:
        subprocess_args.append("-R")
    if list_format:
        subprocess_args.append("-l")
    if sort_by_size:
        subprocess_args.append("-S")
    subprocess_args.append(path)
    ls_run = subprocess.run(["ls"] + subprocess_args, capture_output=True)
    return ls_run.stdout.decode('utf-8')


def run_pyls(path, list_format=False, recursive=False, show_all=False, sort_by_size=False) -> str:
    """ Executes the pyls command with the given arguments and returns the output. """
    pyls.CONFIG.paths = [str(path)]
    pyls.CONFIG.show_all = show_all
    pyls.CONFIG.recursive = recursive
    pyls.CONFIG.list_format = list_format
    pyls.CONFIG.sort_by_size = sort_by_size
    return pyls.ls_string()


@pytest.mark.parametrize("show_all", [False, True])
@pytest.mark.parametrize("relative_path", [False, True])
@pytest.mark.parametrize("sort_by_size", [False, True])
@pytest.mark.parametrize("recursive", [False, True])
@pytest.mark.parametrize("list_format", [False, True])
@pytest.mark.parametrize("test_case", PATHS)
def test_compare_to_system_ls(test_base_dir: pathlib.Path,
                              test_case: str,
                              relative_path: bool,
                              sort_by_size: bool,
                              show_all: bool,
                              recursive: bool,
                              list_format: bool):
    """
    Test the pyls implementation against the output of the system ls command.

    Based on the PATHS dictionary defined in test_data.py, the pytest fixture test_base_dir, defined above,
    creates a directory structure and some (small) test files in a temporary directory. The tests run the system
    ls command via subprocess.run, as well as the pyls implementation with all combinations of supported parameters.
    The result of pyls is compared against the captured stdout of the ls subprocess.

    :param test_base_dir: fixture for a base directory, defined above in setup_test_dirs
    :param test_case: Identifier of the test case, i.e. a key in the PATHS dictionary.
    :param relative_path: Change the working directory and use a relative path to invoke the ls commands
    :param sort_by_size: Use the -S option
    :param show_all: Use the -a option
    :param recursive: Use the -R option
    :param list_format: Use the -l option
    """
    if relative_path:
        working_directory = test_base_dir
        path = test_case
    else:
        working_directory = pathlib.Path.cwd()
        path = test_base_dir / test_case

    assert working_directory.exists()

    with ch_dir_context(working_directory):
        sys_ls_result = run_system_ls(path,
                                      list_format=list_format,
                                      recursive=recursive,
                                      show_all=show_all,
                                      sort_by_size=sort_by_size)
        py_ls_result = run_pyls(path,
                                list_format=list_format,
                                recursive=recursive,
                                show_all=show_all,
                                sort_by_size=sort_by_size)

        print_if_different(py_ls_result, sys_ls_result)
        assert sys_ls_result == py_ls_result


@pytest.mark.skip
@pytest.mark.parametrize("path", [".", "/", pathlib.Path.home()])
@pytest.mark.parametrize("list_format", [False, True])
@pytest.mark.parametrize("show_all", [False, True])
def test_compare_to_system_ls_special_paths(path,
                                            list_format,
                                            show_all):
    """
    Test the pyls implementation against the output of the system ls command. Similar to test_compare_to_system_ls,
    except that this test runs pyls on:

        - filesystem root
        - user's home directory
        - current directory

    For performance reasons, the recursive option is omitted for this test.

    Since the test inspects important locations beyond the scope of this project, it is disabled by default.
    To run it, remove the @pytest.mark.skip decorator.
    """
    sys_ls_result = run_system_ls(path,
                                  list_format=list_format,
                                  show_all=show_all)
    py_ls_result = run_pyls(path,
                            list_format=list_format,
                            show_all=show_all)

    print_if_different(py_ls_result, sys_ls_result)
    assert sys_ls_result == py_ls_result


def print_if_different(py_ls_result, sys_ls_result):
    if sys_ls_result != py_ls_result:
        print("\n==== CONFIGURATION ====")
        print(pyls.CONFIG)
        print("\n==== EXPECTED ====")
        print(sys_ls_result)
        print("==================")
        print("\n==== OBTAINED ====")
        print(py_ls_result)
        print("==================")
