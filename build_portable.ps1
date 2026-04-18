param(
    [switch]$Clean = $true,
    [switch]$SkipZip
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$frontendRoot = Join-Path $projectRoot "frontend"
$chromeExe = Join-Path $projectRoot "engines\\chrome\\chrome.exe"
$firefoxExe = Join-Path $projectRoot "engines\\firefox\\firefox.exe"
Set-Location $projectRoot

if ($Clean) {
    Remove-Item -Recurse -Force "$projectRoot\build" -ErrorAction SilentlyContinue
    Remove-Item -Recurse -Force "$projectRoot\dist\Open-Anti-Browser" -ErrorAction SilentlyContinue
    Remove-Item -Force "$projectRoot\dist\Open-Anti-Browser-portable.zip" -ErrorAction SilentlyContinue
}

if (-not (Test-Path $chromeExe) -or -not (Test-Path $firefoxExe)) {
    throw "缺少内核文件，请先按 README 准备 engines\\chrome 和 engines\\firefox 后再打包。"
}

if (-not (Test-Path $frontendRoot)) {
    throw "未找到前端目录：$frontendRoot"
}

npm run build --prefix $frontendRoot
if ($LASTEXITCODE -ne 0) {
    throw "前端构建失败，退出码：$LASTEXITCODE"
}

python -m PyInstaller "$projectRoot\Open-Anti-Browser.spec" --noconfirm
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller 打包失败，退出码：$LASTEXITCODE"
}

$distDir = Join-Path $projectRoot "dist\Open-Anti-Browser"
$zipPath = Join-Path $projectRoot "dist\Open-Anti-Browser-portable.zip"

if (-not $SkipZip) {
    if (Test-Path $zipPath) {
        Remove-Item -Force $zipPath
    }

    $zipSuccess = $false
    $lastZipError = $null
    for ($attempt = 1; $attempt -le 5 -and -not $zipSuccess; $attempt++) {
        try {
            Compress-Archive -Path "$distDir\*" -DestinationPath $zipPath -Force
            $zipSuccess = $true
        }
        catch {
            $lastZipError = $_
            Start-Sleep -Seconds ([Math]::Min($attempt * 2, 8))
        }
    }

    if (-not $zipSuccess) {
        throw "便携版压缩失败：$($lastZipError.Exception.Message)"
    }
}

Write-Host ""
Write-Host "打包完成："
Write-Host "EXE 目录: $distDir"
if (-not $SkipZip) {
    Write-Host "ZIP 文件: $zipPath"
}
