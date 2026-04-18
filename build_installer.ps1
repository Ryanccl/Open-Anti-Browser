param(
    [switch]$Clean = $true
)

$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$toolsRoot = Join-Path $projectRoot "tools"
$innoRoot = Join-Path $toolsRoot "inno-setup"
$innoInstaller = Join-Path $toolsRoot "innosetup-6.7.1.exe"
$isccPath = Join-Path $innoRoot "ISCC.exe"
$installerUrl = "https://github.com/jrsoftware/issrc/releases/download/is-6_7_1/innosetup-6.7.1.exe"

Set-Location $projectRoot

if ($Clean) {
    Remove-Item -Recurse -Force "$projectRoot\dist\installer" -ErrorAction SilentlyContinue
}

if ($Clean) {
    powershell -ExecutionPolicy Bypass -File "$projectRoot\build_portable.ps1" -Clean -SkipZip
}
else {
    powershell -ExecutionPolicy Bypass -File "$projectRoot\build_portable.ps1" -SkipZip
}
if ($LASTEXITCODE -ne 0) {
    throw "便携版打包失败，退出码：$LASTEXITCODE"
}

New-Item -ItemType Directory -Force -Path $toolsRoot | Out-Null

if (-not (Test-Path $isccPath)) {
    Write-Host "未检测到 Inno Setup，开始下载并安装到本地工具目录..."
    curl.exe -L $installerUrl -o $innoInstaller
    if ($LASTEXITCODE -ne 0 -or -not (Test-Path $innoInstaller)) {
        throw "Inno Setup 下载失败。"
    }

    $installArgs = @(
        "/SP-",
        "/VERYSILENT",
        "/SUPPRESSMSGBOXES",
        "/NORESTART",
        "/DIR=$innoRoot"
    )
    $proc = Start-Process -FilePath $innoInstaller -ArgumentList $installArgs -Wait -PassThru
    if ($proc.ExitCode -ne 0) {
        throw "Inno Setup 安装失败，退出码：$($proc.ExitCode)"
    }
}

if (-not (Test-Path $isccPath)) {
    throw "未找到 ISCC.exe：$isccPath"
}

& $isccPath "$projectRoot\installer\Open-Anti-Browser.iss"
if ($LASTEXITCODE -ne 0) {
    throw "安装包编译失败，退出码：$LASTEXITCODE"
}

$setupExe = Join-Path $projectRoot "dist\installer\Open-Anti-Browser-Setup.exe"
if (-not (Test-Path $setupExe)) {
    throw "安装包没有生成成功：$setupExe"
}

Write-Host ""
Write-Host "安装包完成："
Write-Host "Setup 文件: $setupExe"
