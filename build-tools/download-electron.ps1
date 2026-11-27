$ErrorActionPreference = 'Stop'
$zipRoot = Join-Path $PSScriptRoot 'electron-zips'
New-Item -ItemType Directory -Force $zipRoot | Out-Null
$checksums = Get-Content (Join-Path $PSScriptRoot 'electron-checksums.txt')
$files = @('win32-x64','win32-ia32','win32-arm64','linux-x64','linux-arm64','linux-armv7l','darwin-x64','darwin-arm64')
$files | ForEach-Object -Parallel {
    $name = "electron-v33.4.11-$_.zip"
    $dest = Join-Path $using:zipRoot $name
    if (-not (Test-Path $dest)) {
        Invoke-WebRequest "https://github.com/electron/electron/releases/download/v33.4.11/$name" -OutFile "$dest.download" -TimeoutSec 600
        Move-Item -LiteralPath "$dest.download" -Destination $dest -Force
    }
    $line = $using:checksums | Where-Object { $_.EndsWith(" *$name") -or $_.EndsWith("  $name") }
    if (-not $line) { throw "Missing checksum for $name" }
    if ((Get-FileHash -LiteralPath $dest -Algorithm SHA256).Hash -ne $line.Split(' ')[0]) { throw "Checksum mismatch: $name" }
    Write-Output "Verified $name"
} -ThrottleLimit 3
