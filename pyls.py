import argparse
import dataclasses
import datetime
import grp
import locale
import pathlib
import pwd
import stat
import sys
import shutil
from typing import List, Iterable, Tuple, Any

""" 
The ls command uses a locale-specific string sorting function, resulting in sort orders such as e.g. ["a", ".b", "c"],
while the order obtained by the default sort would be [".b", "a", "c"]. To achieve the same result, we can configure 
python to use the user's locale and use the locale.strxfrm as the sorting key.

The following line applies the user's locale. While this is not a great idea in library code, pyls is meant to run as a 
standalone program, so this should be OK. For more information, refer to
https://docs.python.org/3/library/locale.html#background-details-hints-tips-and-caveats
"""
locale.setlocale(locale.LC_ALL, '')


@dataclasses.dataclass()
class Config:
    """ This class stores the parameters with which pyls was invoked. """
    list_format: bool = False
    show_all: bool = False
    sort_by_size: bool = False
    recursive: bool = False
    use_column_layout: bool = False
    paths: List[str] = dataclasses.field(default_factory=lambda: ["."])


CONFIG = Config()


def main():
    """
    This is the main entry point for the pyls command. The results are printed to stdout.

    Exit codes are set as described in the ls command man page:
        "0 if OK,
        1 if minor problems (e.g., cannot access subdirectory),
        2 if serious trouble (e.g., cannot access command-line argument)."
    """
    global CONFIG
    CONFIG = get_configuration_from_command_line_args()
    CONFIG.use_column_layout = True
    try:
        for line in ls_lines():
            print(line)
    except (FileNotFoundError, PermissionError) as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(e)
        sys.exit(2)
    sys.exit(0)


def get_configuration_from_command_line_args() -> Config:
    """ Parse the command line args and convert them to a Config object. """
    parser = argparse.ArgumentParser(description='A Python implementation of the UNIX ls command.')
    parser.add_argument('paths', nargs='*', default=['.'])
    parser.add_argument('-l', action='store_true')
    parser.add_argument('-a', action='store_true')
    parser.add_argument('-S', action='store_true')
    parser.add_argument('-R', action='store_true')
    args = parser.parse_args()
    return Config(
        list_format=args.l,
        show_all=args.a,
        sort_by_size=args.S,
        recursive=args.R,
        paths=args.paths,
    )


def ls_string() -> str:
    """ Collect the pyls output to a single string. Mostly used for testing. """
    joined_lines = "\n".join(ls_lines())
    if joined_lines:  # only add trailing newline to non-empty output
        joined_lines += "\n"
    return joined_lines


def ls_lines() -> Iterable[str]:
    """ Iterate over the pyls output line by line. """

    # Use two flags to determine if we need to add path headers and leading newlines, see other comment below:
    list_multiple_dirs = (len(CONFIG.paths) > 1) or CONFIG.recursive
    is_first_dir = True

    # Traverse the directory structure.
    stack = sorted((pathlib.Path(p) for p in CONFIG.paths),
                   key=_sort_key, reverse=True)
    while stack:
        base_path = stack.pop()

        """ In recursive mode or if multiple path arguments are given, we first print a header indicating the current 
        directory. This header should have a leading newline, unless it is the first line of the output. Since this 
        requires some awareness of the outer loop, we return the header line here, rather than in
        format_lines_single_dir function. """

        if list_multiple_dirs:
            newline = "" if is_first_dir else "\n"
            yield f"{newline}{base_path}:"
            is_first_dir = False

        yield from format_lines_single_dir(base_path)

        if CONFIG.recursive:
            _populate_stack_for_recursive_execution(base_path, stack)


def format_lines_single_dir(base_path: pathlib.Path) -> Iterable[str]:
    """
    Format the lines for the output based on the provided pathlib.Path instances. This does not include the path
    headers ("/some/path:") in recursive mode or when executing pyls with multiple path arguments.
    """
    paths = list(_iter_single_dir_children(base_path))
    if CONFIG.list_format:
        yield from _lines_of_single_dir_in_list_format(base_path, paths)
    else:
        yield from _lines_of_single_dir_content_in_short_format(base_path, paths)


