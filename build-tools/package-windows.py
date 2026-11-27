import hashlib
import pathlib
import sys
import zipfile

root = pathlib.Path(__file__).resolve().parent.parent
checksums = dict((line.split()[1].lstrip('*'), line.split()[0]) for line in (root / 'build-tools/electron-checksums.txt').read_text().splitlines())
for arch in sys.argv[1:] or ['x64', 'ia32', 'arm64']:
    source = root / f'build-tools/electron-zips/electron-v33.4.11-win32-{arch}.zip'
    with source.open('rb') as f:
        if hashlib.file_digest(f, 'sha256').hexdigest() != checksums[source.name]: raise RuntimeError('Bad Electron checksum')
    dest = root / 'Windows' / arch
    dest.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as archive: archive.extractall(dest)
    original = dest / 'electron.exe'
    original.replace(dest / 'Gazyava-i-Hrumki.exe')
    (dest / 'resources/default_app.asar').unlink(missing_ok=True)
    (dest / 'resources/app.asar').write_bytes((root / 'build-tools/app.asar').read_bytes())
    print(f'Packaged Windows {arch}: {dest}', flush=True)
