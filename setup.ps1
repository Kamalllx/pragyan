# Pragyan AI — one-time setup (Windows, PowerShell).
#   Requires: Python 3.12, Node 20+, ffmpeg, Ollama, a LaTeX distribution (MiKTeX) for Manim maths.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

Write-Host "`n== Pragyan AI setup ==" -ForegroundColor Yellow

foreach ($tool in "python", "node", "npm", "ffmpeg", "ollama") {
    if (-not (Get-Command $tool -ErrorAction SilentlyContinue)) { throw "$tool is not on PATH — install it first." }
}

# --- Python backend -------------------------------------------------------
Write-Host "`n[1/5] Python environment" -ForegroundColor Cyan
if (Get-Command uv -ErrorAction SilentlyContinue) {
    uv venv --python 3.12 backend/.venv
    uv pip install --python backend/.venv/Scripts/python.exe -r backend/requirements.txt
} else {
    python -m venv backend/.venv
    backend/.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
}

# --- Narration voice --------------------------------------------------------
Write-Host "`n[2/5] Kokoro voice model (~350 MB, one time)" -ForegroundColor Cyan
New-Item -ItemType Directory -Force models/kokoro | Out-Null
$base = "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0"
if (-not (Test-Path models/kokoro/kokoro-v1.0.onnx)) { Invoke-WebRequest "$base/kokoro-v1.0.onnx" -OutFile models/kokoro/kokoro-v1.0.onnx }
if (-not (Test-Path models/kokoro/voices-v1.0.bin)) { Invoke-WebRequest "$base/voices-v1.0.bin" -OutFile models/kokoro/voices-v1.0.bin }

# --- Node packages ------------------------------------------------------------
Write-Host "`n[3/5] Motion engine (Remotion) + web app" -ForegroundColor Cyan
Push-Location motion; npm install; Pop-Location
Push-Location web; npm install; Pop-Location

# --- Models -------------------------------------------------------------------
Write-Host "`n[4/5] Ollama models" -ForegroundColor Cyan
$have = (ollama list) -join "`n"
foreach ($m in "qwen3.5:9b", "nomic-embed-text") {
    if ($have -notmatch [regex]::Escape($m)) { ollama pull $m }
}

# --- LaTeX ------------------------------------------------------------------------
Write-Host "`n[5/5] LaTeX auto-install (so Manim never blocks on a package prompt)" -ForegroundColor Cyan
if (Get-Command initexmf -ErrorAction SilentlyContinue) { initexmf --set-config-value="[MPM]AutoInstall=1" | Out-Null }

if (-not (Test-Path .env)) { Copy-Item .env.example .env; Write-Host "Created .env — add your MONGODB_URI (optional; a local JSON store is used otherwise)." }
Write-Host "`nDone. Start Pragyan with:  .\start.ps1`n" -ForegroundColor Green
