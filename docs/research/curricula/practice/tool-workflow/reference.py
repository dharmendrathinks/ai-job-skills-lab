"""Compare after attempting solution.py. This dispatcher never writes data."""
from solution import DOCUMENTS


def dispatch(call):
    if not isinstance(call, dict) or set(call) != {'name', 'arguments'}:
        raise ValueError('Expected name and arguments')
    if call['name'] != 'lookup':
        raise ValueError('Unknown tool')
    args = call['arguments']
    if not isinstance(args, dict) or set(args) != {'item_id'}:
        raise ValueError('Expected only item_id')
    item_id = args['item_id']
    if not isinstance(item_id, str) or item_id not in DOCUMENTS:
        raise ValueError('Unknown item')
    return {'id': item_id, 'text': DOCUMENTS[item_id]}


def load_tests(loader, tests, pattern):
    import test_solution
    test_solution.dispatch = dispatch
    return loader.loadTestsFromModule(test_solution)
