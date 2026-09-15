import unittest
from solution import chunks


class CitationTests(unittest.TestCase):
    def test_offsets_and_identity(self):
        self.assertEqual(chunks('guide', 'One.\n\nTwo.'), [
            {'id': 'guide:0:4', 'document': 'guide', 'text': 'One.', 'start': 0, 'end': 4},
            {'id': 'guide:6:10', 'document': 'guide', 'text': 'Two.', 'start': 6, 'end': 10}])

    def test_empty_and_blank_chunks(self):
        self.assertEqual(chunks('guide', ''), [])
        rows = chunks('guide', '\n\n  \n\nOne.')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['start'], 6)

    def test_unicode_and_spacing_preserved(self):
        text = ' Café ☕ \n\nRetour en cinq jours.'
        for row in chunks('guide', text):
            self.assertEqual(text[row['start']:row['end']], row['text'])
        self.assertEqual(chunks('guide', text)[0]['text'], ' Café ☕ ')

    def test_repeated_text_keeps_distinct_locations(self):
        rows = chunks('guide', 'Same\n\nSame')
        self.assertNotEqual(rows[0]['id'], rows[1]['id'])
        self.assertEqual(rows[1]['start'], 6)

    def test_invalid_inputs(self):
        for doc, text in [('', 'One'), (None, 'One'), ('guide', None)]:
            with self.subTest(doc=doc), self.assertRaises(ValueError):
                chunks(doc, text)
