#!/usr/bin/env python3
"""Build a ML-ready labeled sheet from the *combined_labeled* dataset (948,789 rows).

Inputs:
- ./training_data/crtsh_combined_labeled.csv.gz
- ./outputs/cert_labels.csv   (cert_sha1 -> label/score/reasons)

Output:
- ./outputs/ml/labeled_sheet.csv

Design:
- streaming, no pandas
- output features that are available in combined_labeled

Columns produced:
- cert_sha1, label
- common_name
- san_count
- issuer_dn
- signature_hash_algo, signature_key_algo
- public_key_algo, public_key_size
- not_before, not_after
- matched_domain (if present in reasons)
- reasons

NOTE:
- This is immediately usable in sklearn/xgboost/etc once you install libs.
"""

import csv
import gzip
import os
import re
from pathlib import Path

LABELS = Path('./outputs/cert_labels.csv')
DATA = Path('./training_data/crtsh_combined_labeled.csv.gz')
OUTDIR = Path('./outputs/ml')
OUT = OUTDIR / 'labeled_sheet.csv'


def parse_san_count(s: str) -> int:
    if not s:
        return 0
    s = s.strip()
    if s.startswith('{') and s.endswith('}'):
        s = s[1:-1]
    if not s.strip():
        return 0
    return len([p for p in s.split(',') if p.strip()])


def load_labels(path: Path):
    m = {}
    with path.open(newline='', encoding='utf-8', errors='replace') as f:
        r = csv.DictReader(f)
        for row in r:
            sha1 = (row.get('cert_sha1') or '').strip().lower()
            if not sha1:
                continue
            m[sha1] = {
                'label': row.get('label','unknown'),
                'score': row.get('score',''),
                'reasons': row.get('reasons',''),
            }
    return m


def matched_domain_from_reasons(reasons: str) -> str:
    if not reasons:
        return ''
    for part in reasons.split('|'):
        if part.startswith('domain_blocklist:'):
            return part.split(':',1)[1].strip().lower()
    return ''


def main():
    OUTDIR.mkdir(parents=True, exist_ok=True)

    labels = load_labels(LABELS)
    print('loaded labels', len(labels))

    fieldnames = [
        'cert_sha1','label','score',
        'common_name','san_count','issuer_dn',
        'signature_hash_algo','signature_key_algo',
        'public_key_algo','public_key_size',
        'not_before','not_after',
        'matched_domain','reasons'
    ]

    n = 0
    with gzip.open(DATA, 'rt', encoding='utf-8', errors='replace', newline='') as fin, \
         OUT.open('w', encoding='utf-8', newline='') as fout:
        dr = csv.DictReader(fin)
        dw = csv.DictWriter(fout, fieldnames=fieldnames)
        dw.writeheader()

        for row in dr:
            n += 1
            sha1 = (row.get('cert_sha1') or '').strip().lower()
            lab = labels.get(sha1, {'label':'unknown','score':'','reasons':''})
            reasons = lab.get('reasons','')
            dw.writerow({
                'cert_sha1': sha1,
                'label': lab.get('label','unknown'),
                'score': lab.get('score',''),
                'common_name': (row.get('common_name') or '').strip(),
                'san_count': parse_san_count(row.get('san') or ''),
                'issuer_dn': (row.get('issuer_dn') or '').strip(),
                'signature_hash_algo': (row.get('signature_hash_algo') or '').strip(),
                'signature_key_algo': (row.get('signature_key_algo') or '').strip(),
                'public_key_algo': (row.get('public_key_algo') or '').strip(),
                'public_key_size': (row.get('public_key_size') or '').strip(),
                'not_before': (row.get('not_before') or '').strip(),
                'not_after': (row.get('not_after') or '').strip(),
                'matched_domain': matched_domain_from_reasons(reasons),
                'reasons': reasons,
            })

            if n % 200000 == 0:
                print('processed', n)

    print('wrote', OUT)


if __name__ == '__main__':
    main()
