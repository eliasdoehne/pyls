"""
The PATHS dictionary stores the dictionary structure and files
for the various test cases.
"""
PATHS = dict(
    empty=dict(dirs=[], files=[]),
    one_empty_child_dir=dict(
        dirs=[
            "foo",
        ],
        files=[],
    ),
    size_order_different_from_alphabetical=dict(
        dirs=[
            "foo",
        ],
        files=[
            ("foo/01.txt", 2),
            ("foo/02.txt", 3),
            ("foo/03.txt", 1),
        ],
    ),
    two_empty_dirs=dict(
        dirs=[
            "foo",
            "bar",
        ],
        files=[],
    ),
)
