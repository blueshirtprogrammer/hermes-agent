import json, re
from pathlib import Path
from collections import Counter, defaultdict

p=Path(r'C:\Users\Link Team\Desktop\hermes-agent-fork\.alpha-owl\issue_pr_sweep_latest.json')
d=json.loads(p.read_text(encoding='utf-8'))
issues=d['top_issues']
prs=d['top_prs']

# Show labels/areas in the current sweep for diagnostics.
print('COUNTS', d['counts'])
print('\nTOP ISSUE RAW LABELS')
for r in issues[:20]:
    print(f"#{r['number']} score={r['score']} area={r['area']} labels={r['labels']} title={r['title'][:90]}")
print('\nTOP PR RAW LABELS')
for r in prs[:20]:
    print(f"PR#{r['number']} score={r['score']} area={r['area']} labels={r['labels']} draft={r['draft']} title={r['title'][:90]}")
