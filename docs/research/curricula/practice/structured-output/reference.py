"""Compare after attempting solution.py. This is only one possible solution."""


def validate_record(record):
    if not isinstance(record, dict) or set(record) != {'task', 'owner', 'source'}:
        raise ValueError('Expected exactly task, owner and source')
    for key in ('task', 'source'):
        if not isinstance(record[key], str) or not record[key].strip():
            raise ValueError(key + ' must be a nonblank string')
    owner = record['owner']
    if owner is not None and (not isinstance(owner, str) or not owner.strip()):
        raise ValueError('Owner must be unknown or a nonblank string')
    return record


def load_tests(loader, tests, pattern):
    import test_solution
    test_solution.validate_record = validate_record
    return loader.loadTestsFromModule(test_solution)
