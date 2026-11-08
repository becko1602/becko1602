"""Offline validation of README, generated SVGs and workflow security."""
from pathlib import Path
import re, json, xml.etree.ElementTree as ET
R=Path(__file__).resolve().parents[1]
readme=(R/'README.md').read_text()
assets=list((R/'assets').rglob('*.svg'))
for p in assets:
    root=ET.parse(p).getroot()
    assert root.tag.endswith('svg') and root.get('viewBox'), p
    assert root.find('{http://www.w3.org/2000/svg}title') is not None,p
    assert root.find('{http://www.w3.org/2000/svg}desc') is not None,p
    assert p.stat().st_size<250000,p
    for el in root.iter():
        assert el.tag.split('}')[-1] not in {'script','foreignObject','image'},p
        for key,value in el.attrib.items():
            assert not key.lower().startswith('on'),p
            if key.endswith('href'): assert value.startswith('#'),(p,value)
for target in re.findall(r'(?:src|srcset)="([^"]+)"',readme):
    assert (R/target).is_file(),target
for p in (R/'assets').glob('*-static.svg'):
    assert '@keyframes' not in p.read_text() and 'animation:' not in p.read_text(),p
for p in (R/'.github/workflows').glob('*.yml'):
    text=p.read_text()
    for action in re.findall(r'uses: ([^\s]+)',text):
        assert re.search(r'@[0-9a-f]{40}$|@sha256:[0-9a-f]{64}$',action),(p,action)
for p in [R/'README.md',*assets,*list((R/'.github/workflows').glob('*.yml'))]:
    assert not re.search(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN .*PRIVATE KEY',p.read_text()),p
assert json.loads((R/'data/activity.json').read_text())['collection']['contributionCalendar']['weeks']
print(f'PASS: {len(assets)} valid SVGs, local image references, static fallbacks, pinned actions and credential scan.')

assert 'kaist' not in readme.lower()
for name in ['hero','tech-stack']:
    assert not re.search(r'#(?:FF1744|B90027|00BFFF)',(R/f'assets/{name}.svg').read_text(),re.I)
print('PASS: KAIST removed; updated artwork uses the new palette.')

assert "snake" not in readme.lower()
assert all(word in readme for word in ["About Me", "Tech Stack", "GitHub Stats", "Hackathon Highlights", "Dev Quote"])
print("PASS: reference-style sections and snake-free README.")
