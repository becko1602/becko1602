"""Self-contained cyberpunk SVG cards with authentic GitHub data."""
from pathlib import Path
from html import escape as esc
import re, math, xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
A=R/'assets'
BASE='text{font-family:Arial,Helvetica,sans-serif;fill:#EDF1F5}.mono{font-family:monospace;fill:#8795A8}.accent{fill:#35E8EF}.muted{fill:#9CA9B9}.s0{stop-color:#00D9E8}.s1{stop-color:#6957FF}.s2{stop-color:#F34EC4}.snake{stroke:#397E65}.logo{fill:#35E8EF}'
MOTION='''
@keyframes hue0{0%,100%{stop-color:#00D9E8}33%{stop-color:#6957FF}66%{stop-color:#F34EC4}}
@keyframes hue1{0%,100%{stop-color:#6957FF}33%{stop-color:#F34EC4}66%{stop-color:#00D9E8}}
@keyframes hue2{0%,100%{stop-color:#F34EC4}33%{stop-color:#00D9E8}66%{stop-color:#6957FF}}
@keyframes accent{0%,100%{fill:#35E8EF}33%{fill:#7899C8}66%{fill:#AA8AC7}}
@keyframes snakeColor{0%,100%{stroke:#397E65}33%{stroke:#3C629C}66%{stroke:#7852A0}}
@keyframes breathe{0%,100%{opacity:.7}50%{opacity:1}}
@keyframes scan{0%,10%{transform:translateX(-1200px)}85%,100%{transform:translateX(1200px)}}
@keyframes energy{to{stroke-dashoffset:-180}}
@keyframes travel{0%{stroke-dashoffset:65;opacity:0}3%{opacity:1}94%{opacity:1}100%{stroke-dashoffset:-1000;opacity:0}}
@keyframes draw{0%,25%{stroke-dashoffset:1;opacity:0}32%{opacity:.9}78%,92%{stroke-dashoffset:0;opacity:1}100%{stroke-dashoffset:0;opacity:0}}
@keyframes apple{0%,24%{opacity:1}30%,100%{opacity:0}}
.s0{animation:hue0 24s ease-in-out infinite}.s1{animation:hue1 24s ease-in-out infinite}.s2{animation:hue2 24s ease-in-out infinite}
.accent,.logo{animation:accent 24s ease-in-out infinite}.snake{animation:snakeColor 24s ease-in-out infinite}
@media(prefers-reduced-motion:reduce){*{animation:none!important}.beam{display:none}.trail{stroke-dashoffset:0!important;opacity:1!important}}
'''
FONT={'B':['11110','10001','10001','11110','10001','10001','11110'],'E':['11111','10000','10000','11110','10000','10000','11111'],'C':['01111','10000','10000','10000','10000','10000','01111'],'K':['10001','10010','10100','11000','10100','10010','10001'],'O':['01110','10001','10001','10001','10001','10001','01110']}
WORD='M0 0V-50H25Q45 -50 45 -37Q45 -25 25 -25H0H28Q48 -25 48 -12Q48 0 28 0Z M72 0V-50H115 M72 -25H108 M72 0H115 M185 -45Q140 -68 140 -25Q140 15 185 -5 M210 0V-50 M210 -25L250 -50 M210 -25L250 0 M280 -25Q280 -50 303 -50Q326 -50 326 -25Q326 0 303 0Q280 0 280 -25'
def text(x,y,value,size=20,cls='',extra=''):
    return f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" {extra}>{esc(str(value))}</text>'
def panel(x,y,w,h):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#101426" stroke="#1D2C39"/>'
def logo(slug,x,y,size=32):
    p=A/'icons'/f'{slug}.svg'
    if not p.exists():return text(x,y+size*.75,slug[:2].upper(),size*.6,'accent')
    root=ET.parse(p).getroot()
    paths=''.join(f'<path d="{esc(el.attrib["d"],quote=True)}"/>' for el in root.iter() if el.tag.endswith('path') and 'd' in el.attrib)
    return f'<g transform="translate({x} {y}) scale({size/24})" class="logo">{paths}</g>'
