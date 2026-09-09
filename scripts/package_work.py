"""Create a standalone OpenAI plugin ZIP without case data or local configuration."""
from pathlib import Path
import hashlib
import json
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / 'plugins/pratica-juridica-work'
manifest = json.loads((PLUGIN / '.codex-plugin/plugin.json').read_text(encoding='utf-8'))
out = ROOT / 'outputs' / f"{manifest['name']}-{manifest['version']}.zip"
out.parent.mkdir(exist_ok=True)
files = [PLUGIN / '.codex-plugin/plugin.json', PLUGIN / 'README.md', PLUGIN / 'LICENSE']
files += sorted(p for p in (PLUGIN / 'skills').rglob('*')
                if p.is_file() and p.suffix in {'.md', '.py', '.yaml', '.png', '.jpg'}
                and '__pycache__' not in p.parts)
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as archive:
    for path in files:
        archive.write(path, path.relative_to(PLUGIN).as_posix())
with zipfile.ZipFile(out) as archive:
    assert archive.testzip() is None
    assert '.codex-plugin/plugin.json' in archive.namelist()
print(out)
print('SHA-256:', hashlib.sha256(out.read_bytes()).hexdigest())
