"""The onboarding example must work without a model or a real research store."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from tools.research_demo import generate_demo, NOTICE


class DemoTests(unittest.TestCase):
    def test_first_visit_has_no_selected_path_or_fictional_progress(self):
        with tempfile.TemporaryDirectory() as directory:
            paths=generate_demo(directory,started=False)
            html=Path(paths['workspace.html']).read_text()
            self.assertNotIn('ACTIVE LEARNING PATH',html)
            self.assertNotIn('Fictional example:',html)
            self.assertIn('id="first-visit" open',html)
            self.assertIn('No progress recorded yet',html)
            self.assertEqual(html.count('Start the first lesson →'),3)

    def test_offline_demo_has_connected_views_without_touching_existing_reports(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            existing = root / 'jobs.html'; existing.write_text('existing private report')
            with patch('socket.socket', side_effect=AssertionError('network forbidden')), \
                 patch('tools.research_evidence.Store.transaction', side_effect=AssertionError('store forbidden')), \
                 patch('tools.research_runtime.CodexWorker.__enter__', side_effect=AssertionError('model forbidden')):
                paths = generate_demo(root)
            self.assertEqual(existing.read_text(), 'existing private report')
            for name in ('jobs.html', 'workspace.html'):
                page = Path(paths[name])
                self.assertIn(NOTICE, page.read_text())
                self.assertEqual(page.stat().st_mode & 0o777, 0o600)
            html = Path(paths['workspace.html']).read_text()
            redirect=Path(paths['projects.html'])
            self.assertIn('window.location.replace',redirect.read_text())
            self.assertEqual(redirect.stat().st_mode & 0o777,0o600)
            for expected in ('tab-path', 'tab-skill', 'tab-project', 'tab-youtube', 'Python', 'held-out'):
                self.assertIn(expected, html)
            self.assertFalse(list(root.rglob('research-state.json')))
