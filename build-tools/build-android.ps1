$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path $PSScriptRoot -Parent
if (-not $env:JAVA_HOME) { throw 'Set JAVA_HOME to a JDK 17 or newer.' }
$sdk = Join-Path $PSScriptRoot 'android-sdk'
$bt = Join-Path $sdk 'build-tools/35.0.0'
$androidJar = Join-Path $sdk 'platforms/android-35/android.jar'
$project = Join-Path $PSScriptRoot 'android-project'
$output = Join-Path $taskRoot 'Android'
$intermediate = Join-Path $PSScriptRoot 'android-intermediate'
New-Item -ItemType Directory -Force $output,$intermediate,"$intermediate/classes","$intermediate/dex" | Out-Null
function Checked([scriptblock]$Action) { & $Action; if ($LASTEXITCODE -ne 0) { throw "Command failed: $Action" } }
if (-not (Test-Path "$taskRoot/Web/index.html")) { throw 'Run build-desktop.cjs to prepare Web assets first.' }
New-Item -ItemType Directory -Force "$project/res/drawable" | Out-Null
Copy-Item "$taskRoot/source/icon-192.png" "$project/res/drawable/icon.png" -Force
Checked { & "$bt/aapt.exe" package -f -M "$project/AndroidManifest.xml" -I $androidJar -S "$project/res" -A "$taskRoot/Web" -F "$intermediate/unsigned.apk" }
Checked { & "$env:JAVA_HOME/bin/javac.exe" --release 8 -encoding UTF-8 -classpath $androidJar -d "$intermediate/classes" "$project/src/com/kabil/gazyava/MainActivity.java" }
$classFiles = @(Get-ChildItem "$intermediate/classes" -Filter '*.class' -Recurse | ForEach-Object FullName)
Checked { & "$bt/d8.bat" --lib $androidJar --min-api 23 --output "$intermediate/dex" @classFiles }
Copy-Item "$intermediate/dex/classes.dex" "$intermediate/classes.dex" -Force
Push-Location $intermediate
try { Checked { & "$bt/aapt.exe" add unsigned.apk classes.dex } } finally { Pop-Location }
Checked { & "$bt/zipalign.exe" -f -p 4 "$intermediate/unsigned.apk" "$intermediate/aligned.apk" }
$key = Join-Path $PSScriptRoot 'local-test.keystore'
if (-not (Test-Path $key)) {
    Checked { & "$env:JAVA_HOME/bin/keytool.exe" -genkeypair -keystore $key -storepass android -keypass android -alias local-test -keyalg RSA -keysize 2048 -validity 10000 -dname 'CN=Gazyava Local Test' }
}
Checked { & "$bt/apksigner.bat" sign --ks $key --ks-key-alias local-test --ks-pass pass:android --key-pass pass:android --out "$output/Gazyava-i-Hrumki.apk" "$intermediate/aligned.apk" }
Checked { & "$bt/apksigner.bat" verify --verbose "$output/Gazyava-i-Hrumki.apk" }
Checked { & "$bt/aapt.exe" dump badging "$output/Gazyava-i-Hrumki.apk" }
