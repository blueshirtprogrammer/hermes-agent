import json, datetime, time, os, re, sys
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.parse import quote
from urllib.error import HTTPError
from collections import Counter

OWNER_REPO='NousResearch/hermes-agent'
OUT_DIR=Path(r'C:\Users\Link Team\Desktop\hermes-agent-fork\.alpha-owl')
OUT_DIR.mkdir(parents=True, exist_ok=True)

TOKEN=os.environ.get('GITHUB_TOKEN','').strip()
if not TOKEN or TOKEN in {'***','[REDACTED]'}:
    # One-shot secure-ish path: token piped on stdin, never saved to disk.
    if not sys.stdin.isatty():
        TOKEN=sys.stdin.readline().strip()
if not TOKEN or TOKEN in {'***','[REDACTED]'}:
    raise SystemExit('ERROR: valid GitHub token not available via env or stdin')

headers={'Authorization':f'Bearer {TOKEN}','Accept':'application/vnd.github.v3+json','User-Agent':'hermes-alpha-owl/1.0'}

def api(path):
    url='https://api.github.com/'+path
    req=Request(url,headers=headers)
    try:
        with urlopen(req,timeout=30) as r:
            return json.loads(r.read())
    except HTTPError as e:
        body=e.read().decode('utf-8','replace')[:500]
        raise RuntimeError(f'GitHub API {e.code} for {path}: {body}')

def pages(path, max_pages=20):
    out=[]
    sep='&' if '?' in path else '?'
    for page in range(1,max_pages+1):
        batch=api(f'{path}{sep}per_page=100&page={page}')
        if not batch:
            break
        out.extend(batch)
        if len(batch)<100:
            break
        time.sleep(0.15)
    return out

def search(q, max_pages=5):
    items=[]
    for page in range(1,max_pages+1):
        data=api('search/issues?q='+quote(q)+f'&per_page=100&page={page}')
        batch=data.get('items',[])
        items.extend(batch)
        if len(batch)<100:
            break
        time.sleep(0.3)
    return items

BUG_WORDS='bug error crash exception traceback fail broken regression hang timeout cannot unable invalid corrupt leak auth permission denied rate limit'.split()
FEATURE_WORDS='feat feature request support add implement enable integration connector provider option setting'.split()
DESKTOP_WORDS='desktop electron gui ui app windows mac tray notification updater dock menu webview'.split()
SEC_WORDS='security vuln cve xss injection ssrf csrf token secret credential auth permission sandbox path traversal'.split()

def label_names(x):
    return [l['name'] for l in x.get('labels',[])]

def text(x):
    return ((x.get('title') or '')+' '+(x.get('body') or '')).lower()

def anyword(t, words):
    return any(w in t for w in words)

def is_bug(x):
    labs=' '.join(label_names(x)).lower(); t=text(x)
    return 'bug' in labs or anyword(t, BUG_WORDS)

def is_feature(x):
    labs=' '.join(label_names(x)).lower(); t=text(x)
    return any(k in labs for k in ['feature','enhancement']) or anyword(t, FEATURE_WORDS)

def is_desktop(x):
    labs=' '.join(label_names(x)).lower(); t=text(x)
    return 'desktop' in labs or anyword(t, DESKTOP_WORDS) or '[desktop]' in t

def is_security(x):
    labs=' '.join(label_names(x)).lower(); t=text(x)
    return any(k in labs for k in ['security','vulnerability']) or anyword(t, SEC_WORDS)

def area(x):
    labs=' '.join(label_names(x)).lower(); t=text(x)
    for a in ['desktop','gateway','agent','tools','cron','profile','memory','session','config','terminal','model','provider','auth','billing','telegram','discord','whatsapp','teams','mcp','browser','voice','tts','stt']:
        if a in labs or a in t:
            return a
    return 'unknown'

def score_issue(x):
    s=0; t=text(x); labs=' '.join(label_names(x)).lower()
    if is_security(x): s+=100
    if is_bug(x): s+=55
    if is_desktop(x): s+=35
    if any(k in labs for k in ['p0','critical','severity:critical']): s+=80
    if any(k in labs for k in ['p1','high','priority:high']): s+=45
    if anyword(t, ['crash','data loss','secret','credential','login','auth','rate limit','windows']): s+=25
    if area(x) in ['agent','gateway','tools','desktop','auth','config','terminal']: s+=20
    s+=min(x.get('comments',0)*2,20)
    return s

def score_pr(p):
    s=0; t=text(p); labs=' '.join(label_names(p)).lower()
    if is_desktop(p): s+=40
    if anyword(t, BUG_WORDS): s+=35
    if anyword(t, FEATURE_WORDS): s+=25
    if is_security(p): s+=80
    if p.get('draft'): s-=15
    s+=min(p.get('comments',0)*2,20)
    return s

print('Checking rate limit...')
rl=api('rate_limit')['resources']['core']
print(f"Rate limit before: {rl['remaining']}/{rl['limit']}")

