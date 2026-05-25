$RepoRoot = Resolve-Path "$PSScriptRoot\.."
$VenvActivate = Join-Path $RepoRoot ".venv\Scripts\Activate.ps1"

Set-Location $RepoRoot

if (Test-Path $VenvActivate) {
    . $VenvActivate
}

. .\scripts\load-env.ps1

Set-Location .\data\dbt
$output = dbt debug --profiles-dir . 2>&1
$exitCode = $LASTEXITCODE
$output | ForEach-Object {
    $_ `
        -replace '(\s+account:\s+).*', '$1[redacted]' `
        -replace '(\s+user:\s+).*', '$1[redacted]' `
        -replace 'post\s+[^:\s]+\.snowflakecomputing\.com', 'post [redacted].snowflakecomputing.com' `
        -replace 'DB:\s+[^:\s]+\.snowflakecomputing\.com', 'DB: [redacted].snowflakecomputing.com'
}
Set-Location $RepoRoot
exit $exitCode