def _lines_of_single_dir_in_list_format(base_path: pathlib.Path,
                                        paths: List[pathlib.Path]) -> Iterable[str]:
    """
    Iterate over the formatted rows corresponding to the contents of a single directory in long list format.
    """
    yield f"total {_total_num_blocks(paths)}"
    rows = [_single_row_data_in_list_format(base_path, p) for p in paths]

    col_widths = None
    if rows:
        col_widths = [max(len(r[col_idx]) for r in rows) for col_idx in range(6)]
        col_widths.append(0)

    left_align = lambda s, w: s.ljust(w)
    right_align = lambda s, w: s.rjust(w)
    no_align = lambda s, w: s

    alignments = [
        no_align,  # filemode
        right_align,  # num links
        left_align,  # user
        left_align,  # group
        right_align,  # size_bytes
        left_align,  # last modified
        no_align,  # name
    ]

    for row in rows:
        yield " ".join(align(val, col_width) for (val, col_width, align) in zip(row, col_widths, alignments))


def _total_num_blocks(paths: List[pathlib.Path]) -> int:
    """ Calculates the total number of blocks allocated for the paths. """
    blocks = 0
    for p in paths:
        blocks += p.lstat().st_blocks
    # Divide by two, since st_blocks assumes blocksize of 512, while ls uses 1024:
    # https://docs.python.org/3/library/os.html#os.stat_result.st_blocks
    # https://unix.stackexchange.com/questions/28780/file-block-size-difference-between-stat-and-ls
    return blocks // 2


def _single_row_data_in_list_format(base_path: pathlib.Path,
                                    p: pathlib.Path) -> Tuple[str, str, str, str, str, str, str]:
    """ Collect all items required to print a row in the long list format to a single tuple. """
    lstat = p.lstat()

    filemode = stat.filemode(lstat.st_mode)
    num_links_dirs = str(lstat[stat.ST_NLINK])

    # User and Group code adapted from
    # https://stackoverflow.com/questions/1830618/how-to-find-the-owner-of-a-file-or-directory-in-python
    user = str(pwd.getpwuid(lstat.st_uid).pw_name)
    group = str(grp.getgrgid(lstat.st_uid).gr_name)

    size_bytes = str(lstat.st_size)
    last_modified = _last_modified_time_str(lstat)
    name = _printable_path_name(base_path, p)

    if p.is_symlink():
        name = f"{name} -> {p.resolve()}"

    return filemode, num_links_dirs, user, group, size_bytes, last_modified, name


def _lines_of_single_dir_content_in_short_format(base_path: pathlib.Path,
                                                 paths: List[pathlib.Path]) -> Iterable[str]:
    """
    This function defines the layout of results in the pyls execution without arguments. The algorithm which arranges
    results in columns was ported from the original ls source code.
    """
    path_strings = [_printable_path_name(base_path, p) for p in paths]
    if not CONFIG.use_column_layout:
        yield from path_strings  # yield one path name per line
    else:
        yield from _lines_in_short_format_many_per_line(path_strings)


@dataclasses.dataclass
class ColumnInfo:
    num_cols: int
    col_array: List[int]
    line_len: int = 0
    is_valid: bool = True


def _lines_in_short_format_many_per_line(path_strings: List[str]) -> Iterable[str]:
    """
    This function arranges the output of the pyls command into columns.

    It is a direct port of the original print_many_per_line function in the coreutiles ls source code,
    available at https://www.gnu.org/software/coreutils/, version 5.0, file src/ls.c lines 3485 - 3562.
    """

    terminal_size = shutil.get_terminal_size()
    layout = _get_optimal_column_layout(path_strings, terminal_size)
    num_files = len(path_strings)
    # there are num_files / num_cols many rows, plus maybe one that is not entirely filled
    num_rows = num_files // layout.num_cols + int(num_files % layout.num_cols != 0)
    for row_idx in range(num_rows):
        col_idx = 0
        file_index = row_idx
        row_names = []
        while True:
            max_name_length_in_col = layout.col_array[col_idx]
            row_names.append(path_strings[file_index].ljust(max_name_length_in_col))
            col_idx += 1
            file_index += num_rows
            if file_index >= num_files:
                break
        yield "".join(row_names)


