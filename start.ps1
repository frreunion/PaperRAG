param(
    [switch]$Stop,
    [switch]$SetupOnly,
    [switch]$NoInstall
)

& "$PSScriptRoot\scripts\dev.ps1" @PSBoundParameters
