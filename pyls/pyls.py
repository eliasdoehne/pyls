import argparse

import dataclasses
import pathlib
from typing import List, Iterable, Union


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
    for root in CONFIG.paths:
        root = pathlib.Path(root)
        # iterate over the root dir and convert the resulting paths to relative paths:
        relative_paths = (p.relative_to(root)
                          if isinstance(p, pathlib.Path) else p
                          for p in _iter_single_dir(root))
        # convert everything to strings:
        relative_path_strings = (str(p) for p in relative_paths)
        # combine strings to lines:
        yield from make_lines(relative_path_strings)


def make_lines(path_strings: Iterable[str]) -> Iterable[str]:
    """
    Convert the pathlib.Path instances to formatted lines.

    :return:
    """
    if CONFIG.list_format:
        raise NotImplementedError("TODO")
    else:
        for p in path_strings:
            yield str(p)


def _iter_single_dir(path) -> Iterable[Union[str, pathlib.Path]]:
    if CONFIG.sort_by_size:
        yield from _iterate_dir_by_size(path)
    else:
        yield from _iterate_dir_alphabetically(path)


def _sort_key(path: pathlib.Path) -> str:
    # TODO: Not sure if calling .lower() is sufficient
    key = path.name.lower()
    if key[0] == '.':
        return key[1:]
    return key


def _iterate_dir_by_size(path: pathlib.Path) -> Iterable[Union[str, pathlib.Path]]:
    raise NotImplementedError("TODO")


def _iterate_dir_alphabetically(path: pathlib.Path) -> Iterable[Union[str, pathlib.Path]]:
    if CONFIG.show_all:
        yield "."
        yield ".."
    for p in sorted(path.iterdir(), key=_sort_key):
        if not CONFIG.show_all and p.name[0] == '.':
            continue
        yield p


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
    for line in ls_lines():
        print(line)


if __name__ == '__main__':
    main()
