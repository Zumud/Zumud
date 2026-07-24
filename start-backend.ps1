$ErrorActionPreference = "Stop"

Write-Host "Reading Supabase local settings..." -ForegroundColor Cyan

$lines = npx --yes supabase@latest status -o env

foreach ($line in $lines) {
    if ($line -match '^([A-Z0-9_]+)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2].Trim().Trim('"')

        Set-Item -Path "Env:$name" -Value $value
    }
}

if ([string]::IsNullOrWhiteSpace($env:DB_URL)) {
    throw "Could not read DB_URL. Supabase may not be running."
}

$env:SUPABASE_URL = $env:API_URL
$env:SUPABASE_PUBLISHABLE_KEY = $env:PUBLISHABLE_KEY
$env:SUPABASE_SECRET_KEY = $env:SECRET_KEY
$env:SUPABASE_JWT_SECRET = $env:JWT_SECRET
$env:DATABASE_URL = $env:DB_URL

$env:LATEX_COMPILER_BASE_URL = "http://127.0.0.1:2700"
$env:CORS_ALLOWED_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"
$env:ENVIRONMENT = "development"

Write-Host ""
Write-Host "Database: $env:DATABASE_URL" -ForegroundColor DarkGray
Write-Host "Starting Backend: http://127.0.0.1:8000" -ForegroundColor Green
Write-Host "Swagger: http://127.0.0.1:8000/docs" -ForegroundColor Green
Write-Host ""

& ".\.venv\Scripts\python.exe" -m uvicorn backend.main:app `
    --reload `
    --host 127.0.0.1 `
    --port 8000