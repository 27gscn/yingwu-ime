[CmdletBinding()]
param([string]$Version = '0.57-heng')

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$Root = Split-Path -Parent $PSScriptRoot
$Sources = Join-Path $Root 'data-tools\sources'
$Generated = Join-Path $Root 'build\generated-data'
$Data = Join-Path $Root 'data'
New-Item -ItemType Directory -Path $Generated -Force | Out-Null

python (Join-Path $Root 'data-tools\generate_hengma.py') `
    --hanzi-data (Join-Path $Sources 'hanzi-dictionary.txt') `
    --cjkvi-ids (Join-Path $Sources 'cjkvi-ids.txt') `
    --rime-8105 (Join-Path $Sources '8105.dict.yaml') `
    --out-dir $Generated --version $Version
if ($LASTEXITCODE -ne 0) { throw 'Single-character dictionary build failed.' }

python (Join-Path $Root 'data-tools\generate_phrases.py') `
    --base-dict (Join-Path $Sources 'base.dict.yaml') `
    --char-metadata (Join-Path $Generated 'hengma_codes.jsonl') `
    --out (Join-Path $Generated 'hengma_phrases.dict.yaml') `
    --effective-out (Join-Path $Generated 'phrase_effective_codes.tsv') `
    --version $Version --max-length 12 --max-levels 2
if ($LASTEXITCODE -ne 0) { throw 'Phrase dictionary build failed.' }

python (Join-Path $Root 'data-tools\simulate_phrase_error.py') `
    --effective-tsv (Join-Path $Generated 'phrase_effective_codes.tsv') `
    --out (Join-Path $Root 'build-reports\current_phrase_simulation.json')
if ($LASTEXITCODE -ne 0) { throw 'Phrase collision simulation failed.' }

Copy-Item (Join-Path $Generated 'hengma.dict.yaml') $Data -Force
Copy-Item (Join-Path $Generated 'hengma_fuzzy.dict.yaml') $Data -Force
Copy-Item (Join-Path $Generated 'hengma_phrases.dict.yaml') $Data -Force
# The candidate-annotation table is derived from the finished character
# dictionary, so it is generated after the copy above.
python (Join-Path $Root 'data-tools\generate_codes.py') `
    --source (Join-Path $Data 'hengma.dict.yaml') `
    --output (Join-Path $Data 'hengma_char_codes.dict.yaml') `
    --version $Version
if ($LASTEXITCODE -ne 0) { throw 'Annotation table build failed.' }

Write-Host "Runtime dictionaries rebuilt in $Data"
