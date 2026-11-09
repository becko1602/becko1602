"""Deterministic SVG and GIF terminal animations; no network or runtime scripts.

GIFs use the bundled OFL JetBrains Mono subset. SVG identity glyphs use paths
from the same font, so the signature cannot change with a viewer's fonts.
"""
from pathlib import Path
import json
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

A = Path(__file__).resolve().parents[1] / 'assets'
BG = '#050807'
GREEN = '#00FF41'
MUTED = '#8B949E'
TEXT = '#E6EDF3'
BORDER = '#24332B'
FONT = A / 'fonts/JetBrainsMono-subset.ttf'
STATES = ['8#K@0', '7{X/1', 'B3C|0', 'BE#<0', 'BEC/0', 'BECK0', 'BECKO']


def font(size):
    return ImageFont.truetype(str(FONT), size)


def canvas(w, h):
    im = Image.new('RGB', (w, h), BG)
    ImageDraw.Draw(im).rounded_rectangle((1, 1, w-2, h-2), radius=12, outline=BORDER)
    return im


def gif(name, frames, duration):
    # One shared palette avoids color shimmer across frames.
    palette = Image.new('RGB', (256, 1))
    palette.putdata([(5, 8, 7), (230, 237, 243), (139, 148, 158), (36, 51, 43), (0, 255, 65), (0, 200, 83)] +
                    [(0, i, int(i*.25)) for i in range(6, 256)])
    palette = palette.quantize(colors=256)
    frames = [f.quantize(palette=palette, dither=Image.Dither.NONE) for f in frames]
    frames[0].save(A / f'{name}.gif', save_all=True, append_images=frames[1:],
                   duration=duration, loop=0, optimize=True, disposal=1)


def identity(value, x=64, y=175):
    glyphs = json.loads((A / 'fonts/glyphs.json').read_text())
    return '<g fill="#00FF41">' + ''.join(
        f'<path d="{glyphs[c]}" transform="translate({x+i*50.4} {y}) scale(.084 -.084)"/>'
        for i, c in enumerate(value)) + '</g>'


def hero_svg():
    from design import save, text
    body = text(48, 38, 'becko@arch:~ / identity', 15, 'mono')
    body += '<path d="M24 58H1176" stroke="#24332B"/>'
    body += text(48, 100, '> initializing identity...', 18, 'mono')
    body += identity('BECKO')
    for i, state in enumerate(STATES[:-1]):
        # Final glyph layer stays readable whenever animation is disabled.
        start, end = i*1.2, (i+1)*1.2
        body += (f'<style>@keyframes decode{i}{{0%,{start}%{{opacity:0}}'
                 f'{start+.01}%,{end}%{{opacity:1}}{end+.01}%,100%{{opacity:0}}}}'
                 f'.decode{i}{{opacity:0;animation:decode{i} 16s steps(1) infinite}}'
                 '</style>' + f'<g class="decode{i}"><rect x="48" y="110" width="300" height="85" fill="#050807"/>' + identity(state) + '</g>')
    body += '<style>@keyframes cursor{0%,49%{opacity:1}50%,100%{opacity:0}}.cursor{animation:cursor 1.2s steps(1) infinite}@keyframes scanline{0%{transform:translateY(0);opacity:0}15%,75%{opacity:.12}100%{transform:translateY(260px);opacity:0}}.scanline{animation:scanline 16s linear infinite}</style>'
    body += '<path class="cursor" d="M324 180H359" stroke="#00FF41" stroke-width="3"/>'
    body += text(48, 228, 'BEHRUZBEK BEKCHANOV', 21)
    body += text(48, 267, 'Full-stack developer / AI & automation / Linux', 18, 'muted')
    body += '<path class="scanline" d="M24 60H1176" stroke="#00FF41"/>'
    save('hero', 308, body, 'BECKO — Behruzbek Bekchanov', 'JetBrains Mono identity decodes into BECKO. Terminal cursor; quiet sixteen-second loop.')
    save('hero-mobile', 308, body, 'BECKO — Behruzbek Bekchanov', 'Compact terminal identity for mobile.', width=600)
    # Strip decoding overlays and motion styles from the static fallback.
    import re
    p = A / 'hero-static.svg'
    s = p.read_text()
    s = re.sub(r'<g class="decode\d+">.*?</g></g>', '', s)
    s = re.sub(r'<path class="scanline"[^>]*/>', '', s)
    p.write_text(s)
    p = A / 'hero-mobile-static.svg'
    mobile = p.read_text()
    mobile = re.sub(r'<g class="decode\d+">.*?</g></g>', '', mobile)
    mobile = re.sub(r'<path class="scanline"[^>]*/>', '', mobile)
    p.write_text(mobile)