def save(name,height,body,title,desc=None,width=1200):
    head=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img"><title>{esc(title)}</title><desc>{esc(desc or title)}</desc>'
    defs='<defs><linearGradient id="rgb"><stop class="s0"/><stop offset=".5" class="s1"/><stop offset="1" class="s2"/></linearGradient><linearGradient id="shine"><stop stop-color="#A7CABB" stop-opacity="0"/><stop offset=".5" stop-color="#A7CABB" stop-opacity=".7"/><stop offset="1" stop-color="#A7CABB" stop-opacity="0"/></linearGradient><radialGradient id="glow"><stop stop-color="#173D31" stop-opacity=".45"/><stop offset="1" stop-color="#090B16" stop-opacity="0"/></radialGradient></defs>'
    frame=f'<rect width="{width}" height="{height}" rx="20" fill="#090B16"/><rect x="1" y="1" width="{width-2}" height="{height-2}" rx="20" fill="none" stroke="url(#rgb)" stroke-opacity=".8"/>'
    (A/f'{name}.svg').write_text(head+defs+'<style>'+BASE+MOTION+'</style>'+frame+body+'</svg>')
    static=re.sub(r'<style>.*?</style>','',body,flags=re.S)
    static=re.sub(r' style="[^"]*"','',static)
    static=re.sub(r'<rect[^>]*class="beam"[^>]*/>','',static)
    (A/f'{name}-static.svg').write_text(head+defs+'<style>'+BASE+'</style>'+frame+static+'</svg>')