print('Fetching open issues/PRs...')
issue_items=pages(f'repos/{OWNER_REPO}/issues?state=open&sort=updated&direction=desc', max_pages=30)
issues=[i for i in issue_items if 'pull_request' not in i]
issue_pr_refs=[i for i in issue_items if 'pull_request' in i]
prs=pages(f'repos/{OWNER_REPO}/pulls?state=open&sort=updated&direction=desc', max_pages=20)
labels=api(f'repos/{OWNER_REPO}/labels?per_page=100')

print('Running targeted desktop searches...')
desktop_open_pr_search=search(f'repo:{OWNER_REPO} is:pr is:open [desktop]', max_pages=3)
desktop_open_issue_search=search(f'repo:{OWNER_REPO} is:issue is:open desktop', max_pages=5)

issue_rows=[]
for i in issues:
    issue_rows.append({
        'number':i['number'], 'title':i['title'], 'url':i['html_url'], 'labels':label_names(i),
        'created_at':i['created_at'], 'updated_at':i['updated_at'], 'comments':i['comments'],
        'area':area(i), 'score':score_issue(i), 'is_bug':is_bug(i), 'is_feature':is_feature(i),
        'is_desktop':is_desktop(i), 'is_security':is_security(i),
        'body_excerpt':(i.get('body') or '')[:1000]
    })
issue_rows.sort(key=lambda x:x['score'], reverse=True)

pr_rows=[]
for p in prs:
    pr_rows.append({
        'number':p['number'], 'title':p['title'], 'url':p['html_url'], 'labels':label_names(p),
        'draft':p.get('draft'), 'created_at':p['created_at'], 'updated_at':p['updated_at'],
        'user':p['user']['login'], 'head':p['head']['ref'], 'base':p['base']['ref'],
        'area':area(p), 'score':score_pr(p), 'is_desktop':is_desktop(p),
        'body_excerpt':(p.get('body') or '')[:1000]
    })
pr_rows.sort(key=lambda x:x['score'], reverse=True)

summary={
    'generated_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),
    'rate_limit_before':rl,
    'counts':{
        'open_issue_items_total':len(issue_items), 'open_issues':len(issues), 'open_issue_pr_refs':len(issue_pr_refs),
        'open_prs':len(prs), 'bugs':sum(r['is_bug'] for r in issue_rows),
        'features':sum(r['is_feature'] for r in issue_rows), 'desktop_issues':sum(r['is_desktop'] for r in issue_rows),
        'security_issues':sum(r['is_security'] for r in issue_rows),
        'desktop_pr_search':len(desktop_open_pr_search), 'desktop_issue_search':len(desktop_open_issue_search),
    },
    'area_counts':Counter(r['area'] for r in issue_rows).most_common(),
    'pr_area_counts':Counter(r['area'] for r in pr_rows).most_common(),
    'top_issues':issue_rows[:50],
    'top_prs':pr_rows[:50],
    'desktop_pr_search':[{'number':x['number'],'title':x['title'],'url':x['html_url'],'labels':label_names(x)} for x in desktop_open_pr_search[:100]],
    'desktop_issue_search':[{'number':x['number'],'title':x['title'],'url':x['html_url'],'labels':label_names(x)} for x in desktop_open_issue_search[:100]],
}

stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
json_path=OUT_DIR/f'issue_pr_sweep_{stamp}.json'
md_path=OUT_DIR/f'issue_pr_sweep_{stamp}.md'
latest_json=OUT_DIR/'issue_pr_sweep_latest.json'
latest_md=OUT_DIR/'issue_pr_sweep_latest.md'
json_text=json.dumps(summary, indent=2)
json_path.write_text(json_text, encoding='utf-8')
latest_json.write_text(json_text, encoding='utf-8')

lines=[]
lines.append('# Hermes Agent Issue/PR Sweep')
lines.append(f"Generated: {summary['generated_at']}")
lines.append('')
lines.append('## Counts')
for k,v in summary['counts'].items():
    lines.append(f'- {k}: {v}')
lines.append('')
lines.append('## Top issue areas')
for a,c in summary['area_counts'][:20]:
    lines.append(f'- {a}: {c}')
lines.append('')
lines.append('## Top priority issues')
for r in issue_rows[:25]:
    flags=[]
    if r['is_security']: flags.append('security')
    if r['is_bug']: flags.append('bug')
    if r['is_desktop']: flags.append('desktop')
    if r['is_feature']: flags.append('feature')
    lines.append(f"- score {r['score']:3} #{r['number']} [{r['area']}] ({', '.join(flags)}) {r['title']} — {r['url']}")
lines.append('')
lines.append('## Top priority PRs')
for r in pr_rows[:25]:
    flags=[]
    if r['is_desktop']: flags.append('desktop')
    if r['draft']: flags.append('draft')
    lines.append(f"- score {r['score']:3} PR #{r['number']} [{r['area']}] ({', '.join(flags)}) {r['title']} — {r['url']}")
md='\n'.join(lines)
md_path.write_text(md, encoding='utf-8')
latest_md.write_text(md, encoding='utf-8')

rl2=api('rate_limit')['resources']['core']
print(f"Fetched {len(issues)} issues and {len(prs)} PRs")
print(f"Counts: {summary['counts']}")
print(f"Wrote JSON: {json_path}")
print(f"Wrote MD: {md_path}")
print(f"Rate limit after: {rl2['remaining']}/{rl2['limit']}")
