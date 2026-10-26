"""Validate the local GitHub profile assets without network access."""
from pathlib import Path
import re
import xml.etree.ElementTree as ET
import yaml
ROOT = Path(__file__).resolve().parents[1]
readme = (ROOT / 'README.md').read_text()
assets = list((ROOT / 'assets').glob('*.svg'))
assert assets
for path in assets:
    root = ET.parse(path).getroot()
    assert root.tag.endswith('svg') and root.get('viewBox')
    assert root.find('{http://www.w3.org/2000/svg}title') is not None
    assert root.find('{http://www.w3.org/2000/svg}desc') is not None
    for el in root.iter():
        assert el.tag.split('}')[-1] not in {'script', 'foreignObject', 'image'}, path
        for key, value in el.attrib.items():
            assert not key.lower().startswith('on'), (path, key)
            if key.endswith('href'):
                assert value.startswith('#'), (path, value)
    assert not re.search(r'https?://', path.read_text().replace('http://www.w3.org/2000/svg', ''))
for target in re.findall(r'(?:src|srcset)="([^"]+)"', readme):
    assert not target.startswith(('http:', 'https:')), target
    assert (ROOT / target).is_file(), target
assert 'contribution-snake.svg' not in readme
for name in ['hero', 'typing', 'terminal']:
    assert (ROOT / f'assets/{name}-static.svg').is_file()
    assert '@keyframes' not in (ROOT / f'assets/{name}-static.svg').read_text()
workflow = yaml.safe_load((ROOT / '.github/workflows/contribution-snake.yml').read_text())
assert workflow['permissions'] == {'contents': 'read'}
assert workflow['jobs']['generate']['timeout-minutes'] == 10
for path in [ROOT/'README.md', *assets, *ROOT.glob('.github/workflows/*')]:
    assert not re.search(r'gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|-----BEGIN .*PRIVATE KEY', path.read_text()), path
print(f'PASS: {len(assets)} SVGs, local image paths, static fallbacks, workflow permissions, and credential patterns.')
print('Remote links, GitHub rendering and Actions execution require online verification.')
