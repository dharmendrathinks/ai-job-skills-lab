"""Score explicit held-out skill labels; never manufacture human review."""
import argparse
import json
import os

from tools.research_evidence import Store, ROOT, private_state_path, read_input, fields, require, text, digest
from tools.research_skills import KINDS, MODALITIES
from tools.research_outcomes import artifact


def evaluate(store, labels):
    fields(labels, ['schema_version', 'dataset_revision', 'label_basis', 'reviewer', 'examples'])
    require(labels['schema_version'] == 1 and labels['label_basis'] in ('provisional', 'human-reviewed'), 'unsupported labels')
    text(labels['reviewer']); text(labels['dataset_revision'])
    require(isinstance(labels['examples'], list) and 1 <= len(labels['examples']) <= 100, 'bounded evaluation required')
    with store.transaction() as state:
        rows = []; deps = []; seen = set()
        for example in labels['examples']:
            fields(example, ['analysis', 'split', 'expected'])
            require(example['analysis'] not in seen and example['split'] == 'held-out', 'one held-out row per analysis')
            seen.add(example['analysis'])
            a = artifact(state, example['analysis'], ('analysis',))
            require(a['schema_version'] == 2, 'evaluation requires detailed analysis')
            o = artifact(state, a['observation'], ('observation',))
            require(isinstance(example['expected'], list) and len(example['expected']) <= 150, 'label budget')
            expected = set()
            for label in example['expected']:
                fields(label, ['surface', 'kind', 'modality'])
                text(label['surface'], 180)
                require(o['description'] and label['surface'] in o['description'] and label['kind'] in KINDS and label['modality'] in MODALITIES,
                        'gold label must identify exact source wording and valid type')
                expected.add((label['surface'], label['kind'], label['modality']))
            actual = {(m['surface'],m['kind'],m['modality']) for m in a['skill_mentions']}
            rows.append({'analysis':example['analysis'], 'true_positive':len(actual & expected),
                         'false_positive':len(actual-expected), 'false_negative':len(expected-actual),
                         'extra':sorted(actual-expected), 'missing':sorted(expected-actual)})
            deps.append(example['analysis'])
        tp,fp,fn = [sum(r[k] for r in rows) for k in ('true_positive','false_positive','false_negative')]
        precision = tp/(tp+fp) if tp+fp else None; recall = tp/(tp+fn) if tp+fn else None
        payload = {'schema_version':1,'dataset_revision':labels['dataset_revision'],'labels_digest':digest(labels),
                   'label_basis':labels['label_basis'],'reviewer':labels['reviewer'],'examples':rows,
                   'precision':precision,'recall':recall,'targets':{'precision':0.95,'recall':0.85},
                   'acceptance':'requires-human-review' if labels['label_basis'] != 'human-reviewed' else
                       ('targets-met-on-this-set' if precision is not None and recall is not None and precision >= .95 and recall >= .85 else 'below-target'),
                   'limitations':['Strict surface/type/modality matching; synonym-normalization needs separate review.',
                                  'Exact source-span validation is not semantic accuracy or broad model quality.',
                                  'Reviewer and held-out labels are operator assertions; retain how and when labels were frozen.']}
        key=store.put(state,'skill-evaluation',payload,deps)
        return {'evaluation':key,**payload}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',required=True);args=parser.parse_args()
    try:
        result=evaluate(Store(private_state_path(ROOT,dict(os.environ))),read_input(args.input))
        print(json.dumps(result,ensure_ascii=True,indent=2));return 0
    except (ValueError,KeyError,TypeError,OSError):
        print(json.dumps({'status':'blocked','reason':'Check retained analyses and explicit held-out labels.'}));return 1


if __name__ == '__main__':raise SystemExit(main())
