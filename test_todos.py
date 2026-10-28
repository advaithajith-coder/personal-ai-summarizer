import tempfile
import unittest
from pathlib import Path
import todos


class TodoTests(unittest.TestCase):
    def setUp(self):
        (Path(__file__).parent / 'data').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=Path(__file__).parent / 'data')
        self.original = todos.DB
        todos.DB = Path(self.temp.name) / 'todos.sqlite3'

    def tearDown(self):
        todos.DB = self.original
        self.temp.cleanup()

    def test_deduplication_preserves_completed_tasks(self):
        todos.add('Send the report', 'Jamie', 'Friday')
        first = todos.list_all()[0]
        todos.set_done(first['id'], True)
        todos.add('Send the report!', 'Jamie', 'Friday')
        items = todos.list_all()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['done'], 1)
        todos.add('Review the proposal')
        self.assertEqual(len(todos.list_all()), 2)
        todos.set_done(first['id'], False)
        self.assertTrue(all(not t['done'] for t in todos.list_all()))

    def test_only_tasks_with_source_evidence_are_imported(self):
        todos.import_tasks([
            {'task': 'Send report', 'owner': 'Jamie', 'deadline': 'Friday', 'evidence': 'I will send the report on Friday.'},
            {'task': 'Invented task', 'evidence': 'This was never said.'},
        ], 'Jamie: I will send the report on Friday.', 'meeting-id')
        items = todos.list_all()
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['source_id'], 'meeting-id')
        self.assertEqual(items[0]['owner'], 'Jamie')


if __name__ == '__main__':
    unittest.main()
