#Requires -Version 5.1
$ErrorActionPreference = "Stop"

# Activate virtual environment
$venvActivate = ".\venv\Scripts\Activate.ps1"
if (-not (Test-Path $venvActivate)) {
    Write-Error "Virtual environment not found. Run setup first:`n  python -m venv venv`n  venv\Scripts\Activate.ps1`n  pip install -r requirements.txt"
    exit 1
}
& $venvActivate

# Clean previous build output
foreach ($dir in @("build", "dist")) {
    if (Test-Path $dir) {
        Remove-Item -Recurse -Force $dir
        Write-Host "Removed: $dir"
    }
}

# Build executable
pyinstaller `
    --windowed `
    --icon="application-icon.ico" `
    --name="Vocabulary Extractor" `
    --add-data="data/simplified;data/simplified" `
    --add-data="data/traditional;data/traditional" `
    --add-data="data/*.u8;data" `
    --add-data="dict;dict" `
    --add-data="filter;filter" `
    --add-data="samples/CN;samples/CN" `
    --add-data="samples/VN;samples/VN" `
    --add-data="application-icon.ico;." `
    main.py

if ($LASTEXITCODE -ne 0) {
    Write-Error "PyInstaller failed (exit code $LASTEXITCODE)"
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Build complete. Output is in 'dist\Vocabulary Extractor'."
Write-Host "To distribute, zip that folder."
