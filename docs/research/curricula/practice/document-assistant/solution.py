"""Implement the chunker; run python3 -m unittest -v test_solution."""


def chunks(document_id, text):
    """Split on exactly two newlines; return dicts with id, document, text, start, end.

    Use IDs '<document_id>:<start>:<end>' with Python string offsets, end exclusive.
    Skip empty or whitespace-only chunks; retain other text exactly (no strip).
    Advance offsets even across skipped chunks. Empty text returns [].
    document_id must be a nonempty string and text must be a string, else ValueError.
    IDs locate passages in this exact document revision, not future edited versions.
    """
    raise NotImplementedError('Implement the contract above')
