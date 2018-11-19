"""
The PATHS dictionary stores the dictionary structure and files
for the various test cases.
"""
PATHS = dict(
    empty=dict(dirs=[], files=[]),
    one_empty_child_dir=dict(
        dirs=["foo"],
    ),
    one_hidden_file=dict(
        files=[(".foo", 0)],
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
)