def generate(d):
    c=d['collection'];cal=c['contributionCalendar'];weeks=cal['weeks'];days=[day for w in weeks for day in w['contributionDays']]
    body=panel(24,24,1152,312)+text(48,58,'becko@arch ~ / terminal',16,'mono')
    cmds=[('whoami','Behruzbek Bekchanov / Uzbekistan'),('cat interests.txt','Full-stack · AI · Cybersecurity · Computer Engineering'),('ls ~/projects','eDoska/  Becko/  becko-arch-linux/'),('echo $MISSION','Build impactful products and opportunities in Uzbekistan.'),('neofetch','Arch Linux / Hyprland / terminal-driven workflow')]
    for i,(cmd,out) in enumerate(cmds):
        body+=f'<style>@keyframes cmd{i}{{0%{{clip-path:inset(0 100% 0 0)}}{8+i*8}%{{clip-path:inset(0 0 0 0)}}100%{{clip-path:inset(0 0 0 0)}}}}</style><g style="animation:cmd{i} 20s steps(24,end) infinite">'+text(48,96+i*46,'❯ '+cmd,17,'accent')+text(70,117+i*46,out,17,'muted')+'</g>'
    body+='<rect x="1040" y="294" width="10" height="20" class="accent" style="animation:breathe 4s infinite"/>'
    save('terminal',360,body,'Arch Linux terminal introduction')
    categories=[('FRONTEND',[('react','React'),('nextdotjs','Next.js'),('javascript','JavaScript'),('typescript','TypeScript'),('html5','HTML5'),('css','CSS3'),('tailwindcss','Tailwind CSS')]),('BACKEND',[('nodedotjs','Node.js'),('python','Python'),('fastapi','FastAPI')]),('SYSTEMS & TOOLS',[('archlinux','Arch Linux'),('linux','Linux / Hyprland'),('git','Git'),('github','GitHub'),('docker','Docker¹')]),('AI & AUTOMATION',[('telegram','Telegram bots'),('python','AI assistants')])]
    body=text(32,40,'DEVELOPMENT TOOLKIT / TECHNOLOGIES I USE & EXPLORE',15,'mono')
    for i,(name,items) in enumerate(categories):
        x=24+(i%2)*580;y=65+(i//2)*310
        body+=panel(x,y,568,292)+text(x+24,y+37,name,21,'accent')
        for j,(slug,label) in enumerate(items):
            xx=x+24+(j%2)*272;yy=y+65+(j//2)*50
            body+=logo(slug,xx,yy,30)+text(xx+44,yy+23,label,20)
        if i==1:body+=text(x+24,y+237,'REST APIs / project-based exploration',18,'muted')
        if i==2:body+=text(x+24,y+263,'VS Code / terminal workflows',18,'muted')
        if i==3:body+=text(x+24,y+190,'LLM integrations / workflow automation',18,'muted')+text(x+24,y+225,'Voice interfaces / practical AI tools',18,'muted')
    save('tech-stack',695,body,'Technology stack with official brand logos','Frontend, backend, Linux and tools, AI and automation. Logos are vendored from Simple Icons; technology use is not a mastery claim.')
    mobile=text(24,36,'DEVELOPMENT TOOLKIT',18,'mono')
    for i,(name,items) in enumerate(categories):
        x=16;y=60+i*310
        mobile+=panel(x,y,568,292)+text(x+24,y+37,name,21,'accent')
        for j,(slug,label) in enumerate(items):
            xx=x+24+(j%2)*272;yy=y+65+(j//2)*50
            mobile+=logo(slug,xx,yy,30)+text(xx+44,yy+23,label,20)
        if i==1:mobile+=text(x+24,y+237,'REST APIs / project-based exploration',18,'muted')
        if i==2:mobile+=text(x+24,y+263,'VS Code / terminal workflows',18,'muted')
        if i==3:mobile+=text(x+24,y+190,'LLM integrations / workflow automation',18,'muted')+text(x+24,y+225,'Voice interfaces / practical AI tools',18,'muted')
    save('tech-stack-mobile',1310,mobile,'Technology stack with official brand logos — mobile',width=600)
    langs=sorted(d['languages'].items(),key=lambda kv:-kv[1]);total=sum(d['languages'].values()) or 1
    body=text(32,40,'05 / OPEN-SOURCE TELEMETRY',15,'mono')+text(32,94,d['repos'],38,'accent')+text(32,122,'PUBLIC REPOSITORIES',15,'mono')+text(425,94,cal['totalContributions'],38,'accent')+text(425,122,'CONTRIBUTIONS / API WINDOW',15,'mono')+text(825,94,c['totalCommitContributions'],38,'accent')+text(825,122,'COMMIT CONTRIBUTIONS',15,'mono')
    colors=['#142027','#1C3C33','#285A48','#344E7A','#634888']
    for wi,week in enumerate(weeks):
        for di,day in enumerate(week['contributionDays']):
            body+=f'<rect x="{32+wi*21}" y="{160+di*20}" width="16" height="15" rx="3" fill="{colors[min(4,day["contributionCount"])]}"><title>{day["date"]}: {day["contributionCount"]} contributions</title></rect>'
    body+=text(32,329,f'{days[0]["date"]} → {days[-1]["date"]} / GitHub contribution calendar',14,'mono')+text(32,369,'LANGUAGES / source bytes in non-fork public repositories',14,'mono')
    slugs={'TypeScript':'typescript','Python':'python','CSS':'css','JavaScript':'javascript','Shell':'linux','HTML':'html5'}
    for i,(lang,num) in enumerate(langs[:5]):body+=logo(slugs.get(lang,lang.lower()),32+i*230,389,24)+text(65+i*230,409,f'{lang} {num/total:.1%}',17,'accent')
    body+=text(32,450,'Updated '+d['updated']+' / GitHub REST + GraphQL',14,'mono')
    save('activity',478,body,'Real GitHub activity dashboard','Actual contribution calendar, public repositories, commit contributions and programming-language source bytes.')
    for slug,label in [('github','GitHub'),('telegram','Telegram'),('instagram','Instagram'),('linkedin','LinkedIn'),('youtube','YouTube')]:
        save('social-'+slug,70,panel(1,1,238,68)+logo(slug,18,23,25)+text(60,44,label,22),'Connect on '+label,width=240)
    save('footer',95,text(32,44,'BECKO.DEV',25,'accent')+text(32,74,'Developer. Builder. Innovator. / Uzbekistan → the world',18,'mono'),'BECKO — Developer. Builder. Innovator.')


_original_generate = generate
def generate(d):
    _original_generate(d)
    # Angular polygon lettering drawn locally; no external font dependency.
    glyphs={
      'B':'M0 0H60L80 20V43L69 54L80 65V88L60 108H0Z M24 22V43H51L57 37V28L51 22Z M24 65V86H51L57 80V71L51 65Z',
      'E':'M0 0H80V23H25V42H68V65H25V85H80V108H0Z',
      'C':'M20 0H80V25H30L25 30V78L30 83H80V108H20L0 88V20Z',
      'K':'M0 0H25V43L60 0H88L45 53L88 108H58L25 67V108H0Z',
      'O':'M20 0H64L84 20V88L64 108H20L0 88V20Z M29 24L24 29V79L29 84H55L60 79V29L55 24Z'}
    word=''
    for i,ch in enumerate('BECKO'):
        word+=f'<path d="{glyphs[ch]}" transform="translate({i*105} 0)" fill-rule="evenodd"/>'
    body='<defs><pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" stroke="#8790FF" stroke-opacity=".07"/></pattern></defs><rect width="1200" height="420" fill="url(#grid)"/>'
    body+='<path d="M0 365H730L790 305H1200M0 372H730L790 312H1200" fill="none" stroke="#F34EC4" opacity=".4"/>'
    body+=text(42,45,'BECKO / PERSONAL INTERFACE',15,'mono')+text(1155,45,'UZB · 1602',15,'accent','text-anchor="end"')
    body+='<g transform="translate(44 100) scale(1.48)" fill="#F2F4FF">'+word+'</g><path d="M44 282H206L221 267H815" fill="none" stroke="#35E8EF" stroke-width="3"/>'
    body+=text(44,328,'BEHRUZBEK BEKCHANOV',25,extra='font-weight="700" letter-spacing="4"')+text(44,365,'FULL-STACK DEVELOPER  /  AI & AUTOMATION  /  LINUX',18,'accent')
    body+='<path d="M1000 115L1128 115V243H1000Z M1024 139H1104V219H1024Z" fill="none" stroke="#6957FF" stroke-width="2"/><path d="M984 99V75H1010M1144 99V75H1118M984 259V283H1010M1144 259V283H1118" fill="none" stroke="#F34EC4" stroke-width="3"/>'
    body+=text(1064,191,'</>',39,'accent','text-anchor="middle"')+text(1064,319,'BUILD / SHIP / REPEAT',12,'mono','text-anchor="middle"')
    save('hero',420,body,'BECKO — Behruzbek Bekchanov','Angular custom BECKO lettering, cyan circuits, ultraviolet and hot pink on midnight black. No snake.')
    save('roles',78,text(32,47,'DEVELOPER',20,'accent')+text(405,47,'AI BUILDER',20,'accent')+text(830,47,'LINUX ENTHUSIAST',20,'accent'),'Developer / AI builder / Linux enthusiast')
    items=[('html5','HTML5','#E34F26'),('css','CSS','#316BF3'),('javascript','JAVASCRIPT','#A68B12'),('typescript','TYPESCRIPT','#3178C6'),('react','REACT','#087F96'),('nextdotjs','NEXT.JS','#292C40'),('tailwindcss','TAILWIND','#078CA4'),('nodedotjs','NODE.JS','#388444'),('python','PYTHON','#376DA0'),('fastapi','FASTAPI','#008C80'),('git','GIT','#E64E36'),('github','GITHUB','#292C40'),('docker','DOCKER','#1684D1'),('linux','LINUX','#82700A'),('archlinux','ARCH LINUX','#147EAC'),('telegram','TELEGRAM','#2283B1')]
    body=''
    for i,(slug,label,color) in enumerate(items):
        x=8+(i%4)*298;y=8+(i//4)*65
        body+=f'<rect x="{x}" y="{y}" width="286" height="54" fill="{color}"/>'+logo(slug,x+14,y+13,28)+text(x+56,y+34,label,19,extra='font-weight="700" letter-spacing="2"')
    save('tech-stack',268,body,'Tech stack','HTML, CSS, JavaScript, TypeScript, React, Next.js, Tailwind, Node.js, Python, FastAPI, Git, GitHub, Docker, Linux, Arch Linux and Telegram.')
    body=''
    for i,(label,detail) in enumerate([('GDG EDTECH','2nd place / team'),('AIFU HACKATHON','Top 10 / team'),('BUILD IN PUBLIC','Code. Learn. Repeat.')]):
        x=16+i*396
        body+=panel(x,16,380,162)+text(x+22,57,'0'+str(i+1)+' / MILESTONE',14,'mono')+text(x+22,104,label,23,'accent','font-weight="700"')+text(x+22,144,detail,18,'muted')
    save('trophies',194,body,'Hackathon highlights','GDG EdTech team second place and AIFU Top 10 team result, as recorded in the original profile. These are personal highlights, not GitHub trophies.')
    body=text(36,56,'“Talk is cheap. Show me the code.”',30,'accent')+text(1164,101,'— Linus Torvalds',19,'muted','text-anchor="end"')
    save('quote',132,body,'Developer quote — Linus Torvalds')
