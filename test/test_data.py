# The PATHS dictionary defines the directory structure and files for various test cases.
PATHS = dict(
    empty=dict(dirs=[], files=[]),
    one_empty_child_dir=dict(
        dirs=["foo"],
    ),
    one_nonempty_child_dir=dict(
        dirs=["foo"],
        files=[("foo/01.txt", 0)],
    ),
    one_hidden_file=dict(
        files=[(".foo", 0)],
    ),
    symlink=dict(
        dirs=["foo"],
        symlinks=[("link", "foo")],
    ),
    symlink_to_file=dict(
        dirs=["foo"],
        files=[("foo/a", 0)],
        symlinks=[("link", "foo/a")],
    ),
    symlink_to_nested_subdir=dict(
        dirs=[
            "foo",
            "foo/bar",
        ],
        symlinks=[("link", "foo/bar")],
    ),
    symlink_to_sibling_dir=dict(
        dirs=[
            "foo/bar1",
            "foo/bar2",
        ],
        symlinks=[("foo/bar1/link", "foo/bar2")],
    ),
    one_hidden_one_visible_file=dict(
        # the leading dot should be ignored in the alphabetical ordering.
        files=[
            (".foo", 0),
            ("bar", 0),
        ],
    ),
    one_hidden_one_visible_file_reverse_order=dict(
        # the leading dot should be ignored in the alphabetical ordering.
        files=[
            ("foo", 0),
            (".bar", 0),
        ],
    ),
    size_order_different_from_alphabetical=dict(
        files=[
            ("a.txt", 2),
            ("b.txt", 3),
            ("c.txt", 1),
        ],
    ),
    mixed_upper_lower_case_files=dict(
        files=[
            ("a1.txt", 0),
            ("A2.txt", 0),
            ("B1.txt", 0),
            ("b2.txt", 0),
        ],
    ),
    filenames_with_whitespace=dict(
        files=[("important document.txt", 1)],
    ),
    two_empty_dirs=dict(
        dirs=[
            "foo",
            "bar",
        ],
    ),
    many_files=dict(
        files=[(f"{i:02d}.txt", i) for i in range(13)],
    ),
    many_files_long_name=dict(
        files=[(f"abcdefghijklmnopqrstuvwxyz_{i:02d}.txt", i) for i in range(13)],
    ),
    multiple_files_in_nested_directories=dict(
        dirs=[
            "foo01",
            "foo02",
            "foo01/bar01",
            "foo01/bar02",
            "foo02/bar01",
            "foo02/bar02",
        ],
        files=[
            ("foo01/bar01/a.txt", 0),
            ("foo01/bar01/b.txt", 0),
            ("foo01/bar01/c.txt", 0),
            ("foo01/bar02/a.txt", 0),
            ("foo01/bar02/b.txt", 0),
            ("foo01/bar02/c.txt", 0),
            ("foo02/bar01/a.txt", 0),
            ("foo02/bar01/b.txt", 0),
            ("foo02/bar01/c.txt", 0),
            ("foo02/bar02/a.txt", 0),
            ("foo02/bar02/b.txt", 0),
            ("foo02/bar02/c.txt", 0),
        ],
    ),
    file_names_starting_with_symbols=dict(
        files=[
            # the correct order for these seems to be:
            #   1. File names with alphanumeric characters are sorted as though the alphanumerics
            ("a1", 0),
            ("_a2", 0),
            ("a_2", 0),
            ("......", 0),
            ("..a3", 0),
            ("a3", 0),
            ("a_3", 0),
            ("__a4", 0),
            # repeat with dot prefix to check that they are sorted correctly with the -a option
            (".a1", 0),
            ("._a2", 0),
            (".......", 0),
            ("...a3", 0),
            (".a3", 0),
            (".a_3", 0),
            (".__a4", 0),
        ],
    ),
)
