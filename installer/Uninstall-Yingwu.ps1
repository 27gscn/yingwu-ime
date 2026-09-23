[CmdletBinding()]
param(
    [string]$TargetRoot = "$env:ProgramFiles\Yingwu",
    [switch]$PurgeUserData
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

function Test-Administrator {
    $identity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($identity)
    return $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
}

if (-not (Test-Administrator)) {
    $arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`" -TargetRoot `"$TargetRoot`""
    if ($PurgeUserData) { $arguments += ' -PurgeUserData' }
    $process = Start-Process -FilePath "$PSHOME\powershell.exe" -Verb RunAs `
        -ArgumentList $arguments -Wait -PassThru
    exit $process.ExitCode
}

function Unregister-Dll {
    param([string]$Exe, [string]$Dll)
    if (-not (Test-Path $Exe) -or -not (Test-Path $Dll)) { return }
    $arguments = "/u /s `"$Dll`""
    $process = Start-Process -FilePath $Exe -ArgumentList $arguments `
        -Wait -PassThru
    if ($process.ExitCode -ne 0) {
        Write-Warning "Could not unregister $Dll (exit $($process.ExitCode))."
    }
}

$reg64 = Join-Path $env:WINDIR 'System32\regsvr32.exe'
$reg32 = Join-Path $env:WINDIR 'SysWOW64\regsvr32.exe'
Unregister-Dll $reg32 (Join-Path $TargetRoot 'x86\YingwuTSF.dll')
Unregister-Dll $reg64 (Join-Path $TargetRoot 'x64\YingwuTSF.dll')

if (Test-Path $TargetRoot) {
    try {
        Remove-Item $TargetRoot -Recurse -Force
    } catch {
        Write-Warning 'Some files are still in use. Sign out or restart Windows, then delete the Yingwu folder.'
    }
}
if ($PurgeUserData) {
    $userData = Join-Path $env:LOCALAPPDATA 'Yingwu'
    if (Test-Path $userData) { Remove-Item $userData -Recurse -Force }
}
Write-Host 'Yingwu IME was unregistered.' -ForegroundColor Green
