"""Local SVG design system: restrained forest / indigo / violet, no external widgets."""
from pathlib import Path
from html import escape as esc
import re, math, xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
A=R/'assets'
BASE='text{font-family:Arial,Helvetica,sans-serif;fill:#EDF1F5}.mono{font-family:monospace;fill:#8795A8}.accent{fill:#70A18C}.muted{fill:#9CA9B9}.s0{stop-color:#25634B}.s1{stop-color:#294E85}.s2{stop-color:#653F8F}.snake{stroke:#397E65}.logo{fill:#80B5A0}'
MOTION='''
@keyframes hue0{0%,100%{stop-color:#25634B}33%{stop-color:#294E85}66%{stop-color:#653F8F}}
@keyframes hue1{0%,100%{stop-color:#294E85}33%{stop-color:#653F8F}66%{stop-color:#25634B}}
@keyframes hue2{0%,100%{stop-color:#653F8F}33%{stop-color:#25634B}66%{stop-color:#294E85}}
@keyframes accent{0%,100%{fill:#70A18C}33%{fill:#7899C8}66%{fill:#AA8AC7}}
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
def panel(x,y,w,h):return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="16" fill="#0A1119" stroke="#1D2C39"/>'
def logo(slug,x,y,size=32):
    p=A/'icons'/f'{slug}.svg'
    if not p.exists():return text(x,y+size*.75,slug[:2].upper(),size*.6,'accent')
    root=ET.parse(p).getroot()
    paths=''.join(f'<path d="{esc(el.attrib["d"],quote=True)}"/>' for el in root.iter() if el.tag.endswith('path') and 'd' in el.attrib)
    return f'<g transform="translate({x} {y}) scale({size/24})" class="logo">{paths}</g>'
def save(name,height,body,title,desc=None,width=1200):
    head=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img"><title>{esc(title)}</title><desc>{esc(desc or title)}</desc>'
    defs='<defs><linearGradient id="rgb"><stop class="s0"/><stop offset=".5" class="s1"/><stop offset="1" class="s2"/></linearGradient><linearGradient id="shine"><stop stop-color="#A7CABB" stop-opacity="0"/><stop offset=".5" stop-color="#A7CABB" stop-opacity=".7"/><stop offset="1" stop-color="#A7CABB" stop-opacity="0"/></linearGradient><radialGradient id="glow"><stop stop-color="#173D31" stop-opacity=".45"/><stop offset="1" stop-color="#050709" stop-opacity="0"/></radialGradient></defs>'
    frame=f'<rect width="{width}" height="{height}" rx="20" fill="#050709"/><rect x="1" y="1" width="{width-2}" height="{height-2}" rx="20" fill="none" stroke="url(#rgb)" stroke-opacity=".8"/>'
    (A/f'{name}.svg').write_text(head+defs+'<style>'+BASE+MOTION+'</style>'+frame+body+'</svg>')
    static=re.sub(r'<style>.*?</style>','',body,flags=re.S)
    static=re.sub(r' style="[^"]*"','',static)
    static=re.sub(r'<rect[^>]*class="beam"[^>]*/>','',static)
    (A/f'{name}-static.svg').write_text(head+defs+'<style>'+BASE+'</style>'+frame+static+'</svg>')
def moving_snake(path,duration='28s',width=10,length=65):
    # A moving dash is a flexible body, so bends never rotate a rigid rectangle.
    return f'<path class="snake" d="{path}" pathLength="1000" fill="none" stroke-width="{width}" stroke-linecap="round" stroke-linejoin="round" stroke-dasharray="{length} 1100" stroke-dashoffset="-440" style="animation:travel {duration} linear infinite,snakeColor 24s ease-in-out infinite"/>'
def snake_art(x,y,scale=1):
    # Continuous bezier route: enter from right, reach apple, curve into final O.
    route='M360 -105H40Q-8 -105 -8 -75Q-8 -55 30 -55H250Q305 -55 305 -25Q305 5 280 5'
    return f'<g transform="translate({x} {y}) scale({scale})"><path d="{WORD}" fill="none" stroke="#182A31" stroke-width="7"/><path class="trail" d="{WORD}" pathLength="1" fill="none" stroke="url(#rgb)" stroke-width="5" stroke-linecap="round" style="stroke-dasharray:1;stroke-dashoffset:0;animation:draw 18s ease-in-out infinite"/><g style="animation:apple 18s linear infinite"><path d="M-16 -77Q-18 -89 -8 -85Q4 -90 2 -77Q-1 -65 -8 -69Q-14 -66 -16 -77" fill="#5A906D"/><path d="M-8 -86Q-6 -96 2 -94" fill="none" stroke="#9ABD9D" stroke-width="3"/></g>'+moving_snake(route,'18s',8)+'</g>'
def generate(d):
    c=d['collection'];cal=c['contributionCalendar'];weeks=cal['weeks'];days=[day for w in weeks for day in w['contributionDays']]
    hero='<ellipse cx="270" cy="170" rx="530" ry="320" fill="url(#glow)"/>'
    for y in [62,300,330]:hero+=f'<path d="M700 {y}H780l28 -18H1160" fill="none" stroke="url(#rgb)" opacity=".35"/>'
    hero+='<path d="M32 345H720l40 -26H1160" fill="none" stroke="url(#rgb)" stroke-dasharray="14 76" style="animation:energy 14s linear infinite"/>'
    hero+=text(38,42,'BECKO.DEV / DIGITAL IDENTITY',16,'mono')+text(38,112,'BEHRUZBEK',48,extra='font-weight="800" letter-spacing="2"')+text(38,169,'BEKCHANOV',48,extra='font-weight="800" letter-spacing="2"')+text(38,211,'FULL-STACK DEVELOPER',22,'accent','letter-spacing="3"')+text(38,251,'From Uzbekistan. Building ambitious ideas',19,'muted')+text(38,278,'into real-world products.',19,'muted')
    hero+='<circle cx="44" cy="315" r="4" class="accent"/>'+text(58,320,'BECKO SYSTEM ONLINE',13,'mono')+text(805,90,'01 / SIGNAL IN MOTION',13,'mono')+snake_art(805,245,.94)+text(805,287,'DEVELOPER. BUILDER. INNOVATOR.',12,'mono')
    save('hero',365,hero,'Behruzbek Bekchanov — Full-Stack Developer','Dark forest, indigo and violet interface. A smooth single-color snake approaches an apple and reveals BECKO.')
    roles=['Full-Stack Developer','AI & Automation Builder','Linux Enthusiast','Hackathon Participant','Future Computer Engineer']
    body=text(32,45,'$ becko --identity',18,'accent')
    for i,role in enumerate(roles):
        lo=i*20;hi=(i+1)*20
        body+=f'<style>@keyframes role{i}{{0%,100%{{opacity:0}}{lo+.01}%,{hi-.01}%{{opacity:1}}}}</style>'+text(340,45,role,21,extra=f'style="opacity:{int(i==0)};animation:role{i} 25s linear infinite"')
    save('roles',78,body,'Full-stack · AI · Linux · Hackathons · Computer Engineering')
    save('identity',90,text(32,40,'FULL-STACK / AI / LINUX',24)+text(32,68,'Hackathon participant · Future Computer Engineer',18,'muted'),'Identity and interests')
    (A/'roles-static.svg').write_text((A/'identity-static.svg').read_text())
    squares='';lit='';index=0;peak=max(1,max(day['contributionCount'] for day in days));sample=days[-81:]
    for li,ch in enumerate('BECKO'):
        for row,line in enumerate(FONT[ch]):
            for col,on in enumerate(line):
                if on=='0':continue
                day=sample[index%len(sample)];bright=.48+.52*math.sqrt(day['contributionCount']/peak)
                shape=f'<rect x="{72+li*218+col*33}" y="{76+row*30}" width="27" height="24" rx="5"'
                squares+=shape+f' fill="url(#rgb)" fill-opacity="{bright:.3f}"><title>{day["date"]}: {day["contributionCount"]} contributions (artistic intensity)</title></rect>'
                lit+=shape+'/>';index+=1
    body=text(34,38,'BECKO / LIVING CONTRIBUTION SIGNATURE',15,'mono')+f'<defs><clipPath id="letters">{lit}</clipPath></defs><g style="animation:breathe 9s ease-in-out infinite">{squares}</g><g clip-path="url(#letters)"><rect class="beam" x="0" y="70" width="390" height="220" fill="url(#shine)" style="animation:scan 12s ease-in-out infinite"/></g>'+text(34,320,'Real daily activity shapes the light / a signature, not a calendar.',16,'mono')
    save('becko-neon',348,body,'BECKO contribution signature','Always-readable contribution squares, a slow light sweep and dark RGB color cycle. Brightness samples actual recent activity; no flicker.')
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
    # Wide horizontal passes with rounded U-turns; no abrupt column-by-column zigzag.
    grid=text(32,36,'CONTRIBUTION SNAKE / smooth traversal, real daily activity',16,'mono')
    for wi,week in enumerate(weeks):
        for di,day in enumerate(week['contributionDays']):
            grid+=f'<rect x="{40+wi*21}" y="{65+di*24}" width="16" height="16" rx="3" fill="{colors[min(4,day["contributionCount"])]}"><title>{day["date"]}: {day["contributionCount"]} contributions</title></rect>'
    left=48;right=48+(len(weeks)-1)*21;route=f'M{left} 73'
    for row in range(7):
        y=73+row*24
        route+=f'H{right if row%2==0 else left}'
        if row<6:route+=f'Q{right+12 if row%2==0 else left-12} {y} {right+12 if row%2==0 else left-12} {y+12}Q{right+12 if row%2==0 else left-12} {y+24} {right if row%2==0 else left} {y+24}'
    grid+=moving_snake(route,'48s',10,11)+text(32,262,'Daily activity / '+d['updated'],14,'mono')
    save('contribution-snake',292,grid,'Contribution snake','A flexible single-color snake follows smooth horizontal lanes and rounded turns over the authentic calendar. Forest, blue and violet colors cycle slowly.')
    save('becko-snake',235,text(32,36,'BECKO / SIGNAL IN MOTION',15,'mono')+snake_art(350,182,1.5),'Decorative BECKO snake')
    for slug,label in [('github','GitHub'),('telegram','Telegram'),('instagram','Instagram'),('linkedin','LinkedIn'),('youtube','YouTube')]:
        save('social-'+slug,70,panel(1,1,238,68)+logo(slug,18,23,25)+text(60,44,label,22),'Connect on '+label,width=240)
    save('footer',95,text(32,44,'BECKO.DEV',25,'accent')+text(32,74,'Developer. Builder. Innovator. / Uzbekistan → the world',18,'mono'),'BECKO — Developer. Builder. Innovator.')
