"""Preserve Unix permissions and macOS symlinks when packaging on Windows."""
import io
import json
import pathlib
import plistlib
import stat
import tarfile
import zipfile
from copy import copy

root = pathlib.Path(__file__).resolve().parent.parent
asar = (root / 'build-tools/app.asar').read_bytes()
version = json.loads((root / 'source/package.json').read_text(encoding='utf-8'))['version']
name = 'Gazyava-i-Hrumki'
for platform, arches in [('linux', ['x64','arm64','armv7l']), ('darwin', ['x64','arm64'])]:
    for arch in arches:
        source = root / f'build-tools/electron-zips/electron-v33.4.11-{platform}-{arch}.zip'
        folder = root / ('Linux' if platform == 'linux' else 'macOS')
        folder.mkdir(exist_ok=True)
        target = folder / f'{name}-{platform}-{arch}.zip'
        with zipfile.ZipFile(source) as src, zipfile.ZipFile(target, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as dst:
            for item in src.infolist():
                if item.filename.endswith('default_app.asar'): continue
                updated = copy(item)
                if platform == 'darwin':
                    updated.filename = item.filename.replace('Electron.app/', f'{name}.app/', 1)
                elif item.filename == 'electron': updated.filename = name
                data = src.read(item)
                if item.filename == 'Electron.app/Contents/Info.plist':
                    info = plistlib.loads(data)
                    info.update(CFBundleName=name, CFBundleDisplayName='Газява и Хрумки', CFBundleIdentifier='com.kabil.gazyava', CFBundleShortVersionString=version, CFBundleVersion=version)
                    data = plistlib.dumps(info)
                dst.writestr(updated, data)
            resource = f'{name}.app/Contents/Resources/app.asar' if platform == 'darwin' else 'resources/app.asar'
            entry = zipfile.ZipInfo(resource)
            entry.create_system = 3
            entry.external_attr = (stat.S_IFREG | 0o644) << 16
            dst.writestr(entry, asar, compress_type=zipfile.ZIP_DEFLATED)
        if platform == 'linux':
            tarpath = folder / f'{name}-{platform}-{arch}.tar.gz'
            with zipfile.ZipFile(target) as src, tarfile.open(tarpath, 'w:gz') as dst:
                for item in src.infolist():
                    info = tarfile.TarInfo(f'{name}-{arch}/' + item.filename)
                    mode = item.external_attr >> 16
                    info.mode = stat.S_IMODE(mode) or 0o644
                    if item.is_dir(): info.type = tarfile.DIRTYPE; info.mode = 0o755
                    elif stat.S_ISLNK(mode): info.type = tarfile.SYMTYPE; info.linkname = src.read(item).decode()
                    else:
                        data = src.read(item)
                        info.size = len(data)
                        dst.addfile(info, io.BytesIO(data))
                        continue
                    dst.addfile(info)
            # tar.gz is the portable Linux artifact with executable permissions.
            target.unlink()
            target = tarpath
        print(f'Packaged {target}', flush=True)
