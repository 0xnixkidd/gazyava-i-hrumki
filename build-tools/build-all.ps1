$ErrorActionPreference = 'Stop'
Push-Location (Split-Path $PSScriptRoot -Parent)
try {
    function Run([scriptblock]$Action) { & $Action; if ($LASTEXITCODE -ne 0) { throw "Failed: $Action" } }
    Run { npm.cmd ci --prefix build-tools }
    Run { node build-tools/build-desktop.cjs }
    if (-not (Test-Path build-tools/electron-checksums.txt)) {
        Invoke-WebRequest 'https://github.com/electron/electron/releases/download/v33.4.11/SHASUMS256.txt' -OutFile build-tools/electron-checksums.txt
    }
    Run { python build-tools/download-electron.py }
    Run { python build-tools/package-windows.py }
    Run { python build-tools/package-unix.py }
    & build-tools/build-android.ps1
    New-Item -ItemType Directory -Force iOS | Out-Null
    Get-ChildItem Web -File | Where-Object Name -ne 'README.txt' | Copy-Item -Destination iOS -Force
    Run { python build-tools/verify-artifacts.py }
} finally { Pop-Location }
