param(
    [string]$EnvFile = ".env"
)

if (-not (Test-Path $EnvFile)) {
    Write-Error "Environment file not found: $EnvFile"
    exit 1
}

Get-Content $EnvFile | Where-Object {
    $_ -match '^\s*[^#][^=]*='
} | ForEach-Object {
    $name, $value = $_.Split("=", 2)
    $cleanName = $name.Trim()
    $cleanValue = $value.Trim().Trim('"').Trim("'")
    Set-Item -Path "Env:$cleanName" -Value $cleanValue
}

Write-Host "Environment variables loaded from $EnvFile."
