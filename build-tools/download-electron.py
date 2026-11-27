"""Download official Electron archives in resumable, verified chunks."""
import concurrent.futures
import hashlib
import pathlib
import re
import subprocess

root = pathlib.Path(__file__).resolve().parent
output = root / 'electron-zips'
output.mkdir(exist_ok=True)
checksums = dict((line.split()[1].lstrip('*'), line.split()[0]) for line in (root / 'electron-checksums.txt').read_text().splitlines())
targets = ['win32-x64','win32-ia32','win32-arm64','linux-x64','linux-arm64','linux-armv7l','darwin-x64','darwin-arm64']
jobs = []
archives = []
chunk_size = 4 * 1024 * 1024
for target in targets:
    name = f'electron-v33.4.11-{target}.zip'
    url = f'https://github.com/electron/electron/releases/download/v33.4.11/{name}'
    dest = output / name
    if dest.exists() and hashlib.file_digest(dest.open('rb'), 'sha256').hexdigest() == checksums[name]:
        print(f'Already verified {name}', flush=True)
        continue
    headers = subprocess.check_output(['curl.exe','-sS','-I','-L','--max-time','30',url], text=True)
    size = int(re.findall(r'(?im)^content-length:\s*(\d+)', headers)[-1])
    parts = output / (name + '.parts')
    parts.mkdir(exist_ok=True)
    archives.append((dest, size, parts))
    for start in range(0, size, chunk_size):
        end = min(start + chunk_size, size) - 1
        jobs.append((url, start, end, parts / str(start)))

def download(job):
    url, start, end, part = job
    if not part.exists() or part.stat().st_size != end-start+1:
        subprocess.run(['curl.exe','-f','-sS','-L','--connect-timeout','15','--max-time','120','--retry','3','--range',f'{start}-{end}','-o',str(part),url], check=True)
    if part.stat().st_size != end-start+1:
        raise RuntimeError(f'Wrong chunk size: {part}')

with concurrent.futures.ThreadPoolExecutor(max_workers=16) as pool:
    for count, _ in enumerate(pool.map(download, jobs), 1):
        if count % 16 == 0 or count == len(jobs): print(f'Chunks {count}/{len(jobs)}', flush=True)
for dest, size, parts in archives:
    with dest.open('wb') as stream:
        for start in range(0, size, chunk_size): stream.write((parts / str(start)).read_bytes())
    with dest.open('rb') as stream: actual = hashlib.file_digest(stream, 'sha256').hexdigest()
    if actual != checksums[dest.name]: raise RuntimeError(f'Checksum mismatch: {dest}')
    print(f'Verified {dest.name}', flush=True)
