"""Implement the record contract; run python3 -m unittest -v test_solution."""


def validate_record(record):
    """Return the original dict or raise ValueError.

    Exactly task, owner and source are required. task/source are nonblank strings.
    owner is either None or a nonblank string. Unknown fields are rejected.
    Do not insert defaults or change values. This validates structure, not whether
    the task is supported by the note; later lessons check that separately.
    """
    raise NotImplementedError('Implement the contract above')
