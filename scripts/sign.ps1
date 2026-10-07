# Signs dist\SpeedReport.exe with the certificate from the secrets SIGN_PFX_BASE64 / SIGN_PFX_PASSWORD.
# The certificate can be the Akakus company certificate (self-signed, see certs/) or a purchased one
# (DigiCert, Sectigo, SSL.com ...): just replace the two secrets, nothing else changes.
$ErrorActionPreference = 'Stop'
if (-not $env:SIGN_PFX_BASE64) { Write-Warning "No signing certificate configured: the exe is NOT signed."; exit 0 }
$pfx = Join-Path $env:RUNNER_TEMP 'sign.pfx'
[IO.File]::WriteAllBytes($pfx, [Convert]::FromBase64String($env:SIGN_PFX_BASE64))
$signtool = Get-ChildItem "${env:ProgramFiles(x86)}\Windows Kits\10\bin\*\x64\signtool.exe" | Sort-Object FullName | Select-Object -Last 1
if (-not $signtool) { throw "signtool.exe not found on this runner" }
try {
  & $signtool.FullName sign /fd SHA256 /f $pfx /p $env:SIGN_PFX_PASSWORD /tr http://timestamp.digicert.com /td SHA256 /d "Akakus Speed Report" dist\SpeedReport.exe
  if ($LASTEXITCODE) { throw "signtool failed ($LASTEXITCODE)" }
} finally { Remove-Item $pfx -Force -ErrorAction SilentlyContinue }
$sig = Get-AuthenticodeSignature dist\SpeedReport.exe
"Signed by: $($sig.SignerCertificate.Subject)"
"Status: $($sig.Status) (NotTrusted is expected for the self-signed company certificate on a PC that has not imported certs\AkakusSpeedReport.cer)"
if (-not $sig.SignerCertificate) { throw "no signature found after signing" }
