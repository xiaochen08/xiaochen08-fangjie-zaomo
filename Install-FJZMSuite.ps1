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

$skillNames = @('fjzm', 'fjzm-animation')
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

$existing = @($skillNames | Where-Object { Test-Path -LiteralPath $targetPaths[$_] })
if ($existing.Count -eq 1) {
    throw "Refusing partial suite installation. Found only '$($existing[0])'. Repair or back it up before installing both skills together."
}
if ($existing.Count -eq 2 -and -not $BackupAndReplace) {
    throw "Both skills already exist. Re-run with -BackupAndReplace to create a dated backup and update both together."
}

if (-not (Test-Path -LiteralPath $destination -PathType Container)) {
    New-Item -ItemType Directory -Path $destination | Out-Null
}

$stage = Join-Path $destination ('.fjzm-suite-stage-' + [Guid]::NewGuid().ToString('N'))
$backup = $null
New-Item -ItemType Directory -Path $stage | Out-Null

try {
    foreach ($name in $skillNames) {
        $stagedSkill = Join-Path $stage $name
        Copy-Item -LiteralPath $sourcePaths[$name] -Destination $stagedSkill -Recurse
        $skillFile = Join-Path $stagedSkill 'SKILL.md'
        $skillText = Get-Content -LiteralPath $skillFile -Raw -Encoding UTF8
        if ($skillText -notmatch "(?m)^name:\s+$([regex]::Escape($name))\s*$") {
            throw "Staged skill identity check failed: $name"
        }
    }

    if ($existing.Count -eq 2) {
        $backup = Join-Path $destination ('.fjzm-suite-backup-' + (Get-Date -Format 'yyyyMMdd-HHmmss'))
        New-Item -ItemType Directory -Path $backup | Out-Null
        foreach ($name in $skillNames) {
            Move-Item -LiteralPath $targetPaths[$name] -Destination (Join-Path $backup $name)
        }
    }

    foreach ($name in $skillNames) {
        Move-Item -LiteralPath (Join-Path $stage $name) -Destination $targetPaths[$name]
    }

    $stageChildren = @(Get-ChildItem -LiteralPath $stage -Force)
    if ($stageChildren.Count -ne 0) {
        throw "Installation stage is not empty after activation: $stage"
    }
    Remove-Item -LiteralPath $stage

    Write-Host "Installed FJZM suite 3.0.0:"
    foreach ($name in $skillNames) {
        Write-Host "  $($targetPaths[$name])"
    }
    if ($backup) {
        Write-Host "Previous suite backup: $backup"
    }
    Write-Host 'Restart Codex or start a new task before invoking $fjzm or $fjzm-animation.'
}
catch {
    foreach ($name in $skillNames) {
        $newTarget = $targetPaths[$name]
        if (Test-Path -LiteralPath $newTarget -PathType Container) {
            Move-Item -LiteralPath $newTarget -Destination (Join-Path $stage $name)
        }
    }
    if ($backup -and (Test-Path -LiteralPath $backup -PathType Container)) {
        foreach ($name in $skillNames) {
            $backupSkill = Join-Path $backup $name
            if (Test-Path -LiteralPath $backupSkill -PathType Container) {
                Move-Item -LiteralPath $backupSkill -Destination $targetPaths[$name]
            }
        }
    }
    throw
}