def hero_gif():
    frames = []
    for n in range(160):
        t = n/10
        value = STATES[min(6, int(t/.16))] if t < 1 else 'BECKO'
        im = canvas(1200, 308)
        d = ImageDraw.Draw(im)
        d.text((48, 22), 'becko@arch:~ / identity', font=font(15), fill=MUTED)
        d.line((24, 58, 1176, 58), fill=BORDER)
        sy = 61 + int(n/160*225)
        d.line((24, sy, 1176, sy), fill='#0A1A0D')
        d.text((48, 84), '> initializing identity...', font=font(18), fill=MUTED)
        # Fixed text stays sharp; only the blurred layer breathes.
        layer = Image.new('RGB', im.size, BG)
        ld = ImageDraw.Draw(layer)
        ld.text((64, 175), value, font=font(84), anchor='ls', fill=(0, int(26+8*math.sin(t*math.pi/4)), 7))
        glow = layer.filter(ImageFilter.GaussianBlur(5))
        from PIL import ImageChops
        im = ImageChops.lighter(im, glow)
        d = ImageDraw.Draw(im)
        d.text((64, 175), value, font=font(84), anchor='ls', fill=GREEN)
        if n % 12 < 6:
            d.line((324, 180, 359, 180), fill=GREEN, width=3)
        # One faint character flicker during the long final hold.
        if n == 119:
            d.line((217, 146, 250, 146), fill='#007A24')
        d.text((48, 211), 'BEHRUZBEK BEKCHANOV', font=font(21), fill=TEXT)
        d.text((48, 249), 'Full-stack developer / AI & automation / Linux', font=font(18), fill=MUTED)
        frames.append(im)
    gif('hero', frames, 100)
    mobile = []
    for frame in frames:
        im = frame.crop((0, 0, 600, 308))
        ImageDraw.Draw(im).rounded_rectangle((1, 1, 598, 306), radius=12, outline=BORDER)
        mobile.append(im)
    gif('hero-mobile', mobile, 100)


def snake():
    from design import save, text
    colors = ['#101B14', '#0E4429', '#006D32', '#008F39']
    # A rounded rectangle inside the contribution grid; tail follows the same route.
    points = []
    for cx, cy, start in [(1095, 112, -90), (1095, 188, 0), (105, 188, 90), (105, 112, 180)]:
        if points:
            prev = points[-1]
            end = (cx+22*math.cos(math.radians(start)), cy+22*math.sin(math.radians(start)))
            length = math.dist(prev, end)
            points += [(prev[0]+(end[0]-prev[0])*j/max(1,int(length/4)), prev[1]+(end[1]-prev[1])*j/max(1,int(length/4))) for j in range(1,max(1,int(length/4))+1)]
        points += [(cx+22*math.cos(math.radians(start+j)), cy+22*math.sin(math.radians(start+j))) for j in range(0,91,10)]
    first, last = points[0], points[-1]
    points += [(last[0]+(first[0]-last[0])*j/248, last[1]+(first[1]-last[1])*j/248) for j in range(1,249)]
    path = 'M'+' L'.join(f'{x:.1f} {y:.1f}' for x,y in points)+' Z'
    length = sum(math.dist(points[i], points[(i+1)%len(points)]) for i in range(len(points)))
    body = text(32, 34, 'CONTRIBUTION SNAKE / DEMO', 15, 'mono')
    base = canvas(1200, 288)
    bd = ImageDraw.Draw(base)
    bd.text((32, 20), 'CONTRIBUTION SNAKE / DEMO', font=font(15), fill=MUTED)
    for col in range(53):
        for row in range(7):
            x, y = 24+col*22, 69+row*22
            c = colors[(col*17+row*13)%11%4] if (col*7+row*11)%5 < 2 else colors[0]
            body += f'<rect x="{x}" y="{y}" width="16" height="16" rx="3" fill="{c}"/>'
            bd.rounded_rectangle((x,y,x+16,y+16),radius=3,fill=c)
    food_indices = [int(len(points)*k) for k in (.12,.38,.62,.88)]
    for idx in food_indices:
        x,y = points[idx]
        phase = idx/len(points)*100
        body += f'<style>@keyframes food{idx}{{0%,{phase:.2f}%{{opacity:1}}{phase+.1:.2f}%,99.9%{{opacity:0}}100%{{opacity:1}}}}</style><rect x="{x-5:.1f}" y="{y-5:.1f}" width="10" height="10" rx="2" fill="#00FF41" style="animation:food{idx} 16s linear infinite"/>'
    body += f'<path d="{path}" fill="none" stroke="#00FF41" stroke-width="10" stroke-linecap="round" stroke-dasharray="90 {length-90:.2f}" style="animation:move 16s linear infinite"/><style>@keyframes move{{to{{stroke-dashoffset:-{length:.2f}}}}}</style>'
    body += text(32, 264, 'Synthetic cells / animation study / not GitHub activity', 15, 'mono')
    bd.text((32, 250), 'Synthetic cells / animation study / not GitHub activity', font=font(15), fill=MUTED)
    save('contribution-snake', 288, body, 'Contribution snake — synthetic demo', 'Rectangular green contribution-style grid with a smooth looping snake and collectible food. No GitHub statistics.')
    frames=[]
    for n in range(200):
        im=base.copy();d=ImageDraw.Draw(im);head=int(n/200*len(points))
        for idx in food_indices:
            if head < idx:
                x,y=points[idx]
                d.rounded_rectangle((x-8,y-8,x+8,y+8),radius=4,fill='#0E4429')
                d.rounded_rectangle((x-5,y-5,x+5,y+5),radius=2,fill=GREEN)
        tail=[points[(head-j)%len(points)] for j in range(23,-1,-1)]
        d.line(tail,fill='#00C853',width=10,joint='curve')
        x,y=points[head];d.ellipse((x-6,y-6,x+6,y+6),fill=GREEN)
        frames.append(im)
    gif('contribution-snake',frames,80)


def generate_motion():
    hero_svg()
    hero_gif()
    snake()
