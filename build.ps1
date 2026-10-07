# Builds dist\SpeedReport.exe (one portable file, no installer).
# Needs: Python 3.12, and the app source checked out in .\app (the CI does this; locally: git clone the source repo into app).
$ErrorActionPreference = 'Stop'
python -m pip install --upgrade pip
python -m pip install pillow python-docx rapidocr-onnxruntime flask pyinstaller
python scripts/make_config.py
python scripts/make_icon.py

python -m PyInstaller --noconfirm --clean --onefile --noconsole --name SpeedReport --icon app.ico `
  --paths app `
  --collect-all rapidocr_onnxruntime `
  --collect-binaries onnxruntime `
  --collect-data docx `
  --hidden-import speedreport.web.app `
  --add-data "app/speedreport/web/templates;speedreport/web/templates" `
  --add-data "app/speedreport/web/static;speedreport/web/static" `
  --add-data "config.public.json;." `
  launcher.py
if ($LASTEXITCODE) { throw "PyInstaller failed" }
Get-Item dist\SpeedReport.exe | Select-Object Name, @{n = 'MB'; e = { [math]::Round($_.Length / 1MB, 1) } }
