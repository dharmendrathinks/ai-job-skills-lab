import unittest
from solution import validate_record


class ContractTests(unittest.TestCase):
    def test_unknown_owner_is_preserved(self):
        row = {'task': 'Review guide', 'owner': None, 'source': 'Please review guide.'}
        self.assertIs(validate_record(row), row)
        self.assertIsNone(row['owner'])

    def test_named_owner(self):
        row = {'task': 'Review guide', 'owner': 'Alex', 'source': 'Alex: review guide.'}
        self.assertEqual(validate_record(row), row)

    def test_missing_field(self):
        with self.assertRaises(ValueError):
            validate_record({'task': 'Review guide', 'source': 'Review guide.'})

    def test_invalid_types_and_blank_values(self):
        valid = {'task': 'Review guide', 'owner': None, 'source': 'Review guide.'}
        for key, value in [('task', 7), ('source', ' '), ('owner', []), ('owner', '')]:
            with self.subTest(key=key, value=value), self.assertRaises(ValueError):
                validate_record({**valid, key: value})

    def test_unknown_fields(self):
        with self.assertRaises(ValueError):
            validate_record({'task': 'Review', 'owner': None, 'source': 'Review', 'extra': True})

    def test_non_object(self):
        with self.assertRaises(ValueError):
            validate_record(['Review guide'])
