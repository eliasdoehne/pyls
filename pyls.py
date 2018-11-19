import argparse
import dataclasses
import datetime
import grp
import pathlib
import pwd
import stat
import sys
from typing import List, Iterable, Union, Tuple


@dataclasses.dataclass()
class Config:
    list_format: bool = False
    show_all: bool = False
    sort_by_size: bool = False
    recursive: bool = False
    paths: List[str] = dataclasses.field(default_factory=lambda: ["."])


CONFIG = Config()


def ls_string() -> str:
    joined_lines = "\n".join(ls_lines())
    if joined_lines:  # only add trailing newline to non-empty output
        joined_lines += "\n"
    return joined_lines


def ls_lines() -> Iterable[str]:
    # Keep two flags to determine if we need to add path headers and leading newlines:
    list_multiple_dirs = (len(CONFIG.paths) > 1) or CONFIG.recursive
    is_first_dir = True

    # Traverse the directory structure.
    q = sorted((pathlib.Path(p) for p in CONFIG.paths),
               key=_sort_key, reverse=True)
    while q:
        base_path = q.pop()
        if list_multiple_dirs:
            newline = "" if is_first_dir else "\n"
            yield f"{newline}{base_path}:"
            is_first_dir = False

        yield from make_lines(base_path)

        if CONFIG.recursive:
            _populate_queue_for_recursive_option(base_path, q)


def make_lines(base_path: pathlib.Path) -> Iterable[str]:
    """
    Convert the pathlib.Path instances to formatted lines.

    :return:
    """
    paths = _iter_single_dir(base_path)
    if CONFIG.list_format:
        paths = list(paths)  # need to iterate twice to calculate block count
        yield f"total {_total_blocks(paths)}"
        yield from _lines_in_list_format(base_path, paths)
    else:
        for p in paths:
            yield _path_name(base_path, p)


def _total_blocks(paths: List[pathlib.Path]):
    blocks = 0
    for p in paths:
        blocks += p.lstat().st_blocks
    # Divide by two, since st_blocks assumes blocksize of 512, while ls uses 1024:
    # https://docs.python.org/3/library/os.html#os.stat_result.st_blocks
    # https://unix.stackexchange.com/questions/28780/file-block-size-difference-between-stat-and-ls
    return blocks // 2


def _lines_in_list_format(base_path, paths):
    rows = [_get_list_row(base_path, p) for p in paths]
    # All columns except the last should be right-aligned
    col_widths = None
    if rows:
        col_widths = [max(len(r[col_idx]) for r in rows) for col_idx in range(6)]
    for row in rows:
        yield "{} {} {} {} {} {} {}".format(*(
            val.rjust(col_widths[i]) if i < 6 else val
            for (i, val) in enumerate(row)
        ))


def _get_list_row(base_path, p: pathlib.Path) -> Tuple[str, str, str, str, str, str, str]:
    lstat = pathlib.Path(p).lstat()

    filemode = stat.filemode(lstat.st_mode)
    num_links_dirs = str(lstat[stat.ST_NLINK])

    # User and Group code adapted from
    # https://stackoverflow.com/questions/1830618/how-to-find-the-owner-of-a-file-or-directory-in-python
    user = str(pwd.getpwuid(lstat.st_uid).pw_name)
    group = str(grp.getgrgid(lstat.st_uid).gr_name)

    size_bytes = str(lstat.st_size)
    last_modified = _last_modified_time_str(lstat)
    name = _path_name(base_path, p)
    return filemode, num_links_dirs, user, group, size_bytes, last_modified, name


def _path_name(base_path: pathlib.Path, p: pathlib.Path) -> str:
    name = p.name
    if p == base_path:
        name = "."
    elif p == base_path.parent:
        name = ".."
    return name


def _last_modified_time_str(lstat) -> str:
    last_modified = datetime.datetime.fromtimestamp(lstat.st_mtime)
    # For files older than 6 months, a different date format is used.
    # The constant 31556952 is used in the ls source code, available at
    # http://ftp.gnu.org/gnu/coreutils/
    # It roughly represents the number of seconds in a Gregorian year.
    if (datetime.datetime.now() - last_modified) < datetime.timedelta(seconds=31556952 // 2):
        date_format = "%b %e %H:%M"
    else:
        date_format = "%b %e  %Y"
    return last_modified.strftime(date_format)


def _iter_single_dir(path) -> Iterable[pathlib.Path]:
    if CONFIG.sort_by_size:
        yield from _iter_dir_by_size(path)
    else:
        yield from _iter_dir_by_name(path)


def _iter_dir_by_size(path: pathlib.Path) -> Iterable[pathlib.Path]:
    raise NotImplementedError("TODO")


def _iter_dir_by_name(path: pathlib.Path) -> Iterable[pathlib.Path]:
    if CONFIG.show_all:
        yield path
        yield path.parent
    for p in sorted(path.iterdir(), key=_sort_key):
        if not CONFIG.show_all and p.name[0] == '.':
            continue
        yield p


def _populate_queue_for_recursive_option(base_path: pathlib.Path,
                                         queue: List[pathlib.Path]):
    children = sorted(base_path.iterdir(), key=_sort_key)
    while children:
        c = children.pop()
        if c.is_dir():
            queue.append(c)


def _sort_key(path: pathlib.Path) -> str:
    key = path.name.lower()
    if key[0] == '.':
        return key[1:]
    return key


def get_configuration_from_command_line_args() -> Config:
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


def main():
    global CONFIG
    CONFIG = get_configuration_from_command_line_args()
    try:
        for line in ls_lines():
            print(line)
    except FileNotFoundError as e:
        # 1 if minor problems (e.g., cannot access subdirectory),
        print(e)
        sys.exit(1)
    except Exception as e:
        # 2 if serious trouble (e.g., cannot access command-line argument).
        print(e)
        sys.exit(2)


if __name__ == '__main__':
    main()
