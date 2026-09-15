"""Export original offline exercises. No research Store, model, or network access."""
import argparse
from pathlib import Path
import shutil

from tools.research_curricula import DIRECTORY, PATH_IDS, inspect_curriculum
from tools.research_evidence import ROOT, require


def export_practice(curriculum, output):
    path = inspect_curriculum(curriculum)
    target = Path(output).expanduser().absolute()
    require(not target.exists() and not target.is_symlink(), 'choose a new practice directory; existing work is never overwritten')
    require(not target.resolve().is_relative_to(ROOT.resolve()), 'keep your practice work outside the repository checkout')
    lesson = path['lessons'][0]
    source = DIRECTORY / 'practice' / curriculum
    files = {name: (source / name).read_text() for name in ('solution.py', 'test_solution.py', 'reference.py')}
    files['README.md'] = f'''# {path['title']}: first exercise

Curriculum revision: {path['revision']} · lesson: {lesson['id']}

{lesson['objective']}

## Work through the exercise

1. Open `solution.py` and read its function contract. All data is fictional.
2. Run `python3 -m unittest -v test_solution`. The starter deliberately raises
   `NotImplementedError`: failures are expected until you implement the function.
3. Read each test's input and expected result. Edit only `solution.py`, then rerun.
4. Add a case of your own and explain what it checks in `work-log.md`.
5. After your attempt, compare with `reference.py`. You can check that solution
   separately with `python3 -m unittest -v reference`.

Python 3.10+ and its standard library are sufficient. There are no packages,
accounts, model downloads or API calls. Commands above run from this directory.

## Understand the result

{lesson['explanation']}

{lesson.get('expected_result', lesson['completion_check'])}

Common mistake: {lesson.get('common_mistake', 'Passing these examples does not establish general correctness.')}

## Continue the full lesson

{lesson['exercise']}

Ready to move on: {lesson['completion_check']}

Reflection: {lesson.get('reflection', 'Which behavior did your new test establish?')}

This kit covers the first contract, not the whole curriculum. The remaining
lessons and resources are in the workspace report. These are original editorial
drafts; passing the sample tests does not establish AI accuracy or mastery.

## Keep a record

Use `work-log.md` for actual attempts, failures and results. Nothing is uploaded
or saved into research progress automatically. If you later select this curriculum
in your research workspace, use its Record this lesson action to review and save
your actual work through Codex. You can learn independently without that step.
'''
    files['work-log.md'] = f'''# My work — {lesson['title']}

- Date:
- What I tried:
- Exact command and observed output:
- Test I added and why:
- What failed or remains uncertain:
- What I can explain without the reference solution:
- Next step:

No completion is claimed by this template. Record only work you actually did.
'''
    target.parent.mkdir(parents=True, exist_ok=True)
    target.mkdir(mode=0o700)  # no exist_ok: a racing writer cannot be overwritten
    try:
        for name, content in files.items():
            with (target / name).open('x', encoding='utf-8') as handle:
                (target / name).chmod(0o600)
                handle.write(content)
    except Exception:
        shutil.rmtree(target)
        raise
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--curriculum', required=True, choices=PATH_IDS)
    parser.add_argument('--output', required=True, help='new directory outside this checkout')
    args = parser.parse_args()
    try:
        target = export_practice(args.curriculum, args.output)
    except (ValueError, OSError) as exc:
        parser.exit(2, str(exc) + '\n')
    print(f'Practice kit: {target}\nOpen README.md, then run python3 -m unittest -v test_solution there.\nInitial failures are expected; implement solution.py. No progress was recorded.')


if __name__ == '__main__':
    main()
