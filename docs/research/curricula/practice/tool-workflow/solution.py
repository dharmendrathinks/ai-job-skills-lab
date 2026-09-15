"""Implement the dispatch boundary; run python3 -m unittest -v test_solution."""

DOCUMENTS = {'guide': 'Owned setup guide', 'faq': 'Owned common questions'}


def dispatch(call):
    """Return {'id': item_id, 'text': DOCUMENTS[item_id]} or raise ValueError.

    call must be a dict with exactly 'name' and 'arguments'. Only name='lookup'
    is declared. arguments must be a dict with exactly 'item_id': a string present
    in DOCUMENTS. Reject all other shapes, names and IDs. Never execute arbitrary
    functions from input or evaluate source text. The tool is read-only.
    """
    raise NotImplementedError('Implement the contract above')
