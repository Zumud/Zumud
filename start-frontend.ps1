$ErrorActionPreference = "Stop"

Write-Host "Reading local Supabase settings..." -ForegroundColor Cyan

$lines = cmd.exe /d /s /c "npx --yes supabase@latest status -o env 2>nul"

if ($LASTEXITCODE -ne 0) {
    throw "Failed to read the local Supabase configuration."
}

$settings = @{}

foreach ($line in $lines) {
    if ($line -match '^([A-Z0-9_]+)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2].Trim().Trim('"')
        $settings[$name] = $value
    }
}

if ([string]::IsNullOrWhiteSpace($settings["API_URL"])) {
    throw "Could not read Supabase API_URL."
}

if ([string]::IsNullOrWhiteSpace($settings["PUBLISHABLE_KEY"])) {
    throw "Could not read Supabase PUBLISHABLE_KEY."
}

$supabaseUrl = $settings["API_URL"]
$publishableKey = $settings["PUBLISHABLE_KEY"]

$backendUrl = "http://127.0.0.1:8000"
$frontendUrl = "http://localhost:3000"

$frontendEnv = @"
# Local Windows development settings
NEXT_PUBLIC_SUPABASE_URL=$frontendUrl
SUPABASE_LOCAL_PROXY_TARGET=$supabaseUrl
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=$publishableKey
NEXT_PUBLIC_API_URL=$backendUrl
API_URL=$backendUrl
"@

$envPath = Join-Path $PSScriptRoot "frontend\.env.local"

[System.IO.File]::WriteAllText(
    $envPath,
    $frontendEnv,
    [System.Text.Encoding]::ASCII
)

# These values must also be correct in the running Node process.
# Existing environment variables override .env.local.
$env:NEXT_PUBLIC_SUPABASE_URL = $frontendUrl
$env:SUPABASE_LOCAL_PROXY_TARGET = $supabaseUrl
$env:NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY = $publishableKey
$env:NEXT_PUBLIC_API_URL = $backendUrl
$env:API_URL = $backendUrl

$nextCache = Join-Path $PSScriptRoot "frontend\.next"

if (Test-Path $nextCache) {
    Write-Host "Clearing old Next.js cache..." -ForegroundColor DarkGray
    Remove-Item $nextCache -Recurse -Force
}

Write-Host ""
Write-Host "Supabase proxy: $supabaseUrl" -ForegroundColor DarkGray
Write-Host "Backend: $backendUrl" -ForegroundColor DarkGray
Write-Host "Starting Zumud: $frontendUrl" -ForegroundColor Green
Write-Host ""

Set-Location (Join-Path $PSScriptRoot "frontend")

$env:PORT = "3000"

npm run dev