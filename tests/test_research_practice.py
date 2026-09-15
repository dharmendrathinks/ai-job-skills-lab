"""Exercise the first-run learning loop against owned, offline starter kits."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from tools.research_curricula import library
from tools.research_evidence import Store
from tools.research_practice import export_practice


class PracticeTests(unittest.TestCase):
    def test_starters_fail_and_reference_solutions_pass_without_external_services(self):
        with tempfile.TemporaryDirectory() as temporary:
            for path in library()['paths']:
                with self.subTest(curriculum=path['id']):
                    target=Path(temporary)/path['id']
                    with patch('socket.socket',side_effect=AssertionError('network forbidden')), \
                         patch.object(Store,'transaction',side_effect=AssertionError('store forbidden')):
                        export_practice(path['id'],target)
                    original=(target/'solution.py').read_text()
                    def run(module):
                        return subprocess.run([sys.executable,'-m','unittest','-v',module],cwd=target,
                                              capture_output=True,text=True,timeout=20)
                    starter=run('test_solution')
                    self.assertNotEqual(starter.returncode,0)
                    self.assertIn('NotImplementedError',starter.stderr)
                    reference=run('reference')
                    self.assertEqual(reference.returncode,0,reference.stderr)
                    self.assertEqual((target/'solution.py').read_text(),original)
                    self.assertIn(path['revision'],(target/'README.md').read_text())
                    with self.assertRaises(ValueError):export_practice(path['id'],target)
                    self.assertEqual((target/'solution.py').read_text(),original)

    def test_standalone_examples_and_guidance(self):
        book=library()
        with tempfile.TemporaryDirectory() as temporary:
            for path in [book['foundations'],*book['paths']]:
                for lesson in path['lessons']:
                    with self.subTest(lesson=lesson['id']):
                        for name in ('expected_result','common_mistake','reflection'):
                            self.assertTrue(lesson[name])
                        script=Path(temporary)/'example.py';script.write_text(lesson['example'])
                        result=subprocess.run([sys.executable,str(script)],capture_output=True,text=True,timeout=20)
                        self.assertEqual(result.returncode,0,result.stderr)

    def test_kit_cannot_overwrite_checkout_or_follow_existing_output_symlink(self):
        from tools.research_evidence import ROOT
        with self.assertRaises(ValueError):export_practice('structured-output',ROOT/'practice-never-created')
        with tempfile.TemporaryDirectory() as temporary:
            root=Path(temporary);actual=root/'actual';actual.mkdir();link=root/'link';link.symlink_to(actual)
            with self.assertRaises(ValueError):export_practice('structured-output',link)
            self.assertEqual(list(actual.iterdir()),[])

    def test_cli_invalid_curriculum_exits_without_output_directory(self):
        with tempfile.TemporaryDirectory() as temporary:
            output=Path(temporary)/'invalid'
            result=subprocess.run([sys.executable,'-m','tools.research_practice','--curriculum','unknown',
                                   '--output',str(output)],capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,2)
            self.assertFalse(output.exists())

    def test_small_and_empty_samples_explain_their_denominator(self):
        from tools.research_learning_reports import introductions
        for denominator in (0, 3):
            html=introductions({'skills':{},'counts':{'in_domain_denominator':denominator,
                               'pending_or_legacy_openings':7}},library())
            self.assertIn('7 openings still lack detailed skill analysis',html)
            if denominator:
                self.assertIn('33.3 percentage points',html)
            else:
                self.assertIn('There are no analysed AI openings',html)
