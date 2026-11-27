import hashlib
import json
import pathlib
import plistlib
import stat
import tarfile
import zipfile

root = pathlib.Path(__file__).resolve().parent.parent
asar = (root / 'build-tools/app.asar').read_bytes()
results = []
for arch in ['x64', 'ia32', 'arm64']:
    directory = root / 'Windows' / arch
    assert (directory / 'Gazyava-i-Hrumki.exe').read_bytes()[:2] == b'MZ'
    assert (directory / 'resources/app.asar').read_bytes() == asar
    results.append({'platform':'Windows','arch':arch,'status':'verified'})
for arch in ['x64','arm64','armv7l']:
    archive = root / f'Linux/Gazyava-i-Hrumki-linux-{arch}.tar.gz'
    with tarfile.open(archive) as src:
        prefix = f'Gazyava-i-Hrumki-{arch}/'
        assert src.extractfile(prefix+'resources/app.asar').read() == asar
        exe = src.getmember(prefix+'Gazyava-i-Hrumki')
        assert exe.mode & 0o111
        assert src.extractfile(exe).read(4) == b'\x7fELF'
    results.append({'platform':'Linux','arch':arch,'status':'verified'})
for arch in ['x64','arm64']:
    archive = root / f'macOS/Gazyava-i-Hrumki-darwin-{arch}.zip'
    with zipfile.ZipFile(archive) as src:
        assert src.testzip() is None
        prefix = 'Gazyava-i-Hrumki.app/Contents/'
        assert src.read(prefix+'Resources/app.asar') == asar
        assert plistlib.loads(src.read(prefix+'Info.plist'))['CFBundleIdentifier'] == 'com.kabil.gazyava'
        assert any(stat.S_ISLNK(item.external_attr >> 16) for item in src.infolist())
        assert src.getinfo(prefix+'MacOS/Electron').external_attr >> 16 & 0o111
    results.append({'platform':'macOS','arch':arch,'status':'verified; local ad-hoc signing required'})
with zipfile.ZipFile(root / 'Android/Gazyava-i-Hrumki.apk') as src:
    assert src.testzip() is None
    assert src.read('classes.dex')[:4] == b'dex\n'
    for file in (root/'Web').iterdir():
        if file.suffix != '.txt': assert src.read('assets/'+file.name) == file.read_bytes()
results.append({'platform':'Android','arch':'universal','status':'verified'})
(root/'build-tools/artifact-verification.json').write_text(json.dumps(results,indent=2),encoding='utf8')
files = [root/'Android/Gazyava-i-Hrumki.apk', *sorted((root/'Linux').glob('*.tar.gz')), *sorted((root/'macOS').glob('*.zip'))]
files += [root/f'Windows/{a}/Gazyava-i-Hrumki.exe' for a in ['x64','ia32','arm64']]
lines = []
for file in files:
    with file.open('rb') as stream: digest = hashlib.file_digest(stream,'sha256').hexdigest()
    lines.append(f'{digest}  {file.relative_to(root).as_posix()}')
(root/'SHA256SUMS.txt').write_text('\n'.join(lines)+'\n',encoding='utf8')
print(json.dumps(results,indent=2))
