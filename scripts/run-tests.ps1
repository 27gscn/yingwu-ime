$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot
python -m unittest discover -s (Join-Path $Root 'tests') -v
if ($LASTEXITCODE -ne 0) { throw '应物输入法数据测试失败。' }
