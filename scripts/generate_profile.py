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
STYLE='text{font-family:Arial,Helvetica,sans-serif;fill:#F8FAFC} .mono{font-family:monospace;fill:#94A3B8} .red{fill:#FF1744} .blue{fill:#00BFFF} .muted{fill:#94A3B8} @keyframes pulse{0%,100%{opacity:.55}50%{opacity:1}} @keyframes energy{to{stroke-dashoffset:-160}} @keyframes reveal{0%,8%{opacity:.08}35%,75%{opacity:1}82%{opacity:.7}88%{opacity:1}100%{opacity:.08}} @keyframes trace{0%,28%{stroke-dashoffset:1;opacity:0}32%{opacity:1}76%,90%{stroke-dashoffset:0;opacity:1}100%{stroke-dashoffset:0;opacity:0}} @keyframes consume{0%,20%{opacity:1}26%,100%{opacity:0}} @keyframes snake{0%{offset-distance:0%;opacity:0}5%{opacity:1}87%{opacity:1}95%,100%{offset-distance:100%;opacity:0}} @keyframes type{0%,8%{opacity:0}12%,80%{opacity:1}100%{opacity:0}} @media(prefers-reduced-motion:reduce){*{animation:none!important;offset-distance:100%}.trail{stroke-dashoffset:0!important;opacity:1!important}}'
def t(x,y,s,size=20,cls='',extra=''): return f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" {extra}>{esc(str(s))}</text>'
def panel(x,y,w,h): return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#0B1020" stroke="#202A3C"/>'
def save(name,h,body,title,desc=None):
    start=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 {h}" role="img"><title>{esc(title)}</title><desc>{esc(desc or title)}</desc>'
    defs='<defs><linearGradient id="rgb"><stop stop-color="#FF1744"/><stop offset=".65" stop-color="#00BFFF"/><stop offset="1" stop-color="#8B5CF6"/></linearGradient><radialGradient id="glow"><stop stop-color="#B90027" stop-opacity=".22"/><stop offset="1" stop-color="#050507" stop-opacity="0"/></radialGradient></defs>'
    content=defs+f'<style>{STYLE}</style><rect width="1200" height="{h}" rx="20" fill="#050507"/><rect x="1" y="1" width="1198" height="{h-2}" rx="20" fill="none" stroke="url(#rgb)" stroke-opacity=".5"/>'+body
    (A/f'{name}.svg').write_text(start+content+'</svg>')
    static=re.sub(r'<style>.*?</style>','<style>text{font-family:Arial,Helvetica,sans-serif;fill:#F8FAFC}.mono{font-family:monospace;fill:#94A3B8}.red{fill:#FF1744}.blue{fill:#00BFFF}.muted{fill:#94A3B8}</style>',content,flags=re.S)
    static=re.sub(r'<style>.*?</style>', '', static, flags=re.S)
    static='<style>text{font-family:Arial,Helvetica,sans-serif;fill:#F8FAFC}.mono{font-family:monospace;fill:#94A3B8}.red{fill:#FF1744}.blue{fill:#00BFFF}.muted{fill:#94A3B8}</style>'+static
    static=re.sub(r' style="[^"]*"','',static)
    (A/f'{name}-static.svg').write_text(start+static+'</svg>')
FONT={'B':['11110','10001','10001','11110','10001','10001','11110'],'E':['11111','10000','10000','11110','10000','10000','11111'],'C':['01111','10000','10000','10000','10000','10000','01111'],'K':['10001','10010','10100','11000','10100','10010','10001'],'O':['01110','10001','10001','10001','10001','10001','01110']}
PATH='M 0 0 L 0 -50 L 25 -50 Q 45 -50 45 -37 Q 45 -25 25 -25 L 0 -25 L 28 -25 Q 48 -25 48 -12 Q 48 0 28 0 Z M 72 0 L 72 -50 L 115 -50 M 72 -25 L 108 -25 M 72 0 L 115 0 M 185 -45 Q 140 -68 140 -25 Q 140 15 185 -5 M 210 0 L 210 -50 M 210 -25 L 250 -50 M 210 -25 L 250 0 M 280 -25 Q 280 -50 303 -50 Q 326 -50 326 -25 Q 326 0 303 0 Q 280 0 280 -25'
def snake_art(x,y,scale=1):
    # One continuous travel route reaches the apple, then follows the BECKO strokes.
    route='M 390 -75 L 0 -75 L 0 0 '+PATH[6:]
    return f'<g transform="translate({x} {y}) scale({scale})"><path d="{PATH}" fill="none" stroke="#172034" stroke-width="7"/><path class="trail" d="{PATH}" pathLength="1" fill="none" stroke="url(#rgb)" stroke-width="5" stroke-linecap="round" style="stroke-dasharray:1;stroke-dashoffset:0;animation:trace 14s linear infinite"/><g style="animation:consume 14s linear infinite"><path d="M -8 -77 Q -12 -91 0 -87 Q 14 -92 10 -78 Q 6 -63 0 -68 Q -6 -63 -8 -77" fill="#FF1744"/><path d="M 0 -88 Q 2 -98 10 -96" fill="none" stroke="#00BFFF" stroke-width="3"/></g><g style="offset-path:path(\'{route}\');offset-rotate:auto;animation:snake 14s linear infinite"><rect x="-22" y="-5" width="29" height="10" rx="5" fill="#FF1744"/><circle cx="5" cy="0" r="6" fill="#00BFFF"/><circle cx="7" cy="-2" r="1.5" fill="#050507"/></g></g>'