def _get_optimal_column_layout(path_strings, terminal_size) -> ColumnInfo:
    """
    This function determines the optimal number of columns for the output of the pyls command.

    It is a direct port of the original print_many_per_line function in the coreutiles ls source code,
    available at https://www.gnu.org/software/coreutils/, version 5.0, file src/ls.c lines 3485 - 3562.
    """

    max_possible_cols = max(1, terminal_size.columns // 3)
    col_layouts = [ColumnInfo(num_cols=i, col_array=[0] * i) for i in range(1, max_possible_cols)]
    for p_idx, p in enumerate(path_strings):
        real_length = len(p) + 2  # (2 if p_idx != 0 else 0)
        for col, col_layout in enumerate(col_layouts, 1):
            if not col_layout.is_valid:
                continue
            idx = p_idx // ((len(path_strings) + col - 1) // (col))
            if real_length > col_layout.col_array[idx]:
                col_layout.line_len += real_length - col_layout.col_array[idx]
                col_layout.col_array[idx] = real_length
                col_layout.is_valid = col_layout.line_len < terminal_size.columns
    valid_col = col_layouts[-1]
    for c in reversed(col_layouts):
        if c.is_valid:
            valid_col = c
            break
    return valid_col


def _printable_path_name(base_path: pathlib.Path, p: pathlib.Path) -> str:
    """
    Converts the path object to the name that should be shown in the ls output. The base_path is required to check
    for the special directories . and ..
    """
    name = p.name
    # The main reason for this function is the formatting of the . and .. dirs:
    if p == base_path:
        name = "."
    elif p == base_path.parent:
        name = ".."
    return name


def _last_modified_time_str(lstat) -> str:
    """
    Get the string representing the time of the last modification.

    For files modified within the past 6 months, a date format indicating the day, month and daytime is used.
    For files older than 6 months, a different date format indicating the day, month and year is used.
    """
    last_modified = datetime.datetime.fromtimestamp(lstat.st_mtime)
    # The constant 31556952 is used in the ls source code, available at https://www.gnu.org/software/coreutils/.
    # It roughly represents the number of seconds in a Gregorian year.
    six_months_in_seconds = 31556952 // 2
    if (datetime.datetime.now() - last_modified) < datetime.timedelta(seconds=six_months_in_seconds):
        date_format = "%b %e %H:%M"
    else:
        date_format = "%b %e  %Y"
    return last_modified.strftime(date_format)


def _iter_single_dir_children(path: pathlib.Path) -> Iterable[pathlib.Path]:
    """
    Iterate over the children of a directory in sorted order.

    Compared to calling path.iterdir(), this function:

      1. Returns the paths in sorted order depending on the CONFIG.sort_by_size parameter
      2. Includes the special paths . and .., which are not returned by pathlib.Path.iterdir
    """
    children = list(path.iterdir())
    if CONFIG.show_all:
        if CONFIG.sort_by_size:
            # In size-sorted output, . and .. are sorted together with the other paths
            children.append(path)
            children.append(path / "..")
        else:
            # In name-sorted output, . and .. should always be yielded first
            yield path
            yield path / ".."
    for p in sorted(children, key=_sort_key):
        if _is_hidden_path(p):
            continue
        yield p


def _populate_stack_for_recursive_execution(base_path: pathlib.Path,
                                            stack: List[pathlib.Path]):
    if base_path.is_symlink():
        return  # don't enter symlinks
    if _is_hidden_path(base_path):
        return
    children = sorted(base_path.iterdir(), key=_sort_key, reverse=True)
    for c in children:
        if _is_hidden_path(c):
            continue
        if c.is_dir() and not c.is_symlink():
            stack.append(c)


def _is_hidden_path(p: pathlib.Path) -> bool:
    """ Determine if the path should be excluded from the pyls output. """
    return not CONFIG.show_all and p.name.startswith(".")


def _sort_key(path: pathlib.Path) -> Any:
    """
    The sorting key used throughout the program. Depending on the CONFIG.sort_by_size parameter, the key is a string
    representing the path name, or a tuple of an integer containing the negative size of the path and the name key in
    order to resolve ties.
    """
    if CONFIG.sort_by_size:
        # use the negative size, as largest files should be printed first
        # make a tuple with the name key as the second element to resolve ties.
        return (-path.lstat().st_size,
                locale.strxfrm(str(path)))
    else:
        return locale.strxfrm(str(path))


if __name__ == '__main__':
    main()
