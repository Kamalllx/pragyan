# Pragyan AI — start everything locally.
#   API      http://127.0.0.1:8000   (FastAPI + agents)
#   Studio   http://localhost:3100   (Next.js)
param([switch]$NoBrowser)
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

function Test-Port($p) { [bool](Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue) }

# Ollama
try { Invoke-RestMethod http://127.0.0.1:11434/api/version -TimeoutSec 2 | Out-Null }
catch {
    Write-Host "Starting Ollama…" -ForegroundColor Cyan
    Start-Process ollama -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep 3
}

# Backend
if (-not (Test-Port 8000)) {
    Write-Host "Starting Pragyan API on :8000" -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\backend'; .\.venv\Scripts\python.exe -m uvicorn pragyan.main:app --host 127.0.0.1 --port 8000"
} else { Write-Host "API already running on :8000" }

# Web
if (-not (Test-Port 3100)) {
    Write-Host "Starting Pragyan Studio on :3100" -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$root\web'; npm run dev"
} else { Write-Host "Studio already running on :3100" }

# Warm the model so the first job doesn't pay the load time
Start-Job { try { Invoke-RestMethod http://127.0.0.1:11434/api/generate -Method Post -Body '{"model":"qwen3.5:9b","prompt":"hi","stream":false,"keep_alive":"30m","options":{"num_predict":1}}' -ContentType 'application/json' | Out-Null } catch {} } | Out-Null

if (-not $NoBrowser) {
    for ($i = 0; $i -lt 40 -and -not (Test-Port 3100); $i++) { Start-Sleep 1 }
    Start-Process "http://localhost:3100"
}
Write-Host "`nPragyan is up. Studio: http://localhost:3100  ·  API docs: http://127.0.0.1:8000/docs" -ForegroundColor Green
