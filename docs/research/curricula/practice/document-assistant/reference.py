"""Compare after attempting solution.py. Offsets apply to this exact revision."""


def chunks(document_id, text):
    if not isinstance(document_id, str) or not document_id or not isinstance(text, str):
        raise ValueError('Expected a document ID and text')
    rows, start = [], 0
    for part in text.split('\n\n'):
        end = start + len(part)
        if part.strip():
            rows.append({'id': f'{document_id}:{start}:{end}', 'document': document_id,
                         'text': part, 'start': start, 'end': end})
        start = end + 2
    return rows


def load_tests(loader, tests, pattern):
    import test_solution
    test_solution.chunks = chunks
    return loader.loadTestsFromModule(test_solution)
