"""Generate dependency-free profile artwork from an authenticated GitHub snapshot."""
from pathlib import Path
from html import escape as esc
import json, os, urllib.request, time, re
ROOT=Path(__file__).resolve().parents[1]
A=ROOT/'assets'
USER='becko1602'
def api(path, payload=None):
    token=os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    headers={'Accept':'application/vnd.github+json','User-Agent':'BECKO-profile'}
    if token: headers['Authorization']='Bearer '+token
    data=json.dumps(payload).encode() if payload else None
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request('https://api.github.com/'+path,data=data,headers=headers),timeout=30) as r: return json.load(r)
        except Exception:
            if attempt==2: raise
            time.sleep(2**attempt)
def snapshot():
    repos=[]
    for page in range(1,20):
        batch=api(f'users/{USER}/repos?per_page=100&page={page}')
        repos.extend(batch)
        if len(batch)<100: break
    query='query { user(login:"becko1602") { contributionsCollection { totalCommitContributions contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } } } } }'
    result=api('graphql',{'query':query})
    if result.get('errors'): raise RuntimeError(result['errors'])
    collection=result['data']['user']['contributionsCollection']
    langs={}
    for repo in repos:
        if not repo['fork']:
            for k,v in api(f"repos/{USER}/{repo['name']}/languages").items(): langs[k]=langs.get(k,0)+v
    from datetime import datetime, timezone
    data={'updated':datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC'),'repos':len(repos),'languages':langs,'collection':collection}
    (ROOT/'data').mkdir(exist_ok=True)
    (ROOT/'data/activity.json').write_text(json.dumps(data,indent=2)+'\n')
    return data
from design import generate
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--offline',action='store_true');args=parser.parse_args()
    # Failed refresh exits without replacing the previous good data or artwork.
    data=json.loads((ROOT/'data/activity.json').read_text()) if args.offline else snapshot()
    generate(data)