def generate(d):
    A.mkdir(exist_ok=True)
    c=d['collection']; cal=c['contributionCalendar']; days=[day for week in cal['weeks'] for day in week['contributionDays']]
    hero='<ellipse cx="190" cy="200" rx="520" ry="330" fill="url(#glow)"/>'
    for y in [66,298,330]: hero+=f'<path d="M 700 {y} H 790 l 35 -24 H 1160" fill="none" stroke="#00BFFF" opacity=".2"/>'
    hero+='<path d="M 32 345 H 730 L 770 315 H 1160" fill="none" stroke="url(#rgb)" stroke-dasharray="12 68" style="animation:energy 10s linear infinite"/>'
    hero+=t(38,42,'BECKO.DEV  /  DIGITAL IDENTITY',16,'mono')+t(38,112,'BEHRUZBEK',48,extra='font-weight="800" letter-spacing="2"')+t(38,169,'BEKCHANOV',48,extra='font-weight="800" letter-spacing="2"')+t(38,211,'FULL-STACK DEVELOPER',22,'red', 'letter-spacing="3"')+t(38,251,'From Uzbekistan. Building ambitious ideas',19,'muted')+t(38,278,'into real-world products.',19,'muted')
    hero+='<circle cx="44" cy="315" r="4" fill="#FF1744" style="animation:pulse 4s infinite"/>'+t(58,320,'BECKO SYSTEM ONLINE',13,'mono')+t(810,110,'01 / SIGNAL IN MOTION',13,'mono')+snake_art(795,240,.95)+t(810,290,'DEVELOPER. BUILDER. INNOVATOR.',12,'mono')
    save('hero',365,hero,'Behruzbek Bekchanov — Full-Stack Developer','Uzbekistan. Animated circuits and a decorative snake that eats an apple and traces BECKO on the right.')
    roles=['Full-Stack Developer','AI & Automation Builder','Linux Enthusiast','Hackathon Participant','Future Computer Engineer','Aspiring KAIST Student']
    body=t(32,45,'$ becko --identity',18,'red')
    # Discrete opacity windows keep exactly one role visible.
    for i,role in enumerate(roles):
        lo=i*100/6; hi=(i+1)*100/6
        body+=f'<style>@keyframes role{i}{{0%,100%{{opacity:0}}{lo+.01:.3f}%,{hi-.01:.3f}%{{opacity:1}}}}</style>'+t(340,45,role,21,extra=f'style="opacity:{1 if i==0 else 0};animation:role{i} 24s linear infinite"')
    save('roles',78,body,'Developer · AI builder · Linux enthusiast · Hackathons · Computer engineering · KAIST ambition')
    # Static roles use a single readable line.
    save('identity',90,t(32,40,'FULL-STACK / AI / LINUX',24)+t(32,68,'Hackathon participant · Future Computer Engineer · Aspiring KAIST student',17,'muted'),'Identity and ambitions')
    (A/'roles-static.svg').write_text((A/'identity-static.svg').read_text())
    body=t(34,38,'02 / CONTRIBUTION-POWERED IDENTITY',14,'mono')
    peak=max([day['contributionCount'] for day in days]+[1]); index=0
    for li,ch in enumerate('BECKO'):
        for row,line in enumerate(FONT[ch]):
            for col,on in enumerate(line):
                if on=='0': continue
                sample=days[-90:]; day=sample[index%len(sample)]; intensity=day['contributionCount']/peak
                color='#00BFFF' if intensity>.5 else '#FF1744'
                body+=f'<rect x="{72+li*218+col*33}" y="{76+row*30}" width="27" height="24" rx="4" fill="{color}" fill-opacity="{.32+.68*intensity:.3f}" style="animation:reveal 14s ease-in-out infinite;animation-delay:-{index%28*.15:.2f}s"><title>{day["date"]}: {day["contributionCount"]} contributions (sampled for artistic intensity)</title></rect>'
                index+=1
    body+=t(34,320,'ARTISTIC LETTERFORM / brightness samples real daily activity; not a calendar.',15,'mono')
    save('becko-neon',348,body,'BECKO built from contribution squares','Square brightness comes from real GitHub daily contribution counts. Decorative letter layout, not statistical positioning.')
    body=panel(24,24,1152,312)+t(48,58,'becko@arch ~ / terminal',16,'mono')
    commands=[('whoami','Behruzbek Bekchanov / Uzbekistan'),('cat interests.txt','Full-stack · AI · Cybersecurity · Computer Engineering'),('ls ~/projects','eDoska/  Becko/  becko-arch-linux/'),('echo $MISSION','Build impactful products and opportunities in Uzbekistan.'),('neofetch','Arch Linux / Hyprland / terminal-driven workflow')]
    for i,(cmd,out) in enumerate(commands):
        body+=f'<style>@keyframes cmd{i}{{0%{{clip-path:inset(0 100% 0 0)}}{8+i*8}%{{clip-path:inset(0 0 0 0)}}100%{{clip-path:inset(0 0 0 0)}}}}</style><g style="animation:cmd{i} 18s steps(24,end) infinite">'+t(48,96+i*46,'❯ '+cmd,17,'red')+t(70,117+i*46,out,17,'muted')+'</g>'
    body+='<rect x="1040" y="294" width="10" height="20" fill="#FF1744" style="animation:pulse 3s infinite"/>'
    save('terminal',360,body,'Arch Linux terminal introduction')
    cats=[('FRONTEND',['React / Next.js','JavaScript / TypeScript','HTML5 / CSS3 / Tailwind']),('BACKEND',['Node.js / Python','FastAPI / REST APIs','Project-based exploration']),('SYSTEMS & TOOLS',['Arch Linux / Hyprland','Git / GitHub / VS Code','Terminal / Docker¹']),('AI & AUTOMATION',['LLM integrations','Telegram bots / workflows','Voice AI assistants'])]
    body=t(32,38,'03 / DEVELOPMENT TOOLKIT',14,'mono')
    for i,(name,lines) in enumerate(cats):
        x=24+(i%2)*580;y=62+(i//2)*162
        body+=panel(x,y,568,146)+t(x+24,y+33,name,19,'red')
        for j,line in enumerate(lines):body+=t(x+24,y+66+j*28,line,19,'muted')
    save('tech-stack',410,body,'Development toolkit','Technologies used or explored in public and local projects. Docker is evidenced by the local UZEX Dockerfile; no mastery claim.')
    langs=sorted(d['languages'].items(),key=lambda kv:-kv[1]); total=sum(d['languages'].values()) or 1
    body=t(32,40,'06 / OPEN-SOURCE TELEMETRY',14,'mono')+t(32,94,str(d['repos']),38,'red')+t(32,122,'PUBLIC REPOSITORIES',15,'mono')+t(425,94,str(cal['totalContributions']),38,'blue')+t(425,122,'CONTRIBUTIONS / API WINDOW',15,'mono')+t(825,94,str(c['totalCommitContributions']),38,'red')+t(825,122,'COMMIT CONTRIBUTIONS',15,'mono')
    for wi,week in enumerate(cal['weeks']):
        for di,day in enumerate(week['contributionDays']):
            count=day['contributionCount'];color=['#141B2A','#65182E','#B90027','#FF1744','#00BFFF'][min(4,count)]
            body+=f'<rect x="{32+wi*21}" y="{160+di*20}" width="16" height="15" rx="3" fill="{color}"><title>{day["date"]}: {count} contributions</title></rect>'
    body+=t(32,329,f'{days[0]["date"]} → {days[-1]["date"]} / GitHub contribution calendar',14,'mono')
    body+=t(32,369,'LANGUAGES / tracked source bytes in non-fork public repositories',14,'mono')
    for i,(lang,num) in enumerate(langs[:5]): body+=t(32+i*230,404,f'{lang} {num/total:.1%}',17,'blue' if i%2 else 'red')
    body+=t(32,446,'Updated '+d['updated']+' / GitHub REST + GraphQL',14,'mono')
    save('activity',474,body,'Real GitHub activity dashboard','Public repository count, contribution and commit totals, actual calendar and language bytes. Snapshot timestamp included.')
    body=t(32,40,'KAIST // FUTURE DESTINATION',23,'red')+t(32,79,'Building today what I hope will shape tomorrow.',23)
    milestones=['Strengthen academic profile','Build competitive English proficiency','Prepare for SAT / target 1500+','Develop meaningful technical projects','Document hackathons and olympiads','Prepare recommendation letters','Write application essays','Review official admission requirements','Submit a competitive application']
    for i,line in enumerate(milestones):
        y=124+i*44
        body+=f'<circle cx="48" cy="{y-5}" r="7" fill="#050507" stroke="'+('#FF1744' if i<4 else '#00BFFF')+'"/>'+t(74,y,f'{i+1:02}  '+line,21,'muted')
        if i<8:body+=f'<path d="M48 {y+4}v26" stroke="#263249"/>'
    body+=t(32,548,'PERSONAL ROADMAP / goals, not completed milestones or an admission offer',15,'mono')
    save('kaist-roadmap',575,body,'My journey to KAIST — personal goals, not admission claims')
    # Traditional contribution-grid snake: serpentine travel through exact day positions.
    grid=t(32,36,'CONTRIBUTION SNAKE / authentic calendar, decorative traversal',16,'mono')
    route=[]; cells=[]
    for wi,week in enumerate(cal['weeks']):
        order=list(enumerate(week['contributionDays']))
        if wi%2: order.reverse()
        for di,day in order:
            x=40+wi*21;y=65+di*20;route.append((x+8,y+7))
            color=['#141B2A','#65182E','#B90027','#FF1744','#00BFFF'][min(4,day['contributionCount'])]
            cells.append((x,y,color,day))
    for i,(x,y,color,day) in enumerate(cells):
        hit=(i+1)/len(cells)*90
        grid+=f'<style>@keyframes eat{i}{{0%,{hit:.3f}%{{opacity:1}}{hit+.1:.3f}%,96%{{opacity:.12}}100%{{opacity:1}}}}</style><rect x="{x}" y="{y}" width="16" height="15" rx="3" fill="{color}" style="animation:eat{i} 35s linear infinite"><title>{day["date"]}: {day["contributionCount"]} contributions</title></rect>'
    travel='M '+' L '.join(f'{x} {y}' for x,y in route)
    grid+=f'<style>@keyframes crawl{{0%{{offset-distance:0%;opacity:0}}1%{{opacity:1}}90%,96%{{offset-distance:100%;opacity:1}}100%{{offset-distance:100%;opacity:0}}}}</style><g style="offset-path:path(\'{travel}\');offset-rotate:auto;animation:crawl 35s linear infinite"><rect x="-33" y="-5" width="38" height="10" rx="5" fill="#FF1744"/><circle cx="5" cy="0" r="6" fill="#00BFFF"/><circle cx="7" cy="-2" r="1.5" fill="#050507"/></g>'
    grid+=t(32,233,'Daily source: GitHub contributionCalendar / '+d['updated'],14,'mono')
    save('contribution-snake',260,grid,'Contribution snake','Decorative red-blue snake eats the actual daily contribution grid. Traversal is artistic, counts and positions are authentic.')
    save('becko-snake',220,t(32,36,'BECKO / SNAKE-TO-APPLE',15,'mono')+snake_art(350,167,1.5),'Decorative snake traces BECKO')
    for slug,label,abbr in [('github','GitHub','GH'),('telegram','Telegram','TG'),('instagram','Instagram','IG'),('linkedin','LinkedIn','IN'),('youtube','YouTube','YT')]:
        save('social-'+slug,70,panel(1,1,238,68)+t(16,44,abbr,21,'red')+t(66,44,label,22),'Connect on '+label)
        for suffix in ['', '-static']:
            path=A/f'social-{slug}{suffix}.svg'
            path.write_text(path.read_text().replace('viewBox="0 0 1200 70"','viewBox="0 0 240 70"').replace('width="1200" height="70"','width="240" height="70"').replace('width="1198" height="68"','width="238" height="68"'))
    save('footer',95,t(32,44,'BECKO.DEV',25,'red')+t(32,74,'Developer. Builder. Innovator. / Uzbekistan → the world',18,'mono'),'BECKO — Developer. Builder. Innovator.')
if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--offline',action='store_true');args=parser.parse_args()
    # Failed refresh exits without replacing the previous good data or artwork.
    data=json.loads((ROOT/'data/activity.json').read_text()) if args.offline else snapshot()
    generate(data)
