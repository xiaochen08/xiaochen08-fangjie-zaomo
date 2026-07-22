[CmdletBinding()]
param(
    [Parameter()]
    [string]$DestinationRoot = (Join-Path ([Environment]::GetFolderPath('UserProfile')) '.codex\skills'),

    [Parameter()]
    [switch]$BackupAndReplace
)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$suiteRoot = [System.IO.Path]::GetFullPath($PSScriptRoot)
$sourceRoot = [System.IO.Path]::GetFullPath((Join-Path $suiteRoot 'skills'))
$destination = [System.IO.Path]::GetFullPath($DestinationRoot)
$destinationDriveRoot = [System.IO.Path]::GetPathRoot($destination).TrimEnd('\')
if ($destination.TrimEnd('\') -eq $destinationDriveRoot) {
    throw "DestinationRoot cannot be a drive root: $destination"
}

$skillNames = @('fjzm', 'fjzm-model', 'fjzm-texture', 'fjzm-animation')
$sourcePaths = @{}
$targetPaths = @{}
foreach ($name in $skillNames) {
    $sourcePaths[$name] = [System.IO.Path]::GetFullPath((Join-Path $sourceRoot $name))
    $targetPaths[$name] = [System.IO.Path]::GetFullPath((Join-Path $destination $name))
    if (-not $sourcePaths[$name].StartsWith($sourceRoot + '\', [System.StringComparison]::OrdinalIgnoreCase)) {
        throw "Invalid suite source path: $($sourcePaths[$name])"
    }
    if (-not (Test-Path -LiteralPath (Join-Path $sourcePaths[$name] 'SKILL.md') -PathType Leaf)) {
        throw "Suite source is incomplete: $name/SKILL.md"
    }
}

$existing = @($skillNames | Where-Object { Test-Path -LiteralPath $targetPaths[$_] -PathType Container })
$legacyV3 = $existing.Count -eq 2 -and $existing -contains 'fjzm' -and $existing -contains 'fjzm-animation'
$legacyV4 = $existing.Count -eq 3 -and $existing -contains 'fjzm' -and $existing -contains 'fjzm-texture' -and $existing -contains 'fjzm-animation'
$completeV5 = $existing.Count -eq 4

if ($existing.Count -ne 0 -and -not ($legacyV3 -or $legacyV4 -or $completeV5)) {
    throw "Refusing partial suite installation. Found: $($existing -join ', '). Expected none, a recognized v3/v4 installation, or all four v5 skills."
}
if ($existing.Count -gt 0 -and -not $BackupAndReplace) {
    throw 'Existing FJZM installation detected. Re-run with -BackupAndReplace to back it up and install all four v5 skills together.'
}
if (-not (Test-Path -LiteralPath $destination -PathType Container)) {
    New-Item -ItemType Directory -Path $destination | Out-Null
}

$stage = Join-Path $destination ('.fjzm-suite-stage-' + [Guid]::NewGuid().ToString('N'))
$backup = $null
$activated = @()
New-Item -ItemType Directory -Path $stage | Out-Null

try {
    foreach ($name in $skillNames) {
        $stagedSkill = Join-Path $stage $name
        Copy-Item -LiteralPath $sourcePaths[$name] -Destination $stagedSkill -Recurse
        $skillText = Get-Content -LiteralPath (Join-Path $stagedSkill 'SKILL.md') -Raw -Encoding UTF8
        if ($skillText -notmatch "(?m)^name:\s+$([regex]::Escape($name))\s*$") {
            throw "Staged skill identity check failed: $name"
        }
    }

    if ($existing.Count -gt 0) {
        $backup = Join-Path $destination ('.fjzm-suite-backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
        New-Item -ItemType Directory -Path $backup | Out-Null
        foreach ($name in $existing) {
            Move-Item -LiteralPath $targetPaths[$name] -Destination (Join-Path $backup $name)
        }
    }

    foreach ($name in $skillNames) {
        Move-Item -LiteralPath (Join-Path $stage $name) -Destination $targetPaths[$name]
        $activated += $name
    }

    if (@(Get-ChildItem -LiteralPath $stage -Force).Count -ne 0) {
        throw "Installation stage is not empty after activation: $stage"
    }
    Remove-Item -LiteralPath $stage

    Write-Host 'Installed FJZM suite 5.2.0:'
    foreach ($name in $skillNames) {
        Write-Host "  $($targetPaths[$name])"
    }
    if ($backup) {
        Write-Host "Previous suite backup: $backup"
    }
    Write-Host 'Restart Codex or start a new task before invoking $fjzm and its three specialist skills.'
}
catch {
    foreach ($name in $activated) {
        if (Test-Path -LiteralPath $targetPaths[$name] -PathType Container) {
            Move-Item -LiteralPath $targetPaths[$name] -Destination (Join-Path $stage ($name + '.failed-new'))
        }
    }
    if ($backup -and (Test-Path -LiteralPath $backup -PathType Container)) {
        foreach ($name in $existing) {
            $backupSkill = Join-Path $backup $name
            if ((Test-Path -LiteralPath $backupSkill -PathType Container) -and -not (Test-Path -LiteralPath $targetPaths[$name])) {
                Move-Item -LiteralPath $backupSkill -Destination $targetPaths[$name]
            }
        }
    }
    throw
}
